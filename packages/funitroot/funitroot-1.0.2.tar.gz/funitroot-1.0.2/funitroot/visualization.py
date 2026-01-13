"""
Visualization Module for Fourier Unit Root Tests
Provides interactive plots using Plotly

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/funitroot
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from typing import Union, Optional, List
import warnings


def plot_series_with_fourier(
    data: Union[np.ndarray, pd.Series, list],
    optimal_frequency: int,
    model: str = 'c',
    title: str = "Time Series with Fitted Fourier Components",
    show: bool = True
) -> go.Figure:
    """
    Plot original series with fitted Fourier components.
    
    Parameters
    ----------
    data : array-like
        Time series data
    optimal_frequency : int
        Optimal frequency from test
    model : str
        Model specification ('c' or 'ct')
    title : str
        Plot title
    show : bool
        Whether to display the plot
        
    Returns
    -------
    go.Figure
        Plotly figure object
    """
    # Convert to numpy array
    if isinstance(data, (pd.Series, pd.DataFrame)):
        y = data.values.flatten()
    else:
        y = np.array(data).flatten()
    
    T = len(y)
    t = np.arange(1, T + 1)
    
    # Create Fourier components
    sin_term = np.sin(2 * np.pi * optimal_frequency * t / T)
    cos_term = np.cos(2 * np.pi * optimal_frequency * t / T)
    
    # Fit the model
    if model == 'c':
        X = np.column_stack([np.ones(T), sin_term, cos_term])
    else:
        X = np.column_stack([np.ones(T), t, sin_term, cos_term])
    
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    y_fitted = X @ beta
    residuals = y - y_fitted
    
    # Create figure
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Original Series and Fitted Fourier Components', 'Residuals'),
        vertical_spacing=0.15,
        row_heights=[0.7, 0.3]
    )
    
    # Plot original series
    fig.add_trace(
        go.Scatter(
            x=t, y=y,
            mode='lines',
            name='Original Series',
            line=dict(color='blue', width=1.5),
            opacity=0.7
        ),
        row=1, col=1
    )
    
    # Plot fitted Fourier
    fig.add_trace(
        go.Scatter(
            x=t, y=y_fitted,
            mode='lines',
            name=f'Fitted (k={optimal_frequency})',
            line=dict(color='red', width=2, dash='dash')
        ),
        row=1, col=1
    )
    
    # Plot residuals
    fig.add_trace(
        go.Scatter(
            x=t, y=residuals,
            mode='lines',
            name='Residuals',
            line=dict(color='green', width=1),
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Add zero line for residuals
    fig.add_hline(
        y=0, line_dash="dot", line_color="gray",
        row=2, col=1
    )
    
    # Update layout
    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_yaxes(title_text="Value", row=1, col=1)
    fig.update_yaxes(title_text="Residuals", row=2, col=1)
    
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center'),
        hovermode='x unified',
        height=700,
        showlegend=True,
        legend=dict(x=0.01, y=0.99, xanchor='left', yanchor='top')
    )
    
    if show:
        fig.show()
    
    return fig


def plot_test_results(
    test_result,
    show: bool = True
) -> go.Figure:
    """
    Plot test results with test statistic and critical values.
    
    Parameters
    ----------
    test_result : FourierADF or FourierKPSS
        Test results object
    show : bool
        Whether to display the plot
        
    Returns
    -------
    go.Figure
        Plotly figure object
    """
    # Determine test type
    test_type = type(test_result).__name__
    
    # Get test statistic and critical values
    stat = test_result.statistic
    cv = test_result.critical_values
    
    # Create figure
    fig = go.Figure()
    
    # Add critical values as horizontal lines
    colors = {'10%': 'yellow', '5%': 'orange', '1%': 'red'}
    
    for level, value in sorted(cv.items(), key=lambda x: float(x[0].strip('%'))):
        fig.add_hline(
            y=value,
            line_dash="dash",
            line_color=colors.get(level, 'gray'),
            annotation_text=f"{level} Critical Value: {value:.4f}",
            annotation_position="right"
        )
    
    # Add test statistic
    fig.add_trace(
        go.Scatter(
            x=[test_result.optimal_frequency],
            y=[stat],
            mode='markers',
            name='Test Statistic',
            marker=dict(
                size=15,
                color='blue',
                symbol='diamond',
                line=dict(width=2, color='darkblue')
            ),
            text=[f"Statistic: {stat:.4f}<br>Frequency: {test_result.optimal_frequency}"],
            hovertemplate='%{text}<extra></extra>'
        )
    )
    
    # Determine rejection decision
    if test_type == 'FourierADF':
        reject = stat < cv['5%']
        interpretation = "Reject H₀: Unit Root → Series is Stationary" if reject else "Fail to Reject H₀: Unit Root"
    else:  # FourierKPSS
        reject = stat > cv['5%']
        interpretation = "Reject H₀: Stationarity → Series has Unit Root" if reject else "Fail to Reject H₀: Stationarity"
    
    # Add rejection region annotation
    fig.add_annotation(
        x=test_result.optimal_frequency,
        y=stat,
        text=interpretation,
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="green" if not reject else "red",
        ax=50,
        ay=-50,
        bgcolor="white",
        bordercolor="black",
        borderwidth=2
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f"{test_type} Test Results<br><sub>Optimal Frequency: k={test_result.optimal_frequency}</sub>",
            x=0.5,
            xanchor='center'
        ),
        xaxis_title="Frequency (k)",
        yaxis_title="Test Statistic",
        hovermode='closest',
        height=500,
        showlegend=True
    )
    
    # Set x-axis range
    fig.update_xaxes(range=[0, 6])
    
    if show:
        fig.show()
    
    return fig


def plot_frequency_search(
    data: Union[np.ndarray, pd.Series, list],
    model: str = 'c',
    max_freq: int = 5,
    test_type: str = 'adf',
    show: bool = True
) -> go.Figure:
    """
    Plot test statistics across different frequencies.
    
    Parameters
    ----------
    data : array-like
        Time series data
    model : str
        Model specification ('c' or 'ct')
    max_freq : int
        Maximum frequency to test
    test_type : str
        Test type: 'adf' or 'kpss'
    show : bool
        Whether to display the plot
        
    Returns
    -------
    go.Figure
        Plotly figure object
    """
    from .fourier_adf import FourierADF
    from .fourier_kpss import FourierKPSS
    
    frequencies = list(range(1, max_freq + 1))
    statistics = []
    
    # Compute test statistic for each frequency
    for k in frequencies:
        if test_type.lower() == 'adf':
            result = FourierADF(data, model=model, max_freq=k, max_lag=8)
        else:
            result = FourierKPSS(data, model=model, max_freq=k)
        
        # For frequency search, we manually test at each k
        if test_type.lower() == 'adf':
            _, stat = result._test_at_frequency(k)
        else:
            stat, _ = result._test_at_frequency(k)
        
        statistics.append(stat)
    
    # Find optimal frequency
    if test_type.lower() == 'adf':
        opt_idx = np.argmin(statistics)
    else:
        opt_idx = np.argmin(statistics)
    
    opt_freq = frequencies[opt_idx]
    opt_stat = statistics[opt_idx]
    
    # Create figure
    fig = go.Figure()
    
    # Plot all statistics
    fig.add_trace(
        go.Scatter(
            x=frequencies,
            y=statistics,
            mode='lines+markers',
            name='Test Statistics',
            line=dict(color='blue', width=2),
            marker=dict(size=8, color='blue')
        )
    )
    
    # Highlight optimal frequency
    fig.add_trace(
        go.Scatter(
            x=[opt_freq],
            y=[opt_stat],
            mode='markers',
            name='Optimal Frequency',
            marker=dict(
                size=15,
                color='red',
                symbol='star',
                line=dict(width=2, color='darkred')
            ),
            text=[f"Optimal k={opt_freq}<br>Statistic: {opt_stat:.4f}"],
            hovertemplate='%{text}<extra></extra>'
        )
    )
    
    # Update layout
    test_name = "Fourier ADF" if test_type.lower() == 'adf' else "Fourier KPSS"
    fig.update_layout(
        title=dict(
            text=f"{test_name} Test Statistics Across Frequencies",
            x=0.5,
            xanchor='center'
        ),
        xaxis_title="Frequency (k)",
        yaxis_title="Test Statistic",
        hovermode='x unified',
        height=500,
        showlegend=True
    )
    
    # Set x-axis to show integer ticks
    fig.update_xaxes(dtick=1)
    
    if show:
        fig.show()
    
    return fig


def plot_comparative_analysis(
    data: Union[np.ndarray, pd.Series, list],
    model: str = 'c',
    max_freq: int = 5,
    show: bool = True
) -> go.Figure:
    """
    Comparative plot showing both ADF and KPSS test results.
    
    Parameters
    ----------
    data : array-like
        Time series data
    model : str
        Model specification ('c' or 'ct')
    max_freq : int
        Maximum frequency to test
    show : bool
        Whether to display the plot
        
    Returns
    -------
    go.Figure
        Plotly figure object
    """
    from .fourier_adf import FourierADF
    from .fourier_kpss import FourierKPSS
    
    # Run both tests
    adf_result = FourierADF(data, model=model, max_freq=max_freq)
    kpss_result = FourierKPSS(data, model=model, max_freq=max_freq)
    
    # Create subplot
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Fourier ADF Test', 'Fourier KPSS Test'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # ADF plot
    adf_cv = adf_result.critical_values
    for level, value in adf_cv.items():
        color = {'10%': 'yellow', '5%': 'orange', '1%': 'red'}.get(level, 'gray')
        fig.add_hline(
            y=value,
            line_dash="dash",
            line_color=color,
            annotation_text=f"{level}: {value:.3f}",
            annotation_position="right",
            row=1, col=1
        )
    
    fig.add_trace(
        go.Scatter(
            x=[adf_result.optimal_frequency],
            y=[adf_result.statistic],
            mode='markers',
            name='ADF Statistic',
            marker=dict(size=15, color='blue', symbol='diamond'),
            showlegend=False
        ),
        row=1, col=1
    )
    
    # KPSS plot
    kpss_cv = kpss_result.critical_values
    for level, value in kpss_cv.items():
        color = {'10%': 'yellow', '5%': 'orange', '1%': 'red'}.get(level, 'gray')
        fig.add_hline(
            y=value,
            line_dash="dash",
            line_color=color,
            annotation_text=f"{level}: {value:.3f}",
            annotation_position="right",
            row=1, col=2
        )
    
    fig.add_trace(
        go.Scatter(
            x=[kpss_result.optimal_frequency],
            y=[kpss_result.statistic],
            mode='markers',
            name='KPSS Statistic',
            marker=dict(size=15, color='green', symbol='diamond'),
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Update axes
    fig.update_xaxes(title_text="Frequency (k)", row=1, col=1)
    fig.update_xaxes(title_text="Frequency (k)", row=1, col=2)
    fig.update_yaxes(title_text="Test Statistic", row=1, col=1)
    fig.update_yaxes(title_text="Test Statistic", row=1, col=2)
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="Comparative Fourier Unit Root Test Analysis",
            x=0.5,
            xanchor='center'
        ),
        height=500,
        showlegend=False
    )
    
    # Add decision summary as annotation
    adf_decision = "Stationary" if adf_result.reject_null else "Unit Root"
    kpss_decision = "Stationary" if not kpss_result.reject_null else "Unit Root"
    
    summary_text = (
        f"<b>Test Decisions (5% level):</b><br>"
        f"ADF: {adf_decision} (k={adf_result.optimal_frequency})<br>"
        f"KPSS: {kpss_decision} (k={kpss_result.optimal_frequency})"
    )
    
    if adf_decision == kpss_decision:
        summary_text += "<br><br>✓ <b>Both tests agree!</b>"
        bg_color = "lightgreen"
    else:
        summary_text += "<br><br>⚠ <b>Tests disagree - check for structural breaks</b>"
        bg_color = "lightyellow"
    
    fig.add_annotation(
        text=summary_text,
        xref="paper", yref="paper",
        x=0.5, y=-0.15,
        showarrow=False,
        bgcolor=bg_color,
        bordercolor="black",
        borderwidth=2,
        font=dict(size=12),
        align="left"
    )
    
    if show:
        fig.show()
    
    return fig


def plot_residual_diagnostics(
    test_result,
    show: bool = True
) -> go.Figure:
    """
    Plot residual diagnostics from test.
    
    Parameters
    ----------
    test_result : FourierADF or FourierKPSS
        Test results object with residuals
    show : bool
        Whether to display the plot
        
    Returns
    -------
    go.Figure
        Plotly figure object
    """
    # Get residuals (available from KPSS, need to compute for ADF)
    if hasattr(test_result, 'residuals'):
        residuals = test_result.residuals
    else:
        # Recompute for ADF
        data = test_result.data
        T = len(data)
        t = np.arange(1, T + 1)
        k = test_result.optimal_frequency
        
        sin_term = np.sin(2 * np.pi * k * t / T)
        cos_term = np.cos(2 * np.pi * k * t / T)
        
        if test_result.model == 'c':
            X = np.column_stack([np.ones(T), sin_term, cos_term])
        else:
            X = np.column_stack([np.ones(T), t, sin_term, cos_term])
        
        beta = np.linalg.lstsq(X, data, rcond=None)[0]
        residuals = data - X @ beta
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Residuals Over Time',
            'Residuals Distribution',
            'ACF of Residuals',
            'Q-Q Plot'
        )
    )
    
    t = np.arange(len(residuals))
    
    # Residuals over time
    fig.add_trace(
        go.Scatter(
            x=t, y=residuals,
            mode='lines',
            name='Residuals',
            line=dict(color='blue', width=1)
        ),
        row=1, col=1
    )
    fig.add_hline(y=0, line_dash="dot", line_color="gray", row=1, col=1)
    
    # Histogram
    fig.add_trace(
        go.Histogram(
            x=residuals,
            name='Distribution',
            nbinsx=30,
            marker_color='lightblue',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # ACF
    max_lag = min(40, len(residuals) // 4)
    acf = [np.corrcoef(residuals[:-i or None], residuals[i:])[0, 1] if i > 0 else 1.0 
           for i in range(max_lag)]
    
    fig.add_trace(
        go.Bar(
            x=list(range(max_lag)),
            y=acf,
            name='ACF',
            marker_color='green',
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Confidence interval for ACF
    ci = 1.96 / np.sqrt(len(residuals))
    fig.add_hline(y=ci, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=-ci, line_dash="dash", line_color="red", row=2, col=1)
    
    # Q-Q Plot
    sorted_resid = np.sort(residuals)
    theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, len(residuals)))
    
    fig.add_trace(
        go.Scatter(
            x=theoretical_quantiles,
            y=sorted_resid,
            mode='markers',
            name='Q-Q',
            marker=dict(size=4, color='purple'),
            showlegend=False
        ),
        row=2, col=2
    )
    
    # Add diagonal line
    diag_line = np.linspace(min(theoretical_quantiles), max(theoretical_quantiles), 100)
    fig.add_trace(
        go.Scatter(
            x=diag_line,
            y=diag_line,
            mode='lines',
            line=dict(color='red', dash='dash'),
            showlegend=False
        ),
        row=2, col=2
    )
    
    # Update axes
    fig.update_xaxes(title_text="Time", row=1, col=1)
    fig.update_xaxes(title_text="Residual Value", row=1, col=2)
    fig.update_xaxes(title_text="Lag", row=2, col=1)
    fig.update_xaxes(title_text="Theoretical Quantiles", row=2, col=2)
    
    fig.update_yaxes(title_text="Residuals", row=1, col=1)
    fig.update_yaxes(title_text="Frequency", row=1, col=2)
    fig.update_yaxes(title_text="ACF", row=2, col=1)
    fig.update_yaxes(title_text="Sample Quantiles", row=2, col=2)
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="Residual Diagnostics",
            x=0.5,
            xanchor='center'
        ),
        height=800,
        showlegend=False
    )
    
    if show:
        fig.show()
    
    return fig
