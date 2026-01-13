"""
Drift Detection Visualization Module

This module contains functions for visualizing outputs from drift_detection.py.

Charts:
1. plot_drift_heatmap(): Variable x Test matrix (Drift exists/not)
2. plot_pvalue_bars(): P-value bar chart (with threshold)
3. plot_temporal_drift(): Temporal drift line chart
4. plot_temporal_heatmap(): Temporal drift heatmap
5. create_drift_dashboard(): Dashboard combining all charts
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Optional, List
import warnings
warnings.filterwarnings('ignore')

# For character support
plt.rcParams['font.family'] = 'DejaVu Sans'


def plot_drift_heatmap(
    drift_results: pd.DataFrame,
    title: str = "Data Drift Heatmap",
    figsize: tuple = (12, 8),
    save_path: str = None
) -> plt.Figure:
    """
    Shows drift results as a heatmap.
    
    Parameters:
    -----------
    drift_results : pd.DataFrame
        Output of DriftDetector.run_tests()
    title : str
        Chart title
    figsize : tuple
        Chart size
    save_path : str, optional
        File path to save
    
    Returns:
    --------
    plt.Figure: Matplotlib figure object
    """
    # Create pivot table: Rows=Column, Columns=Test, Values=Drift Detected
    pivot_df = drift_results.pivot_table(
        index='Column', 
        columns='Test', 
        values='Drift Detected',
        aggfunc='first'
    ).astype(float)
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Color map: Green=No Drift, Red=Drift
    cmap = plt.cm.colors.ListedColormap(['#2ecc71', '#e74c3c'])  # Green, Red
    
    # Draw heatmap
    im = ax.imshow(pivot_df.values, cmap=cmap, aspect='auto', vmin=0, vmax=1)
    
    # Axis labels
    ax.set_xticks(range(len(pivot_df.columns)))
    ax.set_xticklabels(pivot_df.columns, rotation=45, ha='right', fontsize=10)
    ax.set_yticks(range(len(pivot_df.index)))
    ax.set_yticklabels(pivot_df.index, fontsize=10)
    
    # Grid lines
    ax.set_xticks(np.arange(-.5, len(pivot_df.columns), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(pivot_df.index), 1), minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=2)
    
    # Write cell values
    for i in range(len(pivot_df.index)):
        for j in range(len(pivot_df.columns)):
            val = pivot_df.iloc[i, j]
            if not np.isnan(val):
                text = "DRIFT" if val == 1 else "OK"
                color = 'white' if val == 1 else 'white'
                ax.text(j, i, text, ha='center', va='center', 
                       color=color, fontweight='bold', fontsize=9)
    
    # Title and legend
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#2ecc71', label='No Drift'),
        mpatches.Patch(facecolor='#e74c3c', label='Drift Detected')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Chart saved: {save_path}")
    
    return fig


def plot_pvalue_bars(
    drift_results: pd.DataFrame,
    threshold: float = 0.05,
    title: str = "P-Value by Variable and Test",
    figsize: tuple = (14, 8),
    save_path: str = None
) -> plt.Figure:
    """
    Shows P-value values as a bar chart.
    
    Parameters:
    -----------
    drift_results : pd.DataFrame
        Output of DriftDetector.run_tests()
    threshold : float
        Drift threshold value (default: 0.05)
    title : str
        Chart title
    figsize : tuple
        Chart size
    save_path : str, optional
        File path to save
    
    Returns:
    --------
    plt.Figure: Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Unique variables and tests
    columns = drift_results['Column'].unique()
    tests = drift_results['Test'].unique()
    
    x = np.arange(len(columns))
    width = 0.8 / len(tests)
    
    colors = ['#3498db', '#9b59b6', '#f39c12', '#1abc9c']  # Blue, Purple, Orange, Teal
    
    for i, test in enumerate(tests):
        test_data = drift_results[drift_results['Test'] == test]
        pvalues = []
        for col in columns:
            row = test_data[test_data['Column'] == col]
            if len(row) > 0:
                pvalues.append(row['P-Value'].values[0])
            else:
                pvalues.append(np.nan)
        
        offset = (i - len(tests)/2 + 0.5) * width
        bars = ax.bar(x + offset, pvalues, width, label=test, color=colors[i % len(colors)], alpha=0.8)
        
        # Emphasize bars with drift
        for j, (bar, pval) in enumerate(zip(bars, pvalues)):
            if not np.isnan(pval) and pval < threshold:
                bar.set_edgecolor('red')
                bar.set_linewidth(2)
    
    # Threshold line
    ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold (α={threshold})')
    
    # Axis settings
    ax.set_xlabel('Variables', fontsize=12)
    ax.set_ylabel('P-Value', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(columns, rotation=45, ha='right')
    ax.legend(loc='upper right')
    ax.set_ylim(0, min(1.0, drift_results['P-Value'].max() * 1.2))
    
    # Grid
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Chart saved: {save_path}")
    
    return fig


def plot_temporal_drift(
    temporal_results: pd.DataFrame,
    metric: str = 'P-Value',
    threshold: float = 0.05,
    title: str = "Temporal Drift Analysis",
    figsize: tuple = (14, 6),
    save_path: str = None
) -> plt.Figure:
    """
    Shows temporal drift analysis results as a line chart.
    
    Parameters:
    -----------
    temporal_results : pd.DataFrame
        Output of TemporalDriftDetector.detect_drift_by_time()
    metric : str
        Metric to display ('P-Value' or 'Statistic')
    threshold : float
        Drift threshold value
    title : str
        Chart title
    figsize : tuple
        Chart size
    save_path : str, optional
        File path to save
    
    Returns:
    --------
    plt.Figure: Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Determine time column for X-axis
    time_col = 'Window_Start' if 'Window_Start' in temporal_results.columns else 'Cumulative_End'
    
    # Draw lines for each variable
    columns = temporal_results['Column'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(columns)))
    
    for i, col in enumerate(columns):
        col_data = temporal_results[temporal_results['Column'] == col].sort_values(time_col)
        
        ax.plot(col_data[time_col], col_data[metric], 
               marker='o', linewidth=2, markersize=6,
               label=col, color=colors[i])
        
        # Emphasize drift points
        drift_points = col_data[col_data['Drift_Detected'] == True]
        if len(drift_points) > 0:
            ax.scatter(drift_points[time_col], drift_points[metric], 
                      s=150, facecolors='none', edgecolors='red', linewidths=2, zorder=5)
    
    # Threshold line (only for P-Value)
    if metric == 'P-Value':
        ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, 
                   label=f'Threshold (α={threshold})')
        ax.set_ylim(0, min(1.0, temporal_results[metric].max() * 1.2))
    
    # Axis settings
    ax.set_xlabel('Time Window', fontsize=12)
    ax.set_ylabel(metric, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    
    # X-axis date format
    plt.xticks(rotation=45, ha='right')
    
    # Grid
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Chart saved: {save_path}")
    
    return fig


def plot_temporal_heatmap(
    temporal_results: pd.DataFrame,
    title: str = "Temporal Drift Heatmap",
    figsize: tuple = (14, 8),
    save_path: str = None
) -> plt.Figure:
    """
    Shows temporal drift results as a heatmap.
    
    Parameters:
    -----------
    temporal_results : pd.DataFrame
        Output of TemporalDriftDetector.detect_drift_by_time()
    title : str
        Chart title
    figsize : tuple
        Chart size
    save_path : str, optional
        File path to save
    
    Returns:
    --------
    plt.Figure: Matplotlib figure object
    """
    # Determine time column for X-axis
    time_col = 'Window_Index' if 'Window_Index' in temporal_results.columns else 'Sample_Size'
    
    # Create pivot table
    pivot_df = temporal_results.pivot_table(
        index='Column',
        columns=time_col,
        values='Drift_Detected',
        aggfunc='first'
    ).astype(float)
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Color map
    cmap = plt.cm.colors.ListedColormap(['#2ecc71', '#e74c3c'])
    
    # Draw heatmap
    im = ax.imshow(pivot_df.values, cmap=cmap, aspect='auto', vmin=0, vmax=1)
    
    # Axis labels
    ax.set_xticks(range(len(pivot_df.columns)))
    ax.set_xticklabels([f'W{int(w)}' for w in pivot_df.columns], fontsize=10)
    ax.set_yticks(range(len(pivot_df.index)))
    ax.set_yticklabels(pivot_df.index, fontsize=10)
    
    # Grid
    ax.set_xticks(np.arange(-.5, len(pivot_df.columns), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(pivot_df.index), 1), minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=2)
    
    # Title
    ax.set_xlabel('Time Window', fontsize=12)
    ax.set_ylabel('Variable', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#2ecc71', label='No Drift'),
        mpatches.Patch(facecolor='#e74c3c', label='Drift Detected')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Chart saved: {save_path}")
    
    return fig


def create_drift_dashboard(
    drift_results: pd.DataFrame = None,
    temporal_results: pd.DataFrame = None,
    title: str = "Drift Detection Dashboard",
    figsize: tuple = (16, 12),
    save_path: str = None
) -> plt.Figure:
    """
    Combines all drift analyses into a single dashboard.
    
    Parameters:
    -----------
    drift_results : pd.DataFrame, optional
        Output of DriftDetector.run_tests()
    temporal_results : pd.DataFrame, optional
        Output of TemporalDriftDetector.detect_drift_by_time()
    title : str
        Dashboard title
    figsize : tuple
        Chart size
    save_path : str, optional
        File path to save
    
    Returns:
    --------
    plt.Figure: Matplotlib figure object
    """
    # Determine how many subplots there will be
    n_plots = sum([drift_results is not None, temporal_results is not None]) * 2
    
    if n_plots == 0:
        raise ValueError("At least one results DataFrame must be provided.")
    
    fig = plt.figure(figsize=figsize)
    fig.suptitle(title, fontsize=16, fontweight='bold', y=1.02)
    
    plot_idx = 1
    
    if drift_results is not None:
        # Heatmap
        ax1 = fig.add_subplot(2, 2, plot_idx)
        _plot_heatmap_on_ax(drift_results, ax1, "Data Drift Heatmap")
        plot_idx += 1
        
        # P-Value Bars
        ax2 = fig.add_subplot(2, 2, plot_idx)
        _plot_pvalue_on_ax(drift_results, ax2, "P-Value Distribution")
        plot_idx += 1
    
    if temporal_results is not None:
        # Temporal Line Chart
        ax3 = fig.add_subplot(2, 2, plot_idx)
        _plot_temporal_on_ax(temporal_results, ax3, "Temporal Drift (P-Value)")
        plot_idx += 1
        
        # Temporal Heatmap
        ax4 = fig.add_subplot(2, 2, plot_idx)
        _plot_temporal_heatmap_on_ax(temporal_results, ax4, "Temporal Drift Heatmap")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Dashboard saved: {save_path}")
    
    return fig


# ==================== HELPER FUNCTIONS FOR DASHBOARD ====================

def _plot_heatmap_on_ax(drift_results, ax, title):
    """Helper function to plot heatmap on a given axis."""
    pivot_df = drift_results.pivot_table(
        index='Column', columns='Test', values='Drift Detected', aggfunc='first'
    ).astype(float)
    
    cmap = plt.cm.colors.ListedColormap(['#2ecc71', '#e74c3c'])
    im = ax.imshow(pivot_df.values, cmap=cmap, aspect='auto', vmin=0, vmax=1)
    
    ax.set_xticks(range(len(pivot_df.columns)))
    ax.set_xticklabels(pivot_df.columns, rotation=45, ha='right', fontsize=8)
    ax.set_yticks(range(len(pivot_df.index)))
    ax.set_yticklabels(pivot_df.index, fontsize=8)
    ax.set_title(title, fontsize=11, fontweight='bold')


def _plot_pvalue_on_ax(drift_results, ax, title):
    """Helper function to plot p-value bars on a given axis."""
    columns = drift_results['Column'].unique()
    tests = drift_results['Test'].unique()
    
    x = np.arange(len(columns))
    width = 0.8 / len(tests)
    colors = ['#3498db', '#9b59b6', '#f39c12', '#1abc9c']
    
    for i, test in enumerate(tests):
        test_data = drift_results[drift_results['Test'] == test]
        pvalues = [test_data[test_data['Column'] == col]['P-Value'].values[0] 
                   if len(test_data[test_data['Column'] == col]) > 0 else np.nan 
                   for col in columns]
        offset = (i - len(tests)/2 + 0.5) * width
        ax.bar(x + offset, pvalues, width, label=test, color=colors[i % len(colors)], alpha=0.8)
    
    ax.axhline(y=0.05, color='red', linestyle='--', linewidth=1.5, label='α=0.05')
    ax.set_xticks(x)
    ax.set_xticklabels(columns, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('P-Value', fontsize=9)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(axis='y', alpha=0.3)


def _plot_temporal_on_ax(temporal_results, ax, title):
    """Helper function to plot temporal drift on a given axis."""
    time_col = 'Window_Start' if 'Window_Start' in temporal_results.columns else 'Cumulative_End'
    columns = temporal_results['Column'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(columns)))
    
    for i, col in enumerate(columns):
        col_data = temporal_results[temporal_results['Column'] == col].sort_values(time_col)
        ax.plot(col_data[time_col], col_data['P-Value'], 
               marker='o', linewidth=1.5, markersize=4, label=col, color=colors[i])
    
    ax.axhline(y=0.05, color='red', linestyle='--', linewidth=1.5)
    ax.set_ylabel('P-Value', fontsize=9)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.legend(fontsize=7, loc='upper right')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=7)
    ax.grid(alpha=0.3)


def _plot_temporal_heatmap_on_ax(temporal_results, ax, title):
    """Helper function to plot temporal heatmap on a given axis."""
    time_col = 'Window_Index' if 'Window_Index' in temporal_results.columns else 'Sample_Size'
    
    pivot_df = temporal_results.pivot_table(
        index='Column', columns=time_col, values='Drift_Detected', aggfunc='first'
    ).astype(float)
    
    cmap = plt.cm.colors.ListedColormap(['#2ecc71', '#e74c3c'])
    ax.imshow(pivot_df.values, cmap=cmap, aspect='auto', vmin=0, vmax=1)
    
    ax.set_xticks(range(len(pivot_df.columns)))
    ax.set_xticklabels([f'W{int(w)}' for w in pivot_df.columns], fontsize=8)
    ax.set_yticks(range(len(pivot_df.index)))
    ax.set_yticklabels(pivot_df.index, fontsize=8)
    ax.set_xlabel('Time Window', fontsize=9)
    ax.set_title(title, fontsize=11, fontweight='bold')


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    from drift_detection import DriftDetector, TemporalDriftDetector
    
    np.random.seed(42)
    
    # ----- CREATE EXAMPLE DATA -----
    # Train data
    train = pd.DataFrame({
        'age': np.random.normal(30, 5, 1000),
        'income': np.random.exponential(5000, 1000),
        'score': np.random.uniform(0, 100, 1000),
        'segment': np.random.choice(['A', 'B', 'C'], 1000, p=[0.2, 0.5, 0.3])
    })
    
    # Score data (Drifted)
    score = pd.DataFrame({
        'age': np.random.normal(38, 5, 1000),  # Mean shift
        'income': np.random.exponential(5000, 1000),  # No drift
        'score': np.random.uniform(20, 120, 1000),  # Distribution shift
        'segment': np.random.choice(['A', 'B', 'C'], 1000, p=[0.1, 0.4, 0.5])  # Ratio shift
    })
    
    # ----- DRIFT DETECTION -----
    detector = DriftDetector(threshold=0.05)
    drift_report = detector.run_tests(train, score)
    
    print("="*60)
    print("DRIFT DETECTION RESULTS")
    print("="*60)
    print(drift_report.to_markdown(index=False))
    
    # ----- TEMPORAL DATA -----
    dates = pd.date_range(start='2024-01-01', periods=1000, freq='D')
    
    train_temporal = pd.DataFrame({
        'feature_x': np.random.normal(50, 10, 1000),
        'feature_y': np.random.uniform(0, 100, 1000)
    })
    
    # First half normal, second half drifted
    normal_part = pd.DataFrame({
        'date': dates[:500],
        'feature_x': np.random.normal(50, 10, 500),
        'feature_y': np.random.uniform(0, 100, 500)
    })
    drifted_part = pd.DataFrame({
        'date': dates[500:],
        'feature_x': np.random.normal(70, 10, 500),  # Drift!
        'feature_y': np.random.uniform(0, 100, 500)  # No drift
    })
    score_temporal = pd.concat([normal_part, drifted_part], ignore_index=True)
    
    temporal_detector = TemporalDriftDetector(threshold=0.05)
    temporal_report = temporal_detector.detect_drift_by_time(
        train_df=train_temporal,
        score_df=score_temporal,
        time_col='date',
        method='sliding',
        n_windows=10
    )
    
    print("\n" + "="*60)
    print("TEMPORAL DRIFT RESULTS")
    print("="*60)
    print(temporal_report.to_markdown(index=False))
    
    # ----- CHARTS -----
    print("\n" + "="*60)
    print("GENERATING VISUALIZATIONS...")
    print("="*60)
    
    # 1. Drift Heatmap
    fig1 = plot_drift_heatmap(drift_report, save_path='drift_heatmap.png')
    
    # 2. P-Value Bars
    fig2 = plot_pvalue_bars(drift_report, save_path='pvalue_bars.png')
    
    # 3. Temporal Drift Line Chart
    fig3 = plot_temporal_drift(temporal_report, save_path='temporal_drift_line.png')
    
    # 4. Temporal Drift Heatmap
    fig4 = plot_temporal_heatmap(temporal_report, save_path='temporal_drift_heatmap.png')
    
    # 5. Dashboard
    fig5 = create_drift_dashboard(
        drift_results=drift_report,
        temporal_results=temporal_report,
        save_path='drift_dashboard.png'
    )
    
    print("\nAll charts created!")
    plt.show()
