"""
funitroot: Fourier Unit Root Tests Package
===========================================

A Python package for testing unit roots in time series with structural breaks
using Fourier approximations.

Implements:
- Fourier ADF Test (Enders & Lee, 2012)
- Fourier KPSS Test (Becker, Enders & Lee, 2006)
- F-tests for linearity (testing significance of Fourier terms)

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/funitroot
"""

__version__ = "1.0.2"
__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

from .fourier_adf import (
    FourierADF, 
    fourier_adf_test, 
    fourier_adf_f_test,
    FTestResult as ADFFTestResult
)
from .fourier_kpss import (
    FourierKPSS, 
    fourier_kpss_test, 
    fourier_kpss_f_test,
    FTestResult as KPSSFTestResult
)
from .visualization import (
    plot_series_with_fourier,
    plot_test_results,
    plot_frequency_search,
    plot_comparative_analysis,
    plot_residual_diagnostics
)

__all__ = [
    # Main test classes
    'FourierADF',
    'FourierKPSS',
    # Convenience functions
    'fourier_adf_test',
    'fourier_kpss_test',
    # F-test functions for linearity
    'fourier_adf_f_test',
    'fourier_kpss_f_test',
    # Result containers
    'ADFFTestResult',
    'KPSSFTestResult',
    # Visualization functions
    'plot_series_with_fourier',
    'plot_test_results',
    'plot_frequency_search',
    'plot_comparative_analysis',
    'plot_residual_diagnostics'
]
