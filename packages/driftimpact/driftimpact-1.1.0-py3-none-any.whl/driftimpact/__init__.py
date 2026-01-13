"""
DriftImpact - Data and Concept Drift Detection Library

This library provides comprehensive tools for detecting data drift and concept drift 
in machine learning models.

Modules:
---------
1. drift_detection: Data drift detection (KS, Mann-Whitney, Levene, Chi-Square tests)
2. concept_drift: Concept drift detection (Feature-Target relationship change)
3. analyzer: Unified analysis class (DriftAnalyzer)
4. drift_visualization: Data drift visualization
5. concept_drift_visualization: Concept drift visualization
6. metrics: Statistical metrics (TVD, KL, JS Divergence)

Usage:
---------
# Individual modules
from driftimpact import DriftDetector, ConceptDriftDetector

# Unified class
from driftimpact import DriftAnalyzer

analyzer = DriftAnalyzer(target_col='target')
results = analyzer.full_analysis(train_df, score_df)
analyzer.visualize_all(results)
"""

# Data Drift
from .drift_detection import DriftDetector, TemporalDriftDetector

# Concept Drift
from .concept_drift import ConceptDriftDetector

# Unified Analyzer
from .analyzer import DriftAnalyzer

# AI Advisor
from .advisor import DriftAdvisor

# Metrics
from .metrics import calculate_tvd, calculate_kl_divergence, calculate_js_divergence

# Visualizations
from .drift_visualization import (
    plot_drift_heatmap,
    plot_pvalue_bars,
    plot_temporal_drift,
    plot_temporal_heatmap,
    create_drift_dashboard
)

from .concept_drift_visualization import (
    plot_correlation_comparison,
    plot_relationship_change,
    plot_temporal_correlation,
    plot_concept_drift_heatmap,
    plot_pvalue_significance,
    create_concept_drift_dashboard
)

__version__ = "1.1.0"
__author__ = "Serkan Arslan"

__all__ = [
    # Classes
    "DriftDetector",
    "TemporalDriftDetector", 
    "ConceptDriftDetector",
    "DriftAnalyzer",
    "DriftAdvisor",
    
    # Metrics
    "calculate_tvd",
    "calculate_kl_divergence",
    "calculate_js_divergence",
    
    # Data Drift Visualization
    "plot_drift_heatmap",
    "plot_pvalue_bars",
    "plot_temporal_drift",
    "plot_temporal_heatmap",
    "create_drift_dashboard",
    
    # Concept Drift Visualization
    "plot_correlation_comparison",
    "plot_relationship_change",
    "plot_temporal_correlation",
    "plot_concept_drift_heatmap",
    "plot_pvalue_significance",
    "create_concept_drift_dashboard"
]
