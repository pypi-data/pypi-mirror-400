"""
Fourier ADF Unit Root Test
Based on: Enders, W., and Lee, J. (2012)
"The flexible Fourier form and Dickey-Fuller type unit root test"
Economics Letters, 117, (2012), 196-199.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/funitroot
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple, Optional, Union, Dict, List, NamedTuple
import warnings


class FTestResult(NamedTuple):
    """Result container for F-test for linearity."""
    f_statistic: float
    critical_values: Dict[str, float]
    pvalue: float
    reject_null: bool
    frequency: int
    lags: int


class FourierADF:
    """
    Fourier ADF unit root test with flexible Fourier form.
    
    This test allows for smooth structural breaks of unknown number and form
    using Fourier approximations.
    
    Parameters
    ----------
    data : array-like
        Time series data to test
    model : str, default='c'
        Deterministic terms: 'c' for constant, 'ct' for constant and trend
    max_lag : int, optional
        Maximum lag length for augmentation. Default is 8.
    max_freq : int, default=5
        Maximum frequency to search (must be between 1 and 5)
    ic : str, default='aic'
        Information criterion for lag selection: 'aic', 'bic', or 'tstat'
        
    Attributes
    ----------
    statistic : float
        The test statistic value
    pvalue : float
        The p-value (based on critical values)
    optimal_frequency : int
        The selected optimal frequency (minimizes SSR)
    optimal_lag : int
        The selected optimal lag
    critical_values : dict
        Critical values at 1%, 5%, and 10% levels
    reject_null : bool
        Whether to reject the null hypothesis of unit root
        
    References
    ----------
    Enders, W., and Lee, J. (2012). "The flexible Fourier form and 
    Dickey-Fuller type unit root tests," Economics Letters, 117, 196-199.
    """
    
    def __init__(
        self,
        data: Union[np.ndarray, pd.Series, list],
        model: str = 'c',
        max_lag: Optional[int] = None,
        max_freq: int = 5,
        ic: str = 'aic'
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
        self.ic = ic.lower()
        
        # Validate max_freq - raise error instead of silent capping
        if max_freq < 1 or max_freq > 5:
            raise ValueError("max_freq must be between 1 and 5")
        self.max_freq = max_freq
        
        # Set default max_lag if not provided (like GAUSS: pmax=8)
        if max_lag is None:
            self.max_lag = 8
        else:
            self.max_lag = max_lag
            
        # Validate inputs
        if self.model not in ['c', 'ct']:
            raise ValueError("model must be 'c' or 'ct'")
        if self.ic not in ['aic', 'bic', 'tstat']:
            raise ValueError("ic must be 'aic', 'bic', or 'tstat'")
            
        # Run the test
        self._run_test()
        
    def _create_fourier_terms(self, k: int, T: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create Fourier trigonometric terms."""
        t = np.arange(1, T + 1)
        sin_term = np.sin(2 * np.pi * k * t / T)
        cos_term = np.cos(2 * np.pi * k * t / T)
        return sin_term, cos_term
    
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
    
    def _compute_aic_bic(
        self,
        ssr: float,
        n_obs: int,
        n_params: int
    ) -> Tuple[float, float]:
        """Compute AIC and BIC."""
        log_ssr = np.log(ssr / n_obs)
        aic = log_ssr + 2 * n_params / n_obs
        bic = log_ssr + n_params * np.log(n_obs) / n_obs
        return aic, bic
    
    def _test_at_frequency_and_lag(
        self,
        k: int,
        p: int
    ) -> Tuple[float, float, float]:
        """
        Perform test at given frequency k and lag p.
        Returns: (t_statistic, ssr, tstat_last_lag)
        """
        T = self.T
        
        # Create data
        dy = np.diff(self.data)  # First difference
        y_lag = self.data[:-1]   # Lagged level y(t-1)
        
        # Create deterministic terms
        const = np.ones(T)
        trend = np.arange(1, T + 1)
        sink, cosk = self._create_fourier_terms(k, T)
        
        # Trim for differencing
        const = const[1:]
        trend = trend[1:]
        sink = sink[1:]
        cosk = cosk[1:]
        
        # Create lagged differences if p > 0
        if p > 0:
            dy_lags = np.column_stack([
                np.concatenate([np.zeros(i+1), dy[:-i-1]]) for i in range(p)
            ])
            # Trim for lags
            dep = dy[p:]
            y1 = y_lag[p:]
            dc = const[p:]
            dt = trend[p:]
            sinp = sink[p:]
            cosp = cosk[p:]
            ldy = dy_lags[p:]
        else:
            dep = dy
            y1 = y_lag
            dc = const
            dt = trend
            sinp = sink
            cosp = cosk
            ldy = None
        
        # Build regressor matrix (order matches GAUSS: y1, const, [trend], sin, cos, [lags])
        if self.model == 'c':
            if p > 0:
                X = np.column_stack([y1, dc, sinp, cosp, ldy])
            else:
                X = np.column_stack([y1, dc, sinp, cosp])
        else:  # model == 'ct'
            if p > 0:
                X = np.column_stack([y1, dc, dt, sinp, cosp, ldy])
            else:
                X = np.column_stack([y1, dc, dt, sinp, cosp])
        
        # OLS regression
        beta, residuals, ssr = self._ols_regression(dep, X)
        n_obs = len(dep)
        n_params = X.shape[1]
        
        # Compute standard errors
        sigma2 = ssr / (n_obs - n_params)
        XtX_inv = np.linalg.inv(X.T @ X + np.eye(n_params) * 1e-10)
        se = np.sqrt(sigma2 * np.diag(XtX_inv))
        
        # t-statistic for rho (coefficient on y1, first position)
        t_stat = beta[0] / se[0]
        
        # t-statistic for last lag (for lag selection via t-stat criterion)
        if p > 0:
            tstat_last = np.abs(beta[-1] / se[-1])
        else:
            tstat_last = 0
        
        return t_stat, ssr, tstat_last
    
    def _select_lag_at_frequency(self, k: int) -> Tuple[int, float, float]:
        """
        Select optimal lag for given frequency k using information criterion.
        Returns: (optimal_lag, t_statistic, ssr)
        """
        results = []
        
        for p in range(self.max_lag + 1):
            t_stat, ssr, tstat_last = self._test_at_frequency_and_lag(k, p)
            
            # Compute information criteria
            n_obs = self.T - 1 - p  # observations after differencing and lags
            n_params = 4 if self.model == 'c' else 5  # y1, const, [trend], sin, cos
            n_params += p  # add lag parameters
            
            aic, bic = self._compute_aic_bic(ssr, n_obs, n_params)
            
            results.append({
                'p': p,
                't_stat': t_stat,
                'ssr': ssr,
                'aic': aic,
                'bic': bic,
                'tstat_last': tstat_last
            })
        
        # Select lag based on criterion
        if self.ic == 'aic':
            opt_idx = np.argmin([r['aic'] for r in results])
        elif self.ic == 'bic':
            opt_idx = np.argmin([r['bic'] for r in results])
        else:  # tstat - general-to-specific
            opt_idx = self.max_lag
            for p in range(self.max_lag, 0, -1):
                if results[p]['tstat_last'] > 1.645:  # 10% significance
                    opt_idx = p
                    break
            else:
                opt_idx = 0
        
        opt_result = results[opt_idx]
        return opt_result['p'], opt_result['t_stat'], opt_result['ssr']
    
    def _run_test(self):
        """
        Run the complete Fourier ADF test.
        Frequency selection uses minimum SSR (following GAUSS implementation).
        """
        freq_results = []
        
        # Search over frequencies
        for k in range(1, self.max_freq + 1):
            opt_lag, t_stat, ssr = self._select_lag_at_frequency(k)
            freq_results.append({
                'k': k,
                'p': opt_lag,
                't_stat': t_stat,
                'ssr': ssr
            })
        
        # Select frequency by minimum SSR (like GAUSS _get_fourier)
        best_idx = np.argmin([r['ssr'] for r in freq_results])
        best_result = freq_results[best_idx]
        
        self.statistic = best_result['t_stat']
        self.optimal_frequency = best_result['k']
        self.optimal_lag = best_result['p']
        self._all_freq_results = freq_results
        
        # Get critical values
        self.critical_values = self._get_critical_values()
        
        # Determine if we reject null hypothesis (unit root)
        # Reject if t-stat < critical value (more negative)
        self.reject_null = self.statistic < self.critical_values['5%']
        
        # Compute p-value with proper extrapolation
        self.pvalue = self._approximate_pvalue()
    
    def _get_critical_values(self) -> Dict[str, float]:
        """
        Get critical values from Enders & Lee (2012) Table 1.
        
        Critical values depend on:
        - Sample size T
        - Model specification (constant vs. constant + trend)
        - Optimal frequency k
        
        Note: This matches the GAUSS implementation exactly.
        """
        k = self.optimal_frequency
        T = self.T
        
        # Critical values from Enders & Lee (2012) Table 1b (model='c') and Table 1a (model='ct')
        if self.model == 'c':
            # Table 1b: τDF_C without linear trend
            if T <= 150:
                crit_table = [
                    [-4.42, -3.81, -3.49],  # k=1
                    [-3.97, -3.27, -2.91],  # k=2
                    [-3.77, -3.07, -2.71],  # k=3
                    [-3.64, -2.97, -2.64],  # k=4
                    [-3.58, -2.93, -2.60]   # k=5
                ]
            elif 151 <= T <= 349:
                crit_table = [
                    [-4.37, -3.78, -3.47],
                    [-3.93, -3.26, -2.92],
                    [-3.74, -3.06, -2.72],
                    [-3.62, -2.98, -2.65],
                    [-3.55, -2.94, -2.62]
                ]
            elif 350 <= T <= 500:
                crit_table = [
                    [-4.35, -3.76, -3.46],
                    [-3.91, -3.26, -2.91],
                    [-3.70, -3.06, -2.72],
                    [-3.62, -2.97, -2.66],
                    [-3.56, -2.94, -2.62]
                ]
            else:  # T > 500
                crit_table = [
                    [-4.31, -3.75, -3.45],
                    [-3.89, -3.25, -2.90],
                    [-3.69, -3.05, -2.71],
                    [-3.61, -2.96, -2.64],
                    [-3.53, -2.93, -2.61]
                ]
        else:  # model == 'ct'
            # Table 1a: τDF_t with linear trend
            if T <= 150:
                crit_table = [
                    [-4.95, -4.35, -4.05],  # k=1
                    [-4.69, -4.05, -3.71],  # k=2
                    [-4.45, -3.78, -3.44],  # k=3
                    [-4.29, -3.65, -3.29],  # k=4
                    [-4.20, -3.56, -3.22]   # k=5
                ]
            elif 151 <= T <= 349:
                crit_table = [
                    [-4.87, -4.31, -4.02],
                    [-4.62, -4.01, -3.69],
                    [-4.38, -3.77, -3.43],
                    [-4.27, -3.63, -3.31],
                    [-4.18, -3.56, -3.24]
                ]
            elif 350 <= T <= 500:
                crit_table = [
                    [-4.81, -4.29, -4.01],
                    [-4.57, -3.99, -3.67],
                    [-4.38, -3.76, -3.43],
                    [-4.25, -3.64, -3.31],
                    [-4.18, -3.56, -3.25]
                ]
            else:  # T > 500
                crit_table = [
                    [-4.80, -4.27, -4.00],
                    [-4.58, -3.98, -3.67],
                    [-4.38, -3.75, -3.43],
                    [-4.24, -3.63, -3.30],
                    [-4.16, -3.55, -3.24]
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
        For ADF tests, smaller (more negative) statistics indicate stronger rejection.
        """
        cv = self.critical_values
        stat = self.statistic
        
        if stat < cv['1%']:
            # Extrapolate beyond 1% (very strong rejection)
            slope = (0.01 - 0.05) / (cv['1%'] - cv['5%'])
            pval = 0.01 + slope * (stat - cv['1%'])
            return max(pval, 0.001)  # Cap at 0.001
        elif stat < cv['5%']:
            # Interpolate between 1% and 5%
            slope = (0.01 - 0.05) / (cv['1%'] - cv['5%'])
            return 0.05 + slope * (stat - cv['5%'])
        elif stat < cv['10%']:
            # Interpolate between 5% and 10%
            slope = (0.05 - 0.10) / (cv['5%'] - cv['10%'])
            return 0.10 + slope * (stat - cv['10%'])
        else:
            # Extrapolate beyond 10% (fail to reject)
            slope = (0.05 - 0.10) / (cv['5%'] - cv['10%'])
            pval = 0.10 + slope * (stat - cv['10%'])
            return min(pval, 0.99)  # Cap at 0.99
    
    def f_test_linearity(self) -> FTestResult:
        """
        F-test for linearity (presence of Fourier terms).
        
        Tests H0: c3 = c4 = 0 (no Fourier terms needed)
        against H1: at least one Fourier coefficient is non-zero
        
        If F-stat < critical value, the null of linearity is not rejected,
        and the standard ADF test should be used instead.
        
        Returns
        -------
        FTestResult
            Named tuple with f_statistic, critical_values, pvalue, reject_null,
            frequency, and lags
            
        References
        ----------
        Enders & Lee (2012), Table 1a and 1b for F critical values
        """
        k = self.optimal_frequency
        p = self.optimal_lag
        T = self.T
        
        # Create data
        dy = np.diff(self.data)
        y_lag = self.data[:-1]
        
        # Create deterministic terms
        const = np.ones(T)[1:]
        trend = np.arange(1, T + 1)[1:]
        sink, cosk = self._create_fourier_terms(k, T)
        sink = sink[1:]
        cosk = cosk[1:]
        
        # Create lagged differences if p > 0
        if p > 0:
            dy_lags = np.column_stack([
                np.concatenate([np.zeros(i+1), dy[:-i-1]]) for i in range(p)
            ])
            dep = dy[p:]
            y1 = y_lag[p:]
            dc = const[p:]
            dt = trend[p:]
            sinp = sink[p:]
            cosp = cosk[p:]
            ldy = dy_lags[p:]
        else:
            dep = dy
            y1 = y_lag
            dc = const
            dt = trend
            sinp = sink
            cosp = cosk
            ldy = None
        
        # Restricted model (without Fourier terms)
        if self.model == 'c':
            if p > 0:
                X_restricted = np.column_stack([y1, dc, ldy])
            else:
                X_restricted = np.column_stack([y1, dc])
        else:  # model == 'ct'
            if p > 0:
                X_restricted = np.column_stack([y1, dc, dt, ldy])
            else:
                X_restricted = np.column_stack([y1, dc, dt])
        
        # Unrestricted model (with Fourier terms)
        if self.model == 'c':
            if p > 0:
                X_unrestricted = np.column_stack([y1, dc, sinp, cosp, ldy])
            else:
                X_unrestricted = np.column_stack([y1, dc, sinp, cosp])
        else:  # model == 'ct'
            if p > 0:
                X_unrestricted = np.column_stack([y1, dc, dt, sinp, cosp, ldy])
            else:
                X_unrestricted = np.column_stack([y1, dc, dt, sinp, cosp])
        
        # Run regressions
        _, _, ssr_restricted = self._ols_regression(dep, X_restricted)
        _, _, ssr_unrestricted = self._ols_regression(dep, X_unrestricted)
        
        # F-statistic: ((SSR_r - SSR_u) / q) / (SSR_u / (T - k))
        q = 2  # Number of restrictions (sin and cos)
        n_obs = len(dep)
        k_unrestricted = X_unrestricted.shape[1]
        
        f_stat = ((ssr_restricted - ssr_unrestricted) / q) / (ssr_unrestricted / (n_obs - k_unrestricted))
        
        # Get F critical values from Enders & Lee (2012) Table 1a/1b
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
            frequency=k,
            lags=p
        )
    
    def _get_f_critical_values(self) -> Dict[str, float]:
        """
        Get F-test critical values from Enders & Lee (2012) Table 1a/1b.
        These are used to test H0: c3 = c4 = 0 (linearity).
        """
        T = self.T
        
        # F critical values for testing linearity (H0: no Fourier terms)
        # From Enders & Lee (2012) Table 1a (ct) and Table 1b (c)
        if self.model == 'ct':
            # Table 1a: Critical values of F(k̂) = MaxF(k) with trend
            if T <= 150:
                cv = [12.21, 9.14, 7.78]
            elif 151 <= T <= 349:
                cv = [11.70, 8.88, 7.62]
            elif 350 <= T <= 500:
                cv = [11.52, 8.76, 7.53]
            else:  # T > 500
                cv = [11.35, 8.71, 7.50]
        else:  # model == 'c'
            # Table 1b: Critical values of F(k̂) = MaxF(k) without trend
            if T <= 150:
                cv = [10.35, 7.58, 6.35]
            elif 151 <= T <= 349:
                cv = [10.02, 7.41, 6.25]
            elif 350 <= T <= 500:
                cv = [9.78, 7.29, 6.16]
            else:  # T > 500
                cv = [9.72, 7.25, 6.11]
        
        return {
            '1%': cv[0],
            '5%': cv[1],
            '10%': cv[2]
        }
    
    def summary(self) -> str:
        """Return a formatted summary of test results."""
        summary = []
        summary.append("=" * 65)
        summary.append("        Fourier ADF Unit Root Test Results")
        summary.append("        Enders & Lee (2012) Economics Letters")
        summary.append("=" * 65)
        summary.append(f"Model: {'Constant' if self.model == 'c' else 'Constant + Trend'}")
        summary.append(f"Sample size: {self.T}")
        summary.append(f"Maximum lag tested: {self.max_lag}")
        summary.append(f"Maximum frequency: {self.max_freq}")
        summary.append(f"Lag selection criterion: {self.ic.upper()}")
        summary.append("-" * 65)
        summary.append(f"Optimal frequency (k): {self.optimal_frequency}")
        summary.append(f"Optimal lag (p): {self.optimal_lag}")
        summary.append(f"ADF statistic: {self.statistic:.4f}")
        summary.append(f"P-value: {self.pvalue:.4f}")
        summary.append("-" * 65)
        summary.append("Critical values:")
        for level, value in self.critical_values.items():
            marker = " *" if (level == '5%' and self.reject_null) or \
                          (level == '1%' and self.statistic < value) else ""
            summary.append(f"  {level:>3s} : {value:7.4f}{marker}")
        summary.append("-" * 65)
        
        # Add F-test results
        f_result = self.f_test_linearity()
        summary.append("F-test for linearity (H0: no Fourier terms needed):")
        summary.append(f"  F-statistic: {f_result.f_statistic:.4f}")
        summary.append(f"  Critical values: 1%={f_result.critical_values['1%']:.2f}, "
                      f"5%={f_result.critical_values['5%']:.2f}, "
                      f"10%={f_result.critical_values['10%']:.2f}")
        if f_result.reject_null:
            summary.append("  → Reject linearity: Fourier terms ARE significant")
        else:
            summary.append("  → Cannot reject linearity: Consider standard ADF test")
        
        summary.append("-" * 65)
        summary.append(f"Conclusion: {'Reject' if self.reject_null else 'Fail to reject'} "
                      f"null hypothesis of unit root")
        summary.append(f"            at 5% significance level")
        summary.append("=" * 65)
        
        return '\n'.join(summary)
    
    def __repr__(self) -> str:
        return (f"FourierADF(statistic={self.statistic:.4f}, "
                f"optimal_frequency={self.optimal_frequency}, "
                f"optimal_lag={self.optimal_lag}, "
                f"reject_null={self.reject_null})")


def fourier_adf_test(
    data: Union[np.ndarray, pd.Series, list],
    model: str = 'c',
    max_lag: Optional[int] = None,
    max_freq: int = 5,
    ic: str = 'aic'
) -> FourierADF:
    """
    Convenience function for Fourier ADF test.
    
    Parameters
    ----------
    data : array-like
        Time series data to test
    model : str, default='c'
        Deterministic terms: 'c' for constant, 'ct' for constant and trend
    max_lag : int, optional
        Maximum lag length for augmentation. Default is 8.
    max_freq : int, default=5
        Maximum frequency to search (must be between 1 and 5)
    ic : str, default='aic'
        Information criterion for lag selection: 'aic', 'bic', or 'tstat'
        
    Returns
    -------
    FourierADF
        Test results object
        
    Examples
    --------
    >>> import numpy as np
    >>> from funitroot import fourier_adf_test
    >>> 
    >>> # Generate stationary data with structural break
    >>> np.random.seed(42)
    >>> T = 200
    >>> t = np.arange(T)
    >>> y = 5 + 3 * np.sin(2 * np.pi * t / T) + np.cumsum(np.random.randn(T) * 0.1)
    >>> 
    >>> # Perform test
    >>> result = fourier_adf_test(y, model='c', max_freq=3)
    >>> print(result.summary())
    >>> 
    >>> # Check F-test for linearity
    >>> f_result = result.f_test_linearity()
    >>> print(f"F-statistic: {f_result.f_statistic:.4f}")
    >>> print(f"Fourier terms significant: {f_result.reject_null}")
    """
    return FourierADF(
        data=data,
        model=model,
        max_lag=max_lag,
        max_freq=max_freq,
        ic=ic
    )


def fourier_adf_f_test(
    data: Union[np.ndarray, pd.Series, list],
    model: str = 'c',
    k: int = 1,
    p: int = 0
) -> FTestResult:
    """
    Standalone F-test for linearity in Fourier ADF framework.
    
    Tests H0: c3 = c4 = 0 (Fourier terms not needed)
    
    Parameters
    ----------
    data : array-like
        Time series data
    model : str, default='c'
        'c' for constant, 'ct' for constant and trend
    k : int, default=1
        Fourier frequency to test
    p : int, default=0
        Number of lags to include
        
    Returns
    -------
    FTestResult
        Named tuple with test results
        
    Examples
    --------
    >>> import numpy as np
    >>> from funitroot import fourier_adf_f_test
    >>> 
    >>> np.random.seed(42)
    >>> y = np.cumsum(np.random.randn(200))
    >>> result = fourier_adf_f_test(y, model='c', k=1, p=4)
    >>> print(f"F-statistic: {result.f_statistic:.4f}")
    >>> print(f"Reject linearity: {result.reject_null}")
    """
    # Create a temporary FourierADF object with specific k
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
    
    # Create data
    dy = np.diff(data_arr)
    y_lag = data_arr[:-1]
    
    # Create deterministic terms
    const = np.ones(T)[1:]
    trend = np.arange(1, T + 1)[1:]
    t_idx = np.arange(1, T + 1)
    sink = np.sin(2 * np.pi * k * t_idx / T)[1:]
    cosk = np.cos(2 * np.pi * k * t_idx / T)[1:]
    
    # Create lagged differences if p > 0
    if p > 0:
        dy_lags = np.column_stack([
            np.concatenate([np.zeros(i+1), dy[:-i-1]]) for i in range(p)
        ])
        dep = dy[p:]
        y1 = y_lag[p:]
        dc = const[p:]
        dt = trend[p:]
        sinp = sink[p:]
        cosp = cosk[p:]
        ldy = dy_lags[p:]
    else:
        dep = dy
        y1 = y_lag
        dc = const
        dt = trend
        sinp = sink
        cosp = cosk
        ldy = None
    
    # Restricted model (without Fourier terms)
    if model == 'c':
        if p > 0:
            X_restricted = np.column_stack([y1, dc, ldy])
        else:
            X_restricted = np.column_stack([y1, dc])
    else:  # model == 'ct'
        if p > 0:
            X_restricted = np.column_stack([y1, dc, dt, ldy])
        else:
            X_restricted = np.column_stack([y1, dc, dt])
    
    # Unrestricted model (with Fourier terms)
    if model == 'c':
        if p > 0:
            X_unrestricted = np.column_stack([y1, dc, sinp, cosp, ldy])
        else:
            X_unrestricted = np.column_stack([y1, dc, sinp, cosp])
    else:  # model == 'ct'
        if p > 0:
            X_unrestricted = np.column_stack([y1, dc, dt, sinp, cosp, ldy])
        else:
            X_unrestricted = np.column_stack([y1, dc, dt, sinp, cosp])
    
    # OLS helper
    def ols(y, X):
        XtX = X.T @ X + np.eye(X.shape[1]) * 1e-10
        beta = np.linalg.solve(XtX, X.T @ y)
        resid = y - X @ beta
        return np.sum(resid ** 2)
    
    ssr_restricted = ols(dep, X_restricted)
    ssr_unrestricted = ols(dep, X_unrestricted)
    
    # F-statistic
    q = 2  # Number of restrictions (sin and cos)
    n_obs = len(dep)
    k_unrestricted = X_unrestricted.shape[1]
    
    f_stat = ((ssr_restricted - ssr_unrestricted) / q) / (ssr_unrestricted / (n_obs - k_unrestricted))
    
    # Get F critical values
    if model == 'ct':
        if T <= 150:
            cv = [12.21, 9.14, 7.78]
        elif 151 <= T <= 349:
            cv = [11.70, 8.88, 7.62]
        elif 350 <= T <= 500:
            cv = [11.52, 8.76, 7.53]
        else:
            cv = [11.35, 8.71, 7.50]
    else:
        if T <= 150:
            cv = [10.35, 7.58, 6.35]
        elif 151 <= T <= 349:
            cv = [10.02, 7.41, 6.25]
        elif 350 <= T <= 500:
            cv = [9.78, 7.29, 6.16]
        else:
            cv = [9.72, 7.25, 6.11]
    
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
        frequency=k,
        lags=p
    )
