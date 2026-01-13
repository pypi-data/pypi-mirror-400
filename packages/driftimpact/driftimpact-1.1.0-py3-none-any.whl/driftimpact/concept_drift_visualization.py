"""
Concept Drift Visualization Module

This module contains functions for visualizing outputs from concept_drift.py.

Charts:
1. plot_correlation_comparison(): Train vs Score/Actuals correlation comparison
2. plot_relationship_change(): Feature-Target relationship change (bar chart)
3. plot_temporal_correlation(): Temporal correlation change (line chart)
4. plot_concept_drift_heatmap(): Concept drift heatmap
5. create_concept_drift_dashboard(): Dashboard combining all charts
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


def plot_correlation_comparison(
    concept_results: pd.DataFrame,
    title: str = "Feature-Target Correlation: Train vs Score",
    figsize: tuple = (12, 6),
    save_path: str = None
) -> plt.Figure:
    """
    Compares correlation values between Train and Score/Actuals.
    
    Parameters:
    -----------
    concept_results : pd.DataFrame
        Output of ConceptDriftDetector.run_analysis() or analyze_with_actuals()
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
    
    # Get only correlation-based results
    corr_results = concept_results[concept_results['Method'].str.contains('Correlation|Fisher', case=False, na=False)]
    
    if len(corr_results) == 0:
        ax.text(0.5, 0.5, 'No correlation data available', ha='center', va='center', fontsize=14)
        return fig
    
    features = corr_results['Feature'].values
    
    # Get Train and Score metrics
    train_col = 'Train_Metric'
    score_col = 'Score_Metric' if 'Score_Metric' in corr_results.columns else 'Actuals_Metric'
    
    train_corr = corr_results[train_col].values
    score_corr = corr_results[score_col].values
    drift_detected = corr_results['Drift_Detected'].values
    
    x = np.arange(len(features))
    width = 0.35
    
    # Draw bars
    bars1 = ax.bar(x - width/2, train_corr, width, label='Train', color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, score_corr, width, label='Score/Actuals', color='#e74c3c', alpha=0.8)
    
    # Emphasize features with drift
    for i, (bar1, bar2, drift) in enumerate(zip(bars1, bars2, drift_detected)):
        if drift:
            bar1.set_edgecolor('red')
            bar1.set_linewidth(2)
            bar2.set_edgecolor('red')
            bar2.set_linewidth(2)
            # Add warning icon
            max_val = max(abs(train_corr[i]), abs(score_corr[i]))
            ax.annotate('⚠️', xy=(i, max_val + 0.05), ha='center', fontsize=12)
    
    # Axis settings
    ax.set_xlabel('Features', fontsize=12)
    ax.set_ylabel('Correlation Coefficient (r)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(features, rotation=45, ha='right')
    ax.legend()
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    ax.set_ylim(-1.1, 1.1)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Chart saved: {save_path}")
    
    return fig


def plot_relationship_change(
    concept_results: pd.DataFrame,
    title: str = "Feature-Target Relationship Change",
    figsize: tuple = (12, 6),
    save_path: str = None
) -> plt.Figure:
    """
    Shows the change (difference) in Feature-Target relationship as a bar chart.
    
    Parameters:
    -----------
    concept_results : pd.DataFrame
        Output of ConceptDriftDetector
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
    
    features = concept_results['Feature'].values
    
    # Calculate metric change
    train_col = 'Train_Metric'
    score_col = 'Score_Metric' if 'Score_Metric' in concept_results.columns else 'Actuals_Metric'
    if score_col not in concept_results.columns:
        score_col = 'Curr_Period_Metric'
        train_col = 'Prev_Period_Metric'
    
    changes = concept_results[score_col].values - concept_results[train_col].values
    drift_detected = concept_results['Drift_Detected'].values
    
    # Determine colors (positive=green, negative=red)
    colors = ['#27ae60' if c >= 0 else '#c0392b' for c in changes]
    
    # Show bars with drift differently
    edge_colors = ['red' if d else 'none' for d in drift_detected]
    linewidths = [3 if d else 0 for d in drift_detected]
    
    bars = ax.bar(features, changes, color=colors, edgecolor=edge_colors, linewidth=linewidths, alpha=0.8)
    
    # Axis settings
    ax.set_xlabel('Features', fontsize=12)
    ax.set_ylabel('Relationship Change (Δ)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    plt.xticks(rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#27ae60', label='Increased'),
        mpatches.Patch(facecolor='#c0392b', label='Decreased'),
        mpatches.Patch(facecolor='white', edgecolor='red', linewidth=2, label='Drift Detected')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Chart saved: {save_path}")
    
    return fig


def plot_temporal_correlation(
    temporal_results: pd.DataFrame,
    title: str = "Temporal Correlation Change",
    figsize: tuple = (14, 6),
    save_path: str = None
) -> plt.Figure:
    """
    Shows temporal correlation change as a line chart.
    (For output of analyze_within_train())
    
    Parameters:
    -----------
    temporal_results : pd.DataFrame
        Output of ConceptDriftDetector.analyze_within_train()
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
    
    # Get only correlation-based results
    corr_results = temporal_results[temporal_results['Method'].str.contains('Fisher|Correlation', case=False, na=False)]
    
    if len(corr_results) == 0:
        ax.text(0.5, 0.5, 'No temporal correlation data available', ha='center', va='center', fontsize=14)
        return fig
    
    features = corr_results['Feature'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(features)))
    
    for i, feature in enumerate(features):
        feat_data = corr_results[corr_results['Feature'] == feature].sort_values('Period')
        
        periods = feat_data['Period'].values
        curr_corr = feat_data['Curr_Period_Metric'].values
        
        # Draw line
        ax.plot(periods, curr_corr, marker='o', linewidth=2, markersize=8,
               label=feature, color=colors[i])
        
        # Emphasize drift points
        drift_points = feat_data[feat_data['Drift_Detected'] == True]
        if len(drift_points) > 0:
            ax.scatter(drift_points['Period'], drift_points['Curr_Period_Metric'],
                      s=200, facecolors='none', edgecolors='red', linewidths=3, zorder=5)
    
    # Axis settings
    ax.set_xlabel('Period', fontsize=12)
    ax.set_ylabel('Correlation Coefficient (r)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    ax.set_ylim(-1.1, 1.1)
    ax.grid(alpha=0.3)
    
    # X-axis integer
    ax.set_xticks(corr_results['Period'].unique())
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Chart saved: {save_path}")
    
    return fig


def plot_concept_drift_heatmap(
    concept_results: pd.DataFrame,
    title: str = "Concept Drift Detection Heatmap",
    figsize: tuple = (10, 6),
    save_path: str = None
) -> plt.Figure:
    """
    Shows concept drift results as a heatmap.
    
    Parameters:
    -----------
    concept_results : pd.DataFrame
        Output of ConceptDriftDetector
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
    
    # If temporal data (contains Period column)
    if 'Period' in concept_results.columns:
        pivot_df = concept_results.pivot_table(
            index='Feature',
            columns='Period',
            values='Drift_Detected',
            aggfunc='first'
        ).astype(float)
        xlabel = 'Period'
        col_labels = [f'P{int(p)}' for p in pivot_df.columns]
    else:
        # For single comparison
        pivot_df = concept_results.pivot_table(
            index='Feature',
            columns='Method',
            values='Drift_Detected',
            aggfunc='first'
        ).astype(float)
        xlabel = 'Method'
        col_labels = pivot_df.columns.tolist()
    
    # Color map
    cmap = plt.cm.colors.ListedColormap(['#2ecc71', '#e74c3c'])
    
    # Draw heatmap
    im = ax.imshow(pivot_df.values, cmap=cmap, aspect='auto', vmin=0, vmax=1)
    
    # Axis labels
    ax.set_xticks(range(len(pivot_df.columns)))
    ax.set_xticklabels(col_labels, rotation=45, ha='right', fontsize=10)
    ax.set_yticks(range(len(pivot_df.index)))
    ax.set_yticklabels(pivot_df.index, fontsize=10)
    
    # Grid
    ax.set_xticks(np.arange(-.5, len(pivot_df.columns), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(pivot_df.index), 1), minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=2)
    
    # Write cell values
    for i in range(len(pivot_df.index)):
        for j in range(len(pivot_df.columns)):
            val = pivot_df.iloc[i, j]
            if not np.isnan(val):
                text = "DRIFT" if val == 1 else "OK"
                ax.text(j, i, text, ha='center', va='center', 
                       color='white', fontweight='bold', fontsize=9)
    
    # Title
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel('Feature', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#2ecc71', label='Stable'),
        mpatches.Patch(facecolor='#e74c3c', label='Concept Drift')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Chart saved: {save_path}")
    
    return fig


def plot_pvalue_significance(
    concept_results: pd.DataFrame,
    threshold: float = 0.05,
    title: str = "P-Value Significance (Fisher Z-Test)",
    figsize: tuple = (12, 6),
    save_path: str = None
) -> plt.Figure:
    """
    Bar chart showing P-value values.
    
    Parameters:
    -----------
    concept_results : pd.DataFrame
        Output of ConceptDriftDetector
    threshold : float
        Significance threshold
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
    
    # Filter rows with P-value
    pval_results = concept_results[concept_results['P_Value'].notna()]
    
    if len(pval_results) == 0:
        ax.text(0.5, 0.5, 'No P-Value data available', ha='center', va='center', fontsize=14)
        return fig
    
    features = pval_results['Feature'].values
    pvalues = pval_results['P_Value'].values
    drift_detected = pval_results['Drift_Detected'].values
    
    # Determine colors
    colors = ['#e74c3c' if d else '#3498db' for d in drift_detected]
    
    bars = ax.bar(features, pvalues, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # Threshold line
    ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'α = {threshold}')
    
    # Axis settings
    ax.set_xlabel('Features', fontsize=12)
    ax.set_ylabel('P-Value', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    ax.set_ylim(0, min(1.0, pvalues.max() * 1.2))
    ax.grid(axis='y', alpha=0.3)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#3498db', label='No Drift (p ≥ α)'),
        mpatches.Patch(facecolor='#e74c3c', label='Drift Detected (p < α)'),
        plt.Line2D([0], [0], color='red', linestyle='--', linewidth=2, label=f'Threshold (α={threshold})')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Chart saved: {save_path}")
    
    return fig


def create_concept_drift_dashboard(
    analysis_results: pd.DataFrame = None,
    temporal_results: pd.DataFrame = None,
    title: str = "Concept Drift Analysis Dashboard",
    figsize: tuple = (16, 12),
    save_path: str = None
) -> plt.Figure:
    """
    Combines concept drift analyses into a single dashboard.
    
    Parameters:
    -----------
    analysis_results : pd.DataFrame, optional
        Output of run_analysis() or analyze_with_actuals()
    temporal_results : pd.DataFrame, optional
        Output of analyze_within_train()
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
    fig = plt.figure(figsize=figsize)
    fig.suptitle(title, fontsize=16, fontweight='bold', y=1.02)
    
    plot_idx = 1
    n_plots = 4
    
    if analysis_results is not None:
        # 1. Correlation comparison
        ax1 = fig.add_subplot(2, 2, plot_idx)
        _plot_corr_comparison_on_ax(analysis_results, ax1, "Correlation: Train vs Score")
        plot_idx += 1
        
        # 2. Relationship change
        ax2 = fig.add_subplot(2, 2, plot_idx)
        _plot_relationship_change_on_ax(analysis_results, ax2, "Relationship Change")
        plot_idx += 1
    
    if temporal_results is not None:
        # 3. Temporal correlation
        ax3 = fig.add_subplot(2, 2, plot_idx)
        _plot_temporal_corr_on_ax(temporal_results, ax3, "Temporal Correlation")
        plot_idx += 1
        
        # 4. Heatmap
        ax4 = fig.add_subplot(2, 2, plot_idx)
        _plot_concept_heatmap_on_ax(temporal_results, ax4, "Concept Drift Heatmap")
    elif analysis_results is not None:
        # P-value chart
        ax3 = fig.add_subplot(2, 2, plot_idx)
        _plot_pvalue_on_ax(analysis_results, ax3, "P-Value Significance")
        plot_idx += 1
        
        ax4 = fig.add_subplot(2, 2, plot_idx)
        _plot_concept_heatmap_on_ax(analysis_results, ax4, "Concept Drift Summary")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Dashboard saved: {save_path}")
    
    return fig


# ==================== HELPER FUNCTIONS ====================

def _plot_corr_comparison_on_ax(results, ax, title):
    """Helper for correlation comparison plot."""
    corr_results = results[results['Method'].str.contains('Correlation|Fisher', case=False, na=False)]
    
    if len(corr_results) == 0:
        ax.text(0.5, 0.5, 'No data', ha='center', va='center')
        return
    
    features = corr_results['Feature'].values
    train_col = 'Train_Metric'
    score_col = 'Score_Metric' if 'Score_Metric' in corr_results.columns else 'Actuals_Metric'
    
    train_corr = corr_results[train_col].values
    score_corr = corr_results[score_col].values
    
    x = np.arange(len(features))
    width = 0.35
    
    ax.bar(x - width/2, train_corr, width, label='Train', color='#3498db', alpha=0.8)
    ax.bar(x + width/2, score_corr, width, label='Score', color='#e74c3c', alpha=0.8)
    
    ax.set_xticks(x)
    ax.set_xticklabels(features, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Correlation', fontsize=9)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.legend(fontsize=8)
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    ax.grid(axis='y', alpha=0.3)


def _plot_relationship_change_on_ax(results, ax, title):
    """Helper for relationship change plot."""
    train_col = 'Train_Metric'
    score_col = 'Score_Metric' if 'Score_Metric' in results.columns else 'Actuals_Metric'
    
    features = results['Feature'].values
    changes = results[score_col].values - results[train_col].values
    colors = ['#27ae60' if c >= 0 else '#c0392b' for c in changes]
    
    ax.bar(features, changes, color=colors, alpha=0.8)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax.set_xticklabels(features, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Change (Δ)', fontsize=9)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)


def _plot_temporal_corr_on_ax(results, ax, title):
    """Helper for temporal correlation plot."""
    corr_results = results[results['Method'].str.contains('Fisher|Correlation', case=False, na=False)]
    
    if len(corr_results) == 0:
        ax.text(0.5, 0.5, 'No data', ha='center', va='center')
        return
    
    features = corr_results['Feature'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(features)))
    
    for i, feature in enumerate(features):
        feat_data = corr_results[corr_results['Feature'] == feature].sort_values('Period')
        ax.plot(feat_data['Period'], feat_data['Curr_Period_Metric'], 
               marker='o', linewidth=1.5, markersize=5, label=feature, color=colors[i])
    
    ax.set_xlabel('Period', fontsize=9)
    ax.set_ylabel('Correlation', fontsize=9)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.legend(fontsize=7)
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    ax.grid(alpha=0.3)


def _plot_concept_heatmap_on_ax(results, ax, title):
    """Helper for concept drift heatmap."""
    if 'Period' in results.columns:
        pivot_df = results.pivot_table(
            index='Feature', columns='Period', values='Drift_Detected', aggfunc='first'
        ).astype(float)
        col_labels = [f'P{int(p)}' for p in pivot_df.columns]
    else:
        pivot_df = results.pivot_table(
            index='Feature', columns='Method', values='Drift_Detected', aggfunc='first'
        ).astype(float)
        col_labels = [m[:10] for m in pivot_df.columns]
    
    cmap = plt.cm.colors.ListedColormap(['#2ecc71', '#e74c3c'])
    ax.imshow(pivot_df.values, cmap=cmap, aspect='auto', vmin=0, vmax=1)
    
    ax.set_xticks(range(len(pivot_df.columns)))
    ax.set_xticklabels(col_labels, rotation=45, ha='right', fontsize=8)
    ax.set_yticks(range(len(pivot_df.index)))
    ax.set_yticklabels(pivot_df.index, fontsize=8)
    ax.set_title(title, fontsize=11, fontweight='bold')


def _plot_pvalue_on_ax(results, ax, title):
    """Helper for p-value plot."""
    pval_results = results[results['P_Value'].notna()]
    
    if len(pval_results) == 0:
        ax.text(0.5, 0.5, 'No P-Value data', ha='center', va='center')
        return
    
    features = pval_results['Feature'].values
    pvalues = pval_results['P_Value'].values
    drift_detected = pval_results['Drift_Detected'].values
    colors = ['#e74c3c' if d else '#3498db' for d in drift_detected]
    
    ax.bar(features, pvalues, color=colors, alpha=0.8)
    ax.axhline(y=0.05, color='red', linestyle='--', linewidth=1.5)
    ax.set_xticklabels(features, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('P-Value', fontsize=9)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    from concept_drift import ConceptDriftDetector
    
    np.random.seed(42)
    
    print("="*70)
    print("CONCEPT DRIFT VISUALIZATION EXAMPLES")
    print("="*70)
    
    # ----- EXAMPLE DATA: Train vs Score -----
    train = pd.DataFrame({
        'feature_a': np.random.normal(0, 1, 1000),
        'feature_b': np.random.normal(0, 1, 1000),
        'feature_c': np.random.normal(0, 1, 1000),
        'target': np.zeros(1000)
    })
    train['target'] = 3*train['feature_a'] + 2*train['feature_b'] + 0.5*train['feature_c'] + np.random.normal(0, 1, 1000)
    
    score = pd.DataFrame({
        'feature_a': np.random.normal(0, 1, 1000),
        'feature_b': np.random.normal(0, 1, 1000),
        'feature_c': np.random.normal(0, 1, 1000),
        'target': np.zeros(1000)
    })
    # feature_a relationship weakened, feature_b same, feature_c strengthened
    score['target'] = 0.5*score['feature_a'] + 2*score['feature_b'] + 3*score['feature_c'] + np.random.normal(0, 1, 1000)
    
    # Analysis
    detector = ConceptDriftDetector(target_col='target')
    analysis_report = detector.run_analysis(train, score)
    
    print("\n--- Analysis Report ---")
    print(analysis_report.to_markdown(index=False))
    
    # ----- EXAMPLE DATA: Within Train -----
    dates = pd.date_range(start='2023-01-01', periods=1000, freq='D')
    train_temporal = pd.DataFrame({
        'date': dates,
        'feature_x': np.random.normal(0, 1, 1000),
        'feature_y': np.random.normal(0, 1, 1000)
    })
    # Strong relationship in first half, weak relationship in second half
    train_temporal['target'] = np.where(
        train_temporal.index < 500,
        3 * train_temporal['feature_x'] + np.random.normal(0, 1, 1000),
        0.2 * train_temporal['feature_x'] + np.random.normal(0, 1, 1000)
    )
    
    within_train_report = detector.analyze_within_train(
        train_df=train_temporal,
        time_col='date',
        n_periods=4
    )
    
    print("\n--- Within Train Report ---")
    print(within_train_report.to_markdown(index=False))
    
    # ----- CHARTS -----
    print("\n" + "="*70)
    print("GENERATING VISUALIZATIONS...")
    print("="*70)
    
    # 1. Correlation Comparison
    fig1 = plot_correlation_comparison(analysis_report, save_path='concept_correlation_comparison.png')
    
    # 2. Relationship Change
    fig2 = plot_relationship_change(analysis_report, save_path='concept_relationship_change.png')
    
    # 3. P-Value Significance
    fig3 = plot_pvalue_significance(analysis_report, save_path='concept_pvalue.png')
    
    # 4. Temporal Correlation
    fig4 = plot_temporal_correlation(within_train_report, save_path='concept_temporal_correlation.png')
    
    # 5. Heatmap
    fig5 = plot_concept_drift_heatmap(within_train_report, save_path='concept_drift_heatmap.png')
    
    # 6. Dashboard
    fig6 = create_concept_drift_dashboard(
        analysis_results=analysis_report,
        temporal_results=within_train_report,
        save_path='concept_drift_dashboard.png'
    )
    
    print("\nAll charts created!")
    plt.show()
