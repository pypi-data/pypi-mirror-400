"""
Comprehensive Examples for funitroot Package (v1.0.2)
=====================================================

This script demonstrates all features of the funitroot package:
- Fourier ADF test for unit roots
- Fourier KPSS test for stationarity  
- F-tests for linearity (testing significance of Fourier terms)
- Proper interpretation of results

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
"""

import numpy as np
import pandas as pd
from funitroot import (
    FourierADF, FourierKPSS,
    fourier_adf_test, fourier_kpss_test,
    fourier_adf_f_test, fourier_kpss_f_test
)


def example_1_basic_usage():
    """
    Example 1: Basic Usage of Fourier ADF and KPSS Tests
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Usage")
    print("="*70)
    
    # Generate stationary series with smooth structural break
    np.random.seed(42)
    T = 200
    t = np.arange(T)
    
    # Stationary series with Fourier component (smooth mean shift)
    y = 5 + 3 * np.sin(2 * np.pi * t / T) + np.random.randn(T) * 0.5
    
    # Fourier ADF Test
    print("\n[1.1] Fourier ADF Test")
    print("-" * 50)
    adf_result = fourier_adf_test(y, model='c', max_freq=5)
    print(adf_result.summary())
    
    # Fourier KPSS Test
    print("\n[1.2] Fourier KPSS Test")
    print("-" * 50)
    kpss_result = fourier_kpss_test(y, model='c', max_freq=5)
    print(kpss_result.summary())
    
    # Interpretation
    print("\n[1.3] Interpretation")
    print("-" * 50)
    print(f"ADF: {'Reject' if adf_result.reject_null else 'Fail to reject'} unit root (p={adf_result.pvalue:.4f})")
    print(f"KPSS: {'Reject' if kpss_result.reject_null else 'Fail to reject'} stationarity (p={kpss_result.pvalue:.4f})")
    
    if adf_result.reject_null and not kpss_result.reject_null:
        print("→ Both tests agree: Series is STATIONARY")
    elif not adf_result.reject_null and kpss_result.reject_null:
        print("→ Both tests agree: Series has UNIT ROOT")


def example_2_f_test_for_linearity():
    """
    Example 2: F-test for Linearity
    
    The F-test determines whether Fourier terms are statistically significant.
    If not significant, you should use standard ADF/KPSS tests instead.
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: F-test for Linearity")
    print("="*70)
    
    np.random.seed(123)
    T = 200
    t = np.arange(T)
    
    # Case A: Series WITH significant Fourier component
    print("\n[2.1] Series with Significant Fourier Component")
    print("-" * 50)
    y_fourier = 5 + 4 * np.sin(2 * np.pi * t / T) + np.random.randn(T) * 0.5
    
    adf_result = fourier_adf_test(y_fourier, model='c', max_freq=3)
    f_result = adf_result.f_test_linearity()
    
    print(f"F-statistic: {f_result.f_statistic:.4f}")
    print(f"Critical values: 1%={f_result.critical_values['1%']:.2f}, "
          f"5%={f_result.critical_values['5%']:.2f}, "
          f"10%={f_result.critical_values['10%']:.2f}")
    print(f"P-value: {f_result.pvalue:.4f}")
    print(f"Reject linearity: {f_result.reject_null}")
    
    if f_result.reject_null:
        print("→ Fourier terms ARE significant. Use Fourier ADF test.")
    else:
        print("→ Fourier terms NOT significant. Use standard ADF test.")
    
    # Case B: Series WITHOUT significant Fourier component (random walk)
    print("\n[2.2] Series without Significant Fourier Component")
    print("-" * 50)
    y_rw = np.cumsum(np.random.randn(T))
    
    adf_result_rw = fourier_adf_test(y_rw, model='c', max_freq=3)
    f_result_rw = adf_result_rw.f_test_linearity()
    
    print(f"F-statistic: {f_result_rw.f_statistic:.4f}")
    print(f"P-value: {f_result_rw.pvalue:.4f}")
    print(f"Reject linearity: {f_result_rw.reject_null}")
    
    if not f_result_rw.reject_null:
        print("→ Fourier terms NOT significant. Use standard ADF test.")


