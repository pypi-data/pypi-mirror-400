"""
Fourier KPSS Stationarity Test
Based on: Becker, R., Enders, W., and Lee, J. (2006)
"A stationarity test in the presence of an unknown number of smooth breaks"
Journal of Time Series Analysis, 27(3), 381-409.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/funitroot
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple, Optional, Union, Dict, NamedTuple
import warnings


class FTestResult(NamedTuple):
    """Result container for F-test for linearity."""
    f_statistic: float
    critical_values: Dict[str, float]
    pvalue: float
    reject_null: bool
    frequency: int


class FourierKPSS:
    """
    Fourier KPSS stationarity test with flexible Fourier form.
    
    This test allows for smooth structural breaks of unknown number and form
    using Fourier approximations. Unlike standard KPSS, null hypothesis is
    stationarity around Fourier components.
    
    Parameters
    ----------
    data : array-like
        Time series data to test
    model : str, default='c'
        Deterministic terms: 'c' for level stationarity, 'ct' for trend stationarity
    max_freq : int, default=5
        Maximum frequency to search (must be between 1 and 5)
    lags : str or int, default='auto'
        Number of lags for Newey-West HAC estimator. 
        If 'auto', uses int(4*(T/100)^(2/9))
        
    Attributes
    ----------
    statistic : float
        The test statistic value
    pvalue : float
        The approximate p-value
    optimal_frequency : int
        The selected optimal frequency (minimizes SSR)
    critical_values : dict
        Critical values at 1%, 5%, and 10% levels
    reject_null : bool
        Whether to reject the null hypothesis of stationarity
    tau_statistic : float
        The Fourier KPSS τ statistic
        
    References
    ----------
    Becker, R., Enders, W., and Lee, J. (2006). "A stationarity test in the 
    presence of an unknown number of smooth breaks," Journal of Time Series 
    Analysis, 27(3), 381-409.
    """
    
    def __init__(
        self,
        data: Union[np.ndarray, pd.Series, list],
        model: str = 'c',
        max_freq: int = 5,
        lags: Union[str, int] = 'auto'
    ):
        # Convert data to numpy array
        if isinstance(data, (pd.Series, pd.DataFrame)):
            self.data = data.values.flatten()
        else:
            self.data = np.array(data).flatten()
            
        # Remove NaN values
        self.data = self.data[~np.isnan(self.data)]
        
        self.T = len(self.data)
        self.model = model.lower()
        
        # Validate max_freq - raise error instead of silent capping
        if max_freq < 1 or max_freq > 5:
            raise ValueError("max_freq must be between 1 and 5")
        self.max_freq = max_freq
        
        # Set number of lags for Newey-West estimator
        # Default: round(4 * (T/100)^(2/9)) as in GAUSS code
        if lags == 'auto':
            self.lags = int(round(4 * (self.T / 100) ** (2/9)))
        else:
            self.lags = int(lags)
            
        # Validate inputs
        if self.model not in ['c', 'ct']:
            raise ValueError("model must be 'c' or 'ct'")
            
        # Run the test
        self._run_test()
        
    def _create_fourier_terms(self, k: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create Fourier trigonometric terms."""
        t = np.arange(1, self.T + 1)
        sin_term = np.sin(2 * np.pi * k * t / self.T)
        cos_term = np.cos(2 * np.pi * k * t / self.T)
        return sin_term, cos_term
    
    def _create_deterministic_terms(self, k: int) -> np.ndarray:
        """Create deterministic regressors including Fourier terms."""
        t = np.arange(1, self.T + 1)
        
        # Constant
        const = np.ones(self.T)
        
        # Get Fourier terms
        sin_k, cos_k = self._create_fourier_terms(k)
        
        if self.model == 'c':
            # Model with constant and Fourier terms (level stationarity)
            # Order: const, sin, cos (like GAUSS)
            Z = np.column_stack([const, sin_k, cos_k])
        else:  # model == 'ct'
            # Model with constant, trend, and Fourier terms (trend stationarity)
            # Order: const, trend, sin, cos (like GAUSS)
            Z = np.column_stack([const, t, sin_k, cos_k])
            
        return Z
    
    def _ols_regression(
        self,
        y: np.ndarray,
        X: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, float]:
        """Perform OLS regression and return coefficients, residuals, and SSR."""
        # Add small regularization to avoid singular matrix
        XtX = X.T @ X
        XtX += np.eye(XtX.shape[0]) * 1e-10
        
        beta = np.linalg.solve(XtX, X.T @ y)
        residuals = y - X @ beta
        ssr = np.sum(residuals ** 2)
        
        return beta, residuals, ssr
    
    def _compute_long_run_variance(self, residuals: np.ndarray) -> float:
        """
        Compute long-run variance using Newey-West HAC estimator.
        
        Uses Bartlett kernel with specified bandwidth.
        This follows the GAUSS implementation with varm=1 (iid assumption)
        for simplicity, but can be extended for other kernels.
        """
        T = len(residuals)
        
        # For iid errors (varm=1 in GAUSS), just use residual variance
        # For more general HAC estimation, use Bartlett kernel:
        
        # Residual variance (lag 0)
        gamma_0 = np.sum(residuals ** 2) / T
        
        # For iid case (simplest, most common)
        if self.lags == 0:
            return gamma_0
        
        # Bartlett kernel for autocorrelation-robust estimation
        gamma_sum = 0.0
        for j in range(1, self.lags + 1):
            # Bartlett kernel weight
            weight = 1 - j / (self.lags + 1)
            
            # Autocovariance at lag j
            gamma_j = np.sum(residuals[j:] * residuals[:-j]) / T
            
            # Add weighted autocovariance (both positive and negative lags)
            gamma_sum += 2 * weight * gamma_j
        
        # Long-run variance
        lrv = gamma_0 + gamma_sum
        
        # Ensure positive
        return max(lrv, 1e-10)
    
    def _compute_kpss_statistic(
        self,
        residuals: np.ndarray,
        lrv: float
    ) -> float:
        """
        Compute the KPSS test statistic.
        
        τ = (1/T²) * Σ S_t² / σ²_lr
        where S_t = Σ_{j=1}^{t} e_j (partial sum of residuals)
        """
        T = len(residuals)
        
        # Partial sum of residuals
        S = np.cumsum(residuals)
        
        # KPSS statistic: (1/T²) * Σ S² / σ²_lr
        statistic = np.sum(S ** 2) / (T ** 2 * lrv)
        
        return statistic
    
    def _test_at_frequency(self, k: int) -> Tuple[float, np.ndarray, float]:
        """
        Perform test at given frequency and return statistic, residuals, and SSR.
        SSR is used for frequency selection (minimum SSR criterion).
        """
        # Create deterministic terms
        Z = self._create_deterministic_terms(k)
        
        # Detrend data using Fourier regression
        beta, residuals, ssr = self._ols_regression(self.data, Z)
        
        # Compute long-run variance
        lrv = self._compute_long_run_variance(residuals)
        
        # Compute KPSS statistic
        tau_stat = self._compute_kpss_statistic(residuals, lrv)
        
        return tau_stat, residuals, ssr
    
    def _run_test(self):
        """
        Run the complete Fourier KPSS test.
        Frequency selection uses minimum SSR (following GAUSS _get_fourier).
        """
        freq_results = []
        
        # Search over frequencies
        for k in range(1, self.max_freq + 1):
            stat, residuals, ssr = self._test_at_frequency(k)
            freq_results.append({
                'k': k,
                'stat': stat,
                'residuals': residuals,
                'ssr': ssr
            })
        
        # Select frequency by minimum SSR (like GAUSS _get_fourier)
        best_idx = np.argmin([r['ssr'] for r in freq_results])
        best_result = freq_results[best_idx]
        
        self.statistic = best_result['stat']
        self.tau_statistic = best_result['stat']
        self.optimal_frequency = best_result['k']
        self.residuals = best_result['residuals']
        self._all_freq_results = freq_results
        
        # Get critical values
        self.critical_values = self._get_critical_values()
        
        # Determine if we reject null hypothesis (stationarity)
        # For KPSS: reject stationarity if statistic > critical value
        self.reject_null = self.statistic > self.critical_values['5%']
        
        # Compute p-value with proper extrapolation
        self.pvalue = self._approximate_pvalue()
    
    def _get_critical_values(self) -> Dict[str, float]:
        """
        Get critical values from Becker, Enders, Lee (2006) Table 1a.
        
        Critical values depend on:
        - Sample size T
        - Model specification (level vs. trend stationarity)
        - Optimal frequency k
        
        Note: This matches the GAUSS implementation exactly.
        """
        k = self.optimal_frequency
        T = self.T
        
        # Critical values from Becker, Enders & Lee (2006) Table 1a
        if self.model == 'c':
            # sl(k) - level stationarity
            if T <= 250:
                crit_table = [
                    [0.2699, 0.1720, 0.1318],  # k=1
                    [0.6671, 0.4152, 0.3150],  # k=2
                    [0.7182, 0.4480, 0.3393],  # k=3
                    [0.7222, 0.4592, 0.3476],  # k=4
                    [0.7386, 0.4626, 0.3518]   # k=5
                ]
            elif 251 <= T <= 500:
                crit_table = [
                    [0.2709, 0.1696, 0.1294],
                    [0.6615, 0.4075, 0.3053],
                    [0.7046, 0.4424, 0.3309],
                    [0.7152, 0.4491, 0.3369],
                    [0.7344, 0.4571, 0.3415]
                ]
            else:  # T > 500
                crit_table = [
                    [0.2706, 0.1704, 0.1295],
                    [0.6526, 0.4047, 0.3050],
                    [0.7086, 0.4388, 0.3304],
                    [0.7163, 0.4470, 0.3355],
                    [0.7297, 0.4525, 0.3422]
                ]
        else:  # model == 'ct'
            # ss(k) - trend stationarity
            if T <= 250:
                crit_table = [
                    [0.0716, 0.0546, 0.0471],  # k=1
                    [0.2022, 0.1321, 0.1034],  # k=2
                    [0.2103, 0.1423, 0.1141],  # k=3
                    [0.2170, 0.1478, 0.1189],  # k=4
                    [0.2177, 0.1484, 0.1201]   # k=5
                ]
            elif 251 <= T <= 500:
                crit_table = [
                    [0.0720, 0.0539, 0.0463],
                    [0.1968, 0.1278, 0.0995],
                    [0.2091, 0.1404, 0.1123],
                    [0.2111, 0.1441, 0.1155],
                    [0.2178, 0.1465, 0.1178]
                ]
            else:  # T > 500
                crit_table = [
                    [0.0718, 0.0538, 0.0461],
                    [0.1959, 0.1275, 0.0994],
                    [0.2081, 0.1398, 0.1117],
                    [0.2139, 0.1436, 0.1149],
                    [0.2153, 0.1451, 0.1163]
                ]
        
        # Get critical values for optimal frequency (k-1 for 0-indexing)
        cv_values = crit_table[k - 1]
        
        return {
            '1%': cv_values[0],
            '5%': cv_values[1],
            '10%': cv_values[2]
        }
    
    def _approximate_pvalue(self) -> float:
        """
        Approximate p-value based on critical values with proper extrapolation.
        For KPSS tests, larger statistics indicate stronger evidence against stationarity.
        """
        cv = self.critical_values
        stat = self.statistic
        
        if stat > cv['1%']:
            # Extrapolate beyond 1% (very strong rejection of stationarity)
            slope = (0.01 - 0.05) / (cv['1%'] - cv['5%'])
            pval = 0.01 + slope * (stat - cv['1%'])
            return max(pval, 0.001)  # Cap at 0.001
        elif stat > cv['5%']:
            # Interpolate between 1% and 5%
            slope = (0.01 - 0.05) / (cv['1%'] - cv['5%'])
            return 0.05 + slope * (stat - cv['5%'])
        elif stat > cv['10%']:
            # Interpolate between 5% and 10%
            slope = (0.05 - 0.10) / (cv['5%'] - cv['10%'])
            return 0.10 + slope * (stat - cv['10%'])
        else:
            # Extrapolate beyond 10% (fail to reject stationarity)
            slope = (0.05 - 0.10) / (cv['5%'] - cv['10%'])
            pval = 0.10 + slope * (stat - cv['10%'])
            return min(pval, 0.99)  # Cap at 0.99
    
    def f_test_linearity(self) -> FTestResult:
        """
        F-test for linearity (presence of Fourier terms).
        
        Tests H0: c1 = c2 = 0 (no Fourier terms needed)
        against H1: at least one Fourier coefficient is non-zero
        
        If F-stat < critical value, the null of linearity is not rejected,
        and the standard KPSS test should be used instead.
        
        Note: This F-test should only be used after confirming stationarity
        (i.e., when the KPSS null is not rejected).
        
        Returns
        -------
        FTestResult
            Named tuple with f_statistic, critical_values, pvalue, reject_null,
            and frequency
            
        References
        ----------
        Becker, Enders & Lee (2006), Table 1c for F critical values
        """
        k = self.optimal_frequency
        T = self.T
        
        # Create regressors for restricted model (without Fourier terms)
        const = np.ones(T)
        trend = np.arange(1, T + 1)
        
        if self.model == 'c':
            X_restricted = const.reshape(-1, 1)
        else:  # model == 'ct'
            X_restricted = np.column_stack([const, trend])
        
        # Create regressors for unrestricted model (with Fourier terms)
        sin_k, cos_k = self._create_fourier_terms(k)
        
        if self.model == 'c':
            X_unrestricted = np.column_stack([const, sin_k, cos_k])
        else:  # model == 'ct'
            X_unrestricted = np.column_stack([const, trend, sin_k, cos_k])
        
        # Run regressions
        _, _, ssr_restricted = self._ols_regression(self.data, X_restricted)
        _, _, ssr_unrestricted = self._ols_regression(self.data, X_unrestricted)
        
        # F-statistic: ((SSR_r - SSR_u) / q) / (SSR_u / (T - k_u))
        q = 2  # Number of restrictions (sin and cos)
        k_unrestricted = X_unrestricted.shape[1]
        
        f_stat = ((ssr_restricted - ssr_unrestricted) / q) / (ssr_unrestricted / (T - k_unrestricted))
        
        # Get F critical values from Becker, Enders & Lee (2006) Table 1c
        f_cv = self._get_f_critical_values()
        
        # Reject linearity if F > critical value
        reject_linearity = f_stat > f_cv['5%']
        
        # Approximate p-value for F-test
        if f_stat > f_cv['1%']:
            f_pval = 0.01
        elif f_stat > f_cv['5%']:
            slope = (0.01 - 0.05) / (f_cv['1%'] - f_cv['5%'])
            f_pval = 0.05 + slope * (f_stat - f_cv['5%'])
        elif f_stat > f_cv['10%']:
            slope = (0.05 - 0.10) / (f_cv['5%'] - f_cv['10%'])
            f_pval = 0.10 + slope * (f_stat - f_cv['10%'])
        else:
            # Extrapolate beyond 10%
            slope = (0.05 - 0.10) / (f_cv['5%'] - f_cv['10%'])
            f_pval = min(0.10 + slope * (f_stat - f_cv['10%']), 0.99)
        
        return FTestResult(
            f_statistic=f_stat,
            critical_values=f_cv,
            pvalue=f_pval,
            reject_null=reject_linearity,
            frequency=k
        )
    
    def _get_f_critical_values(self) -> Dict[str, float]:
        """
        Get F-test critical values from Becker, Enders & Lee (2006) Table 1c.
        These are used to test H0: c1 = c2 = 0 (linearity).
        """
        T = self.T
        
        # F critical values from Table 1c
        # Note: These are for testing linearity when k is estimated
        if self.model == 'c':
            # Fl(k̂) - level stationarity F-test
            if T < 500:
                cv = [6.730, 4.929, 4.133]
            else:  # T >= 500
                cv = [6.281, 4.651, 3.935]
        else:  # model == 'ct'
            # Fs(k̂) - trend stationarity F-test
            if T < 500:
                cv = [6.873, 4.972, 4.162]
            else:  # T >= 500
                cv = [6.315, 4.669, 3.928]
        
        return {
            '1%': cv[0],
            '5%': cv[1],
            '10%': cv[2]
        }
    
    def summary(self) -> str:
        """Return a formatted summary of test results."""
        summary = []
        summary.append("=" * 65)
        summary.append("       Fourier KPSS Stationarity Test Results")
        summary.append("       Becker, Enders & Lee (2006) JTSA")
        summary.append("=" * 65)
        summary.append(f"Model: {'Level stationarity' if self.model == 'c' else 'Trend stationarity'}")
        summary.append(f"Sample size: {self.T}")
        summary.append(f"Maximum frequency: {self.max_freq}")
        summary.append(f"Newey-West lags: {self.lags}")
        summary.append(f"Null hypothesis: Stationarity around Fourier components")
        summary.append("-" * 65)
        summary.append(f"Optimal frequency (k): {self.optimal_frequency}")
        summary.append(f"KPSS statistic (τ): {self.tau_statistic:.6f}")
        summary.append(f"P-value: {self.pvalue:.4f}")
        summary.append("-" * 65)
        summary.append("Critical values:")
        for level, value in self.critical_values.items():
            marker = " *" if (level == '5%' and self.reject_null) or \
                          (level == '1%' and self.statistic > value) else ""
            summary.append(f"  {level:>3s} : {value:8.6f}{marker}")
        summary.append("-" * 65)
        
        # Add F-test results
        f_result = self.f_test_linearity()
        summary.append("F-test for linearity (H0: no Fourier terms needed):")
        summary.append(f"  F-statistic: {f_result.f_statistic:.4f}")
        summary.append(f"  Critical values: 1%={f_result.critical_values['1%']:.3f}, "
                      f"5%={f_result.critical_values['5%']:.3f}, "
                      f"10%={f_result.critical_values['10%']:.3f}")
        if f_result.reject_null:
            summary.append("  → Reject linearity: Fourier terms ARE significant")
        else:
            summary.append("  → Cannot reject linearity: Consider standard KPSS test")
        
        summary.append("-" * 65)
        summary.append(f"Conclusion: {'Reject' if self.reject_null else 'Fail to reject'} "
                      f"null hypothesis of stationarity")
        summary.append(f"            at 5% significance level")
        if not self.reject_null:
            summary.append(f"            → Evidence for stationarity with smooth breaks")
        else:
            summary.append(f"            → Evidence against stationarity (possible unit root)")
        summary.append("=" * 65)
        
        return '\n'.join(summary)
    
    def __repr__(self) -> str:
        return (f"FourierKPSS(statistic={self.statistic:.6f}, "
                f"optimal_frequency={self.optimal_frequency}, "
                f"reject_null={self.reject_null})")


