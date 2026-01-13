"""
Visualization Example: Interactive Plots with Plotly
=====================================================

This example demonstrates all visualization functions available in funitroot package.

Author: Dr. Merwan Roudane
"""

import numpy as np
import sys
sys.path.insert(0, '..')

from funitroot import (
    fourier_adf_test,
    fourier_kpss_test,
    plot_series_with_fourier,
    plot_test_results,
    plot_frequency_search,
    plot_comparative_analysis,
    plot_residual_diagnostics
)

print("=" * 70)
print("FOURIER UNIT ROOT TESTS - VISUALIZATION EXAMPLES")
print("=" * 70)

# Generate interesting data with multiple breaks
np.random.seed(42)
T = 300
t = np.arange(T)

# Create series with two breaks and trend
y = np.zeros(T)
for i in range(T):
    if i < 100:
        y[i] = 5 + 0.02 * i + 0.5 * np.sin(2 * np.pi * i / 50) + np.random.randn() * 0.3
    elif i < 200:
        y[i] = 8 + 0.02 * i + 0.5 * np.sin(2 * np.pi * i / 50) + np.random.randn() * 0.3
    else:
        y[i] = 11 + 0.02 * i + 0.5 * np.sin(2 * np.pi * i / 50) + np.random.randn() * 0.3

print("\n1. Running Fourier ADF Test...")
adf_result = fourier_adf_test(y, model='ct', max_freq=5, ic='aic')
print(f"   Test Statistic: {adf_result.statistic:.4f}")
print(f"   Optimal Frequency: k={adf_result.optimal_frequency}")
print(f"   Decision: {'Stationary' if adf_result.reject_null else 'Unit Root'}")

print("\n2. Running Fourier KPSS Test...")
kpss_result = fourier_kpss_test(y, model='ct', max_freq=5)
print(f"   Test Statistic: {kpss_result.statistic:.6f}")
print(f"   Optimal Frequency: k={kpss_result.optimal_frequency}")
print(f"   Decision: {'Stationary' if not kpss_result.reject_null else 'Unit Root'}")

print("\n" + "=" * 70)
print("GENERATING VISUALIZATIONS")
print("=" * 70)

# 1. Plot series with fitted Fourier components
print("\n1. Series with Fitted Fourier Components")
fig1 = plot_series_with_fourier(
    y,
    optimal_frequency=adf_result.optimal_frequency,
    model='ct',
    title="Time Series with Fourier Components (k={})".format(adf_result.optimal_frequency),
    show=False  # Set to True to display immediately
)
fig1.write_html('/mnt/user-data/outputs/fourier_series_fit.html')
print("   → Saved to: fourier_series_fit.html")

# 2. Plot ADF test results
print("\n2. Fourier ADF Test Results")
fig2 = plot_test_results(adf_result, show=False)
fig2.write_html('/mnt/user-data/outputs/fourier_adf_results.html')
print("   → Saved to: fourier_adf_results.html")

# 3. Plot KPSS test results
print("\n3. Fourier KPSS Test Results")
fig3 = plot_test_results(kpss_result, show=False)
fig3.write_html('/mnt/user-data/outputs/fourier_kpss_results.html')
print("   → Saved to: fourier_kpss_results.html")

# 4. Frequency search for ADF
print("\n4. Frequency Search - ADF")
fig4 = plot_frequency_search(
    y,
    model='ct',
    max_freq=5,
    test_type='adf',
    show=False
)
fig4.write_html('/mnt/user-data/outputs/fourier_adf_frequency_search.html')
print("   → Saved to: fourier_adf_frequency_search.html")

# 5. Frequency search for KPSS
print("\n5. Frequency Search - KPSS")
fig5 = plot_frequency_search(
    y,
    model='ct',
    max_freq=5,
    test_type='kpss',
    show=False
)
fig5.write_html('/mnt/user-data/outputs/fourier_kpss_frequency_search.html')
print("   → Saved to: fourier_kpss_frequency_search.html")

# 6. Comparative analysis
print("\n6. Comparative Analysis (ADF vs KPSS)")
fig6 = plot_comparative_analysis(
    y,
    model='ct',
    max_freq=5,
    show=False
)
fig6.write_html('/mnt/user-data/outputs/fourier_comparative_analysis.html')
print("   → Saved to: fourier_comparative_analysis.html")

# 7. Residual diagnostics for ADF
print("\n7. Residual Diagnostics - ADF")
fig7 = plot_residual_diagnostics(adf_result, show=False)
fig7.write_html('/mnt/user-data/outputs/fourier_adf_diagnostics.html')
print("   → Saved to: fourier_adf_diagnostics.html")

# 8. Residual diagnostics for KPSS
print("\n8. Residual Diagnostics - KPSS")
fig8 = plot_residual_diagnostics(kpss_result, show=False)
fig8.write_html('/mnt/user-data/outputs/fourier_kpss_diagnostics.html')
print("   → Saved to: fourier_kpss_diagnostics.html")

print("\n" + "=" * 70)
print("ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
print("=" * 70)
print("\nFiles saved to /mnt/user-data/outputs/:")
print("  1. fourier_series_fit.html")
print("  2. fourier_adf_results.html")
print("  3. fourier_kpss_results.html")
print("  4. fourier_adf_frequency_search.html")
print("  5. fourier_kpss_frequency_search.html")
print("  6. fourier_comparative_analysis.html")
print("  7. fourier_adf_diagnostics.html")
print("  8. fourier_kpss_diagnostics.html")
print("\nOpen these HTML files in your browser to view interactive plots!")
print("=" * 70)
