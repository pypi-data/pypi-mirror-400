"""
Basic Example: Fourier ADF and KPSS Tests
==========================================

This example demonstrates the basic usage of both Fourier ADF and Fourier KPSS tests
on simulated data with structural breaks.

Author: Dr. Merwan Roudane
"""

import numpy as np
import sys
sys.path.insert(0, '..')

from funitroot import fourier_adf_test, fourier_kpss_test

# Set random seed for reproducibility
np.random.seed(42)

# Generate time series with structural break
T = 200
t = np.arange(T)
break_point = 100

print("=" * 70)
print("EXAMPLE 1: Stationary Series with Structural Break")
print("=" * 70)

# Stationary series with level shift
y1 = np.zeros(T)
y1[:break_point] = 5 + 0.5 * np.sin(2 * np.pi * t[:break_point] / 50) + np.random.randn(break_point) * 0.5
y1[break_point:] = 8 + 0.5 * np.sin(2 * np.pi * t[break_point:] / 50) + np.random.randn(T - break_point) * 0.5

print("\nFourier ADF Test:")
print("-" * 70)
adf_result1 = fourier_adf_test(y1, model='c', max_freq=3, ic='aic')
print(adf_result1.summary())

print("\nFourier KPSS Test:")
print("-" * 70)
kpss_result1 = fourier_kpss_test(y1, model='c', max_freq=3)
print(kpss_result1.summary())

print("\n" + "=" * 70)
print("EXAMPLE 2: Unit Root Series with Structural Break")
print("=" * 70)

# Random walk with drift and level shift
y2 = np.zeros(T)
innovations = np.random.randn(T) * 0.5
y2[0] = 5
for i in range(1, T):
    if i < break_point:
        y2[i] = y2[i-1] + 0.05 + innovations[i]
    else:
        y2[i] = y2[i-1] + 0.05 + 3 + innovations[i]  # Level shift at break

print("\nFourier ADF Test:")
print("-" * 70)
adf_result2 = fourier_adf_test(y2, model='c', max_freq=3, ic='aic')
print(adf_result2.summary())

print("\nFourier KPSS Test:")
print("-" * 70)
kpss_result2 = fourier_kpss_test(y2, model='c', max_freq=3)
print(kpss_result2.summary())

print("\n" + "=" * 70)
print("EXAMPLE 3: Trend Stationary with Smooth Breaks")
print("=" * 70)

# Trend stationary with smooth transition
y3 = np.zeros(T)
for i in range(T):
    trend = 0.05 * i
    # Smooth transition using logistic function
    smooth_break = 3 / (1 + np.exp(-0.1 * (i - break_point)))
    y3[i] = 5 + trend + smooth_break + np.random.randn() * 0.5

print("\nFourier ADF Test (with trend):")
print("-" * 70)
adf_result3 = fourier_adf_test(y3, model='ct', max_freq=3, ic='aic')
print(adf_result3.summary())

print("\nFourier KPSS Test (with trend):")
print("-" * 70)
kpss_result3 = fourier_kpss_test(y3, model='ct', max_freq=3)
print(kpss_result3.summary())

print("\n" + "=" * 70)
print("SUMMARY OF RESULTS")
print("=" * 70)
print("\nExample 1 (Stationary with break):")
print(f"  ADF: {'Reject H0 → Stationary' if adf_result1.reject_null else 'Fail to Reject H0 → Unit Root'}")
print(f"  KPSS: {'Reject H0 → Unit Root' if kpss_result1.reject_null else 'Fail to Reject H0 → Stationary'}")
print(f"  Agreement: {'YES ✓' if adf_result1.reject_null and not kpss_result1.reject_null else 'NO ✗'}")

print("\nExample 2 (Unit root with break):")
print(f"  ADF: {'Reject H0 → Stationary' if adf_result2.reject_null else 'Fail to Reject H0 → Unit Root'}")
print(f"  KPSS: {'Reject H0 → Unit Root' if kpss_result2.reject_null else 'Fail to Reject H0 → Stationary'}")
print(f"  Agreement: {'YES ✓' if not adf_result2.reject_null and kpss_result2.reject_null else 'NO ✗'}")

print("\nExample 3 (Trend stationary with smooth break):")
print(f"  ADF: {'Reject H0 → Stationary' if adf_result3.reject_null else 'Fail to Reject H0 → Unit Root'}")
print(f"  KPSS: {'Reject H0 → Unit Root' if kpss_result3.reject_null else 'Fail to Reject H0 → Stationary'}")
print(f"  Agreement: {'YES ✓' if adf_result3.reject_null and not kpss_result3.reject_null else 'NO ✗'}")
print("=" * 70)