def example_3_standalone_f_test():
    """
    Example 3: Standalone F-test Functions
    
    You can test specific frequencies without running the full test.
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Standalone F-test Functions")
    print("="*70)
    
    np.random.seed(42)
    T = 200
    t = np.arange(T)
    y = 5 + 3 * np.sin(2 * np.pi * t / T) + np.random.randn(T) * 0.5
    
    print("\n[3.1] Testing Different Frequencies (Fourier ADF F-test)")
    print("-" * 50)
    
    for k in range(1, 4):
        f_result = fourier_adf_f_test(y, model='c', k=k, p=4)
        print(f"k={k}: F-stat={f_result.f_statistic:8.4f}, p-value={f_result.pvalue:.4f}, "
              f"Significant: {f_result.reject_null}")
    
    print("\n[3.2] Fourier KPSS F-test")
    print("-" * 50)
    
    for k in range(1, 4):
        f_result = fourier_kpss_f_test(y, model='c', k=k)
        print(f"k={k}: F-stat={f_result.f_statistic:8.4f}, p-value={f_result.pvalue:.4f}, "
              f"Significant: {f_result.reject_null}")


def example_4_pvalue_extrapolation():
    """
    Example 4: P-value Extrapolation
    
    Demonstrates that p-values now properly extrapolate beyond 10% bounds.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: P-value Extrapolation")
    print("="*70)
    
    np.random.seed(42)
    T = 200
    t = np.arange(T)
    
    # Unit root series (should give p-value > 0.10)
    print("\n[4.1] Unit Root Series (Random Walk)")
    print("-" * 50)
    y_ur = np.cumsum(np.random.randn(T))
    result_ur = fourier_adf_test(y_ur, model='c', max_freq=3)
    print(f"ADF statistic: {result_ur.statistic:.4f}")
    print(f"P-value: {result_ur.pvalue:.4f}")
    print("Note: P-value > 0.10 demonstrates proper extrapolation beyond bounds")
    
    # Strongly stationary series (should give p-value < 0.01)
    print("\n[4.2] Strongly Stationary Series")
    print("-" * 50)
    y_stat = np.random.randn(T) * 0.1  # White noise
    result_stat = fourier_adf_test(y_stat, model='c', max_freq=3)
    print(f"ADF statistic: {result_stat.statistic:.4f}")
    print(f"P-value: {result_stat.pvalue:.4f}")
    print("Note: P-value < 0.01 demonstrates proper extrapolation beyond bounds")