def fourier_kpss_test(
    data: Union[np.ndarray, pd.Series, list],
    model: str = 'c',
    max_freq: int = 5,
    lags: Union[str, int] = 'auto'
) -> FourierKPSS:
    """
    Convenience function for Fourier KPSS stationarity test.
    
    Parameters
    ----------
    data : array-like
        Time series data to test
    model : str, default='c'
        Deterministic terms: 'c' for level stationarity, 'ct' for trend stationarity
    max_freq : int, default=5
        Maximum frequency to search (must be between 1 and 5)
    lags : str or int, default='auto'
        Number of lags for Newey-West HAC estimator
        
    Returns
    -------
    FourierKPSS
        Test results object
        
    Examples
    --------
    >>> import numpy as np
    >>> from funitroot import fourier_kpss_test
    >>> 
    >>> # Generate stationary data with structural break
    >>> np.random.seed(42)
    >>> T = 200
    >>> t = np.arange(T)
    >>> # Stationary process with smooth mean shift
    >>> y = 5 + 3 * np.sin(2 * np.pi * t / T) + np.random.randn(T) * 0.5
    >>> 
    >>> # Perform test
    >>> result = fourier_kpss_test(y, model='c', max_freq=3)
    >>> print(result.summary())
    >>> print(f"Stationary: {not result.reject_null}")
    >>> 
    >>> # Check F-test for linearity
    >>> f_result = result.f_test_linearity()
    >>> print(f"F-statistic: {f_result.f_statistic:.4f}")
    >>> print(f"Fourier terms significant: {f_result.reject_null}")
    """
    return FourierKPSS(
        data=data,
        model=model,
        max_freq=max_freq,
        lags=lags
    )