def example_5_model_comparison():
    """
    Example 5: Comparing Constant vs. Constant+Trend Models
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Model Comparison (Constant vs. Constant+Trend)")
    print("="*70)
    
    np.random.seed(42)
    T = 200
    t = np.arange(T)
    
    # Trend stationary series
    y = 5 + 0.05 * t + 2 * np.sin(2 * np.pi * t / T) + np.random.randn(T) * 0.5
    
    # Model: Constant only
    print("\n[5.1] Model: Constant Only (model='c')")
    print("-" * 50)
    result_c = fourier_adf_test(y, model='c', max_freq=3)
    print(f"ADF statistic: {result_c.statistic:.4f}")
    print(f"P-value: {result_c.pvalue:.4f}")
    print(f"Reject unit root: {result_c.reject_null}")
    
    # Model: Constant + Trend
    print("\n[5.2] Model: Constant + Trend (model='ct')")
    print("-" * 50)
    result_ct = fourier_adf_test(y, model='ct', max_freq=3)
    print(f"ADF statistic: {result_ct.statistic:.4f}")
    print(f"P-value: {result_ct.pvalue:.4f}")
    print(f"Reject unit root: {result_ct.reject_null}")
    
    print("\n[5.3] Interpretation")
    print("-" * 50)
    print("For trend-stationary data, model='ct' is more appropriate.")
    print("Critical values are more negative for 'ct' model.")


def example_6_complete_workflow():
    """
    Example 6: Complete Analysis Workflow
    
    Demonstrates the recommended workflow for unit root testing with Fourier terms.
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Complete Analysis Workflow")
    print("="*70)
    
    np.random.seed(42)
    T = 200
    t = np.arange(T)
    
    # Generate test data
    y = 5 + 3 * np.sin(2 * np.pi * t / T) + np.random.randn(T) * 0.5
    
    print("\n[Step 1] Run Fourier ADF Test")
    print("-" * 50)
    adf_result = fourier_adf_test(y, model='c', max_freq=5, ic='aic')
    print(f"Optimal frequency k = {adf_result.optimal_frequency}")
    print(f"Optimal lag p = {adf_result.optimal_lag}")
    print(f"ADF statistic = {adf_result.statistic:.4f}")
    print(f"P-value = {adf_result.pvalue:.4f}")
    
    print("\n[Step 2] Check F-test for Linearity")
    print("-" * 50)
    f_result = adf_result.f_test_linearity()
    print(f"F-statistic = {f_result.f_statistic:.4f}")
    print(f"P-value = {f_result.pvalue:.4f}")
    
    if f_result.reject_null:
        print("→ Fourier terms are SIGNIFICANT")
        print("  Proceed with Fourier ADF results")
    else:
        print("→ Fourier terms are NOT significant")
        print("  Consider using standard ADF test instead")
    
    print("\n[Step 3] Run Fourier KPSS for Confirmation")
    print("-" * 50)
    kpss_result = fourier_kpss_test(y, model='c', max_freq=5)
    print(f"KPSS statistic = {kpss_result.statistic:.6f}")
    print(f"P-value = {kpss_result.pvalue:.4f}")
    
    print("\n[Step 4] Joint Interpretation")
    print("-" * 50)
    print(f"ADF: {'Reject' if adf_result.reject_null else 'Fail to reject'} unit root")
    print(f"KPSS: {'Reject' if kpss_result.reject_null else 'Fail to reject'} stationarity")
    
    if adf_result.reject_null and not kpss_result.reject_null:
        conclusion = "STATIONARY around Fourier components"
    elif not adf_result.reject_null and kpss_result.reject_null:
        conclusion = "HAS UNIT ROOT"
    elif not adf_result.reject_null and not kpss_result.reject_null:
        conclusion = "INCONCLUSIVE (low power or misspecification)"
    else:
        conclusion = "CONTRADICTORY (needs further analysis)"
    
    print(f"\n→ Final Conclusion: Series {conclusion}")


def example_7_different_ic_criteria():
    """
    Example 7: Different Information Criteria for Lag Selection
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: Lag Selection Criteria Comparison")
    print("="*70)
    
    np.random.seed(42)
    T = 200
    t = np.arange(T)
    y = 5 + 3 * np.sin(2 * np.pi * t / T) + np.random.randn(T) * 0.5
    
    criteria = ['aic', 'bic', 'tstat']
    
    for ic in criteria:
        result = fourier_adf_test(y, model='c', max_freq=3, ic=ic)
        print(f"\n[{ic.upper()}] Optimal lag p = {result.optimal_lag}, "
              f"k = {result.optimal_frequency}, "
              f"stat = {result.statistic:.4f}")


if __name__ == "__main__":
    print("="*70)
    print("funitroot Package v1.0.2 - Comprehensive Examples")
    print("Fourier ADF & KPSS Tests with F-tests for Linearity")
    print("="*70)
    
    example_1_basic_usage()
    example_2_f_test_for_linearity()
    example_3_standalone_f_test()
    example_4_pvalue_extrapolation()
    example_5_model_comparison()
    example_6_complete_workflow()
    example_7_different_ic_criteria()
    
    print("\n" + "="*70)
    print("All examples completed successfully!")
    print("="*70)