def fourier_kpss_f_test(
    data: Union[np.ndarray, pd.Series, list],
    model: str = 'c',
    k: int = 1
) -> FTestResult:
    """
    Standalone F-test for linearity in Fourier KPSS framework.
    
    Tests H0: c1 = c2 = 0 (Fourier terms not needed)
    
    Parameters
    ----------
    data : array-like
        Time series data
    model : str, default='c'
        'c' for level stationarity, 'ct' for trend stationarity
    k : int, default=1
        Fourier frequency to test
        
    Returns
    -------
    FTestResult
        Named tuple with test results
        
    Examples
    --------
    >>> import numpy as np
    >>> from funitroot import fourier_kpss_f_test
    >>> 
    >>> np.random.seed(42)
    >>> T = 200
    >>> t = np.arange(T)
    >>> y = 5 + 3 * np.sin(2 * np.pi * t / T) + np.random.randn(T) * 0.5
    >>> result = fourier_kpss_f_test(y, model='c', k=1)
    >>> print(f"F-statistic: {result.f_statistic:.4f}")
    >>> print(f"Reject linearity: {result.reject_null}")
    """
    # Convert and validate data
    if isinstance(data, (pd.Series, pd.DataFrame)):
        data_arr = data.values.flatten()
    else:
        data_arr = np.array(data).flatten()
    
    data_arr = data_arr[~np.isnan(data_arr)]
    T = len(data_arr)
    
    # Validate inputs
    model = model.lower()
    if model not in ['c', 'ct']:
        raise ValueError("model must be 'c' or 'ct'")
    if k < 1 or k > 5:
        raise ValueError("k must be between 1 and 5")
    
    # Create regressors for restricted model (without Fourier terms)
    const = np.ones(T)
    trend = np.arange(1, T + 1)
    
    if model == 'c':
        X_restricted = const.reshape(-1, 1)
    else:  # model == 'ct'
        X_restricted = np.column_stack([const, trend])
    
    # Create Fourier terms
    t = np.arange(1, T + 1)
    sin_k = np.sin(2 * np.pi * k * t / T)
    cos_k = np.cos(2 * np.pi * k * t / T)
    
    # Create regressors for unrestricted model (with Fourier terms)
    if model == 'c':
        X_unrestricted = np.column_stack([const, sin_k, cos_k])
    else:  # model == 'ct'
        X_unrestricted = np.column_stack([const, trend, sin_k, cos_k])
    
    # OLS helper
    def ols(y, X):
        XtX = X.T @ X + np.eye(X.shape[1]) * 1e-10
        beta = np.linalg.solve(XtX, X.T @ y)
        resid = y - X @ beta
        return np.sum(resid ** 2)
    
    ssr_restricted = ols(data_arr, X_restricted)
    ssr_unrestricted = ols(data_arr, X_unrestricted)
    
    # F-statistic
    q = 2  # Number of restrictions (sin and cos)
    k_unrestricted = X_unrestricted.shape[1]
    
    f_stat = ((ssr_restricted - ssr_unrestricted) / q) / (ssr_unrestricted / (T - k_unrestricted))
    
    # Get F critical values
    if model == 'c':
        if T < 500:
            cv = [6.730, 4.929, 4.133]
        else:
            cv = [6.281, 4.651, 3.935]
    else:  # model == 'ct'
        if T < 500:
            cv = [6.873, 4.972, 4.162]
        else:
            cv = [6.315, 4.669, 3.928]
    
    f_cv = {'1%': cv[0], '5%': cv[1], '10%': cv[2]}
    
    # P-value approximation
    if f_stat > f_cv['1%']:
        f_pval = 0.01
    elif f_stat > f_cv['5%']:
        slope = (0.01 - 0.05) / (f_cv['1%'] - f_cv['5%'])
        f_pval = 0.05 + slope * (f_stat - f_cv['5%'])
    elif f_stat > f_cv['10%']:
        slope = (0.05 - 0.10) / (f_cv['5%'] - f_cv['10%'])
        f_pval = 0.10 + slope * (f_stat - f_cv['10%'])
    else:
        slope = (0.05 - 0.10) / (f_cv['5%'] - f_cv['10%'])
        f_pval = min(0.10 + slope * (f_stat - f_cv['10%']), 0.99)
    
    return FTestResult(
        f_statistic=f_stat,
        critical_values=f_cv,
        pvalue=f_pval,
        reject_null=f_stat > f_cv['5%'],
        frequency=k
    )
