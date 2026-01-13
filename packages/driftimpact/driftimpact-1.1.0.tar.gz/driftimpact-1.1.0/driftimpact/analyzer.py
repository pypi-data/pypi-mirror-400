"""
Drift Analyzer - Unified Analysis Class

This module provides a unified interface combining data drift and 
concept drift analyses.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
import os

from .drift_detection import DriftDetector, TemporalDriftDetector
from .concept_drift import ConceptDriftDetector
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


class DriftAnalyzer:
    """
    Main class for performing all drift analyses through a single interface.
    
    This class combines data drift and concept drift analyses and 
    provides a single API for ease of use.
    
    Parameters:
    -----------
    target_col : str, optional
        Target column name (required for concept drift)
    threshold : float
        Statistical significance threshold (default: 0.05)
    
    Example Usage:
    --------------
    >>> from analyzer import DriftAnalyzer
    >>> 
    >>> analyzer = DriftAnalyzer(target_col='churn', threshold=0.05)
    >>> 
    >>> # Full analysis
    >>> results = analyzer.full_analysis(train_df, score_df)
    >>> 
    >>> # Visualize results
    >>> analyzer.visualize_all(results, save_dir='./reports/')
    """
    
    def __init__(self, target_col: str = None, threshold: float = 0.05):
        self.target_col = target_col
        self.threshold = threshold
        
        # Initialize detectors
        self.data_drift_detector = DriftDetector(threshold=threshold)
        self.temporal_drift_detector = TemporalDriftDetector(threshold=threshold)
        
        if target_col:
            self.concept_drift_detector = ConceptDriftDetector(
                target_col=target_col, 
                threshold=threshold
            )
        else:
            self.concept_drift_detector = None
    
    # ==================== DATA DRIFT ====================
    
    def detect_data_drift(
        self, 
        train_df: pd.DataFrame, 
        score_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Detects data drift between Train and Score data.
        
        Returns:
        --------
        pd.DataFrame: Drift results for each variable and test
        """
        return self.data_drift_detector.run_tests(train_df, score_df)
    
    def detect_temporal_drift(
        self,
        train_df: pd.DataFrame,
        score_df: pd.DataFrame,
        time_col: str,
        method: str = 'sliding',
        n_windows: int = 10
    ) -> pd.DataFrame:
        """
        Performs temporal data drift detection.
        
        Returns:
        --------
        pd.DataFrame: Drift results for each time window
        """
        return self.temporal_drift_detector.detect_drift_by_time(
            train_df=train_df,
            score_df=score_df,
            time_col=time_col,
            method=method,
            n_windows=n_windows
        )
    
    def find_first_drift_point(
        self, 
        temporal_results: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Finds the first point where drift was detected.
        """
        return self.temporal_drift_detector.find_first_drift_point(temporal_results)
    
    # ==================== CONCEPT DRIFT ====================
    
    def detect_concept_drift(
        self,
        train_df: pd.DataFrame,
        score_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Detects concept drift between Train and Score data.
        (Target must exist in both datasets)
        
        Returns:
        --------
        pd.DataFrame: Feature-target relationship change results
        """
        if self.concept_drift_detector is None:
            raise ValueError("target_col must be specified for concept drift.")
        
        return self.concept_drift_detector.run_analysis(train_df, score_df)
    
    def detect_concept_drift_within_train(
        self,
        train_df: pd.DataFrame,
        time_col: str,
        n_periods: int = 4
    ) -> pd.DataFrame:
        """
        Temporal concept drift analysis within Train data itself.
        
        Returns:
        --------
        pd.DataFrame: Relationship change results between periods
        """
        if self.concept_drift_detector is None:
            raise ValueError("target_col must be specified for concept drift.")
        
        return self.concept_drift_detector.analyze_within_train(
            train_df=train_df,
            time_col=time_col,
            n_periods=n_periods
        )
    
    def detect_concept_drift_with_actuals(
        self,
        train_df: pd.DataFrame,
        actuals_df: pd.DataFrame,
        time_col: str = None
    ) -> pd.DataFrame:
        """
        Concept drift analysis using actual labels.
        
        Returns:
        --------
        pd.DataFrame: Train vs Actuals relationship change results
        """
        if self.concept_drift_detector is None:
            raise ValueError("target_col must be specified for concept drift.")
        
        return self.concept_drift_detector.analyze_with_actuals(
            train_df=train_df,
            actuals_df=actuals_df,
            time_col=time_col
        )
    
    # ==================== FULL ANALYSIS ====================
    
    def full_analysis(
        self,
        train_df: pd.DataFrame,
        score_df: pd.DataFrame,
        time_col: str = None,
        include_concept_drift: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Runs all drift analyses in one go.
        
        Parameters:
        -----------
        train_df : pd.DataFrame
            Training data
        score_df : pd.DataFrame
            Scoring/prediction data
        time_col : str, optional
            Time column (for temporal analysis)
        include_concept_drift : bool
            Whether to include concept drift analysis
        
        Returns:
        --------
        Dict[str, pd.DataFrame]: All analysis results
            - 'data_drift': Data drift results
            - 'temporal_drift': Temporal drift results (if time_col exists)
            - 'concept_drift': Concept drift results (if target exists)
        """
        results = {}
        
        # 1. Data Drift
        print("📊 Performing Data Drift analysis...")
        results['data_drift'] = self.detect_data_drift(train_df, score_df)
        
        # 2. Temporal Drift
        if time_col and time_col in score_df.columns:
            print("⏰ Performing Temporal Drift analysis...")
            results['temporal_drift'] = self.detect_temporal_drift(
                train_df, score_df, time_col
            )
            results['first_drift_points'] = self.find_first_drift_point(
                results['temporal_drift']
            )
        
        # 3. Concept Drift
        if include_concept_drift and self.concept_drift_detector:
            if self.target_col in train_df.columns and self.target_col in score_df.columns:
                print("🎯 Performing Concept Drift analysis...")
                results['concept_drift'] = self.detect_concept_drift(train_df, score_df)
            elif self.target_col in train_df.columns and time_col:
                print("🎯 Performing Within-Train Concept Drift analysis...")
                results['concept_drift_within_train'] = self.detect_concept_drift_within_train(
                    train_df, time_col
                )
        
        print("✅ Analysis complete!")
        return results
    
    # ==================== PERFORMANCE IMPACT ====================

    def analyze_performance_impact(
        self,
        model,
        score_df: pd.DataFrame,
        y_true: pd.Series,
        time_col: str,
        drift_results: pd.DataFrame = None,
        task_type: str = 'classification'
    ) -> pd.DataFrame:
        """
        Analyzes the relationship between drift and model performance.
        
        Parameters:
        -----------
        model : object
            Trained model (scikit-learn compatible)
        score_df : pd.DataFrame
            Features + time to be scored by the model
        y_true : pd.Series
            Actual target values (same row count as score_df)
        time_col : str
            Time column
        drift_results : pd.DataFrame, optional
            Pre-calculated temporal drift results. 
            If not provided, it is automatically calculated (requires train_df but not present here, so providing it is recommended).
        
        Returns:
        --------
        pd.DataFrame: Performance and drift score by time windows
        """
        from .performance_impact import PerformanceAnalyzer
        
        analyzer = PerformanceAnalyzer(model, task_type=task_type)
        
        # If drift results are not provided, raise error (for now)
        if drift_results is None:
            raise ValueError("Please provide the 'drift_results' (temporal_drift) parameter.")
            
        print("📉 Analyzing model performance impact...")
        
        # Separate time column and remove from features
        # PerformanceAnalyzer should only receive model features
        time_series = score_df[time_col]
        X_features = score_df.drop(columns=[time_col]) if time_col in score_df.columns else score_df
        
        impact_results = analyzer.analyze_impact(
            X_df=X_features,
            y_true=y_true,
            time_col=time_series,
            drift_results=drift_results
        )
        
        return impact_results

    def visualize_performance_impact(
        self,
        impact_results: pd.DataFrame,
        metric_name: str = 'accuracy',
        save_dir: str = None,
        show_plot: bool = True
    ):
        """Visualizes the performance impact analysis."""
        from .performance_impact import PerformanceAnalyzer
        # Dummy instance for plotting
        PA = PerformanceAnalyzer(None)
        
        save_path = f"{save_dir}/performance_impact.png" if save_dir else None
        PA.plot_impact(impact_results, metric_name=metric_name, save_path=save_path, show_plot=show_plot)

    
    # ==================== VISUALIZATION ====================
    
    def visualize_data_drift(
        self,
        drift_results: pd.DataFrame,
        save_dir: str = None
    ) -> None:
        """
        Visualizes data drift results.
        """
        import matplotlib.pyplot as plt
        
        save_path = f"{save_dir}/data_drift_heatmap.png" if save_dir else None
        plot_drift_heatmap(drift_results, save_path=save_path)
        
        save_path = f"{save_dir}/data_drift_pvalues.png" if save_dir else None
        plot_pvalue_bars(drift_results, save_path=save_path)
        
        plt.show()
    
    def visualize_temporal_drift(
        self,
        temporal_results: pd.DataFrame,
        save_dir: str = None
    ) -> None:
        """
        Visualizes temporal drift results.
        """
        import matplotlib.pyplot as plt
        
        save_path = f"{save_dir}/temporal_drift_line.png" if save_dir else None
        plot_temporal_drift(temporal_results, save_path=save_path)
        
        save_path = f"{save_dir}/temporal_drift_heatmap.png" if save_dir else None
        plot_temporal_heatmap(temporal_results, save_path=save_path)
        
        plt.show()
    
    def visualize_concept_drift(
        self,
        concept_results: pd.DataFrame,
        save_dir: str = None
    ) -> None:
        """
        Visualizes concept drift results.
        """
        import matplotlib.pyplot as plt
        
        save_path = f"{save_dir}/concept_correlation.png" if save_dir else None
        plot_correlation_comparison(concept_results, save_path=save_path)
        
        save_path = f"{save_dir}/concept_change.png" if save_dir else None
        plot_relationship_change(concept_results, save_path=save_path)
        
        plt.show()
    
    def visualize_all(
        self,
        results: Dict[str, pd.DataFrame],
        save_dir: str = None
    ) -> None:
        """
        Visualizes all analysis results.
        """
        import matplotlib.pyplot as plt
        
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        
        if 'data_drift' in results:
            print("📈 Creating Data Drift charts...")
            self.visualize_data_drift(results['data_drift'], save_dir)
        
        if 'temporal_drift' in results:
            print("📈 Creating Temporal Drift charts...")
            self.visualize_temporal_drift(results['temporal_drift'], save_dir)
        
        if 'concept_drift' in results:
            print("📈 Creating Concept Drift charts...")
            self.visualize_concept_drift(results['concept_drift'], save_dir)
        
        if 'concept_drift_within_train' in results:
            print("📈 Creating Within-Train Concept Drift charts...")
            save_path = f"{save_dir}/concept_temporal.png" if save_dir else None
            plot_temporal_correlation(results['concept_drift_within_train'], save_path=save_path)
            plt.show()
        
        print("✅ All charts created!")
    
    # ==================== REPORTING ====================
    
    def generate_summary(
        self,
        results: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Creates a summary of all analysis results.
        
        Returns:
        --------
        pd.DataFrame: Drift summary table
        """
        summary_rows = []
        
        if 'data_drift' in results:
            df = results['data_drift']
            drift_count = df['Drift Detected'].sum()
            total_tests = len(df)
            summary_rows.append({
                'Analysis': 'Data Drift',
                'Total Tests': total_tests,
                'Drift Detected': drift_count,
                'Drift Rate': f"{drift_count/total_tests*100:.1f}%"
            })
        
        if 'temporal_drift' in results:
            df = results['temporal_drift']
            drift_count = df['Drift_Detected'].sum()
            total_tests = len(df)
            summary_rows.append({
                'Analysis': 'Temporal Drift',
                'Total Tests': total_tests,
                'Drift Detected': drift_count,
                'Drift Rate': f"{drift_count/total_tests*100:.1f}%"
            })
        
        if 'concept_drift' in results:
            df = results['concept_drift']
            drift_count = df['Drift_Detected'].sum()
            total_tests = len(df)
            summary_rows.append({
                'Analysis': 'Concept Drift',
                'Total Tests': total_tests,
                'Drift Detected': drift_count,
                'Drift Rate': f"{drift_count/total_tests*100:.1f}%"
            })
        
        return pd.DataFrame(summary_rows)

    def generate_alarm_report(
        self,
        results: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Reports how many alarms were produced for each variable.
        
        Returns:
        --------
        pd.DataFrame: Variable-based alarm counts
        """
        alarm_counts = {}

        # 1. Data Drift Alarms
        if 'data_drift' in results:
            df = results['data_drift']
            drifted = df[df['Drift Detected'] == True]
            for col in drifted['Column'].unique():
                count = drifted[drifted['Column'] == col].shape[0]
                alarm_counts[col] = alarm_counts.get(col, 0) + count

        # 2. Temporal Drift Alarms
        if 'temporal_drift' in results:
            df = results['temporal_drift']
            drifted = df[df['Drift_Detected'] == True]
            for col in drifted['Column'].unique():
                count = drifted[drifted['Column'] == col].shape[0]
                alarm_counts[col] = alarm_counts.get(col, 0) + count

        # 3. Concept Drift Alarms
        if 'concept_drift' in results:
            df = results['concept_drift']
            drifted = df[df['Drift_Detected'] == True]
            for feat in drifted['Feature'].unique():
                count = drifted[drifted['Feature'] == feat].shape[0]
                alarm_counts[feat] = alarm_counts.get(feat, 0) + count

        if not alarm_counts:
            return pd.DataFrame(columns=['Variable', 'Total_Alarms'])

        alarm_df = pd.DataFrame([
            {'Variable': k, 'Total_Alarms': v} for k, v in alarm_counts.items()
        ])
        
        return alarm_df.sort_values('Total_Alarms', ascending=False)
    
    def print_report(
        self,
        results: Dict[str, pd.DataFrame],
        save_dir: str = None,
        show_plots: bool = True
    ) -> None:
        """
        Prints drift report to console and creates dashboard.
        
        Parameters:
        -----------
        results : Dict[str, pd.DataFrame]
            Output of full_analysis()
        save_dir : str, optional
            Directory to save charts
        show_plots : bool
            Show charts (default: True)
        """
        import matplotlib.pyplot as plt
        
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        
        print("\n" + "="*70)
        print("📋 DRIFT ANALYSIS REPORT")
        print("="*70)
        
        # Summary
        summary = self.generate_summary(results)
        print("\n📊 SUMMARY:")
        print(summary.to_markdown(index=False))

        # Alarm Report
        alarm_summary = self.generate_alarm_report(results)
        if not alarm_summary.empty:
            print("\n🚨 VARIABLE ALARM SUMMARY:")
            print(alarm_summary.to_markdown(index=False))
        
        # Details
        if 'data_drift' in results:
            print("\n" + "-"*50)
            print("🔍 DATA DRIFT DETAILS:")
            drifted = results['data_drift'][results['data_drift']['Drift Detected'] == True]
            if len(drifted) > 0:
                print(drifted[['Column', 'Test', 'P-Value']].to_markdown(index=False))
            else:
                print("✅ No data drift detected!")
        
        if 'first_drift_points' in results:
            print("\n" + "-"*50)
            print("⏰ FIRST DRIFT POINTS:")
            print(results['first_drift_points'].to_markdown(index=False))
        
        if 'concept_drift' in results:
            print("\n" + "-"*50)
            print("🎯 CONCEPT DRIFT DETAILS:")
            drifted = results['concept_drift'][results['concept_drift']['Drift_Detected'] == True]
            if len(drifted) > 0:
                cols_to_show = ['Feature', 'Method', 'Train_Metric']
                if 'Score_Metric' in drifted.columns:
                    cols_to_show.append('Score_Metric')
                elif 'Actuals_Metric' in drifted.columns:
                    cols_to_show.append('Actuals_Metric')
                cols_to_show.append('P_Value')
                print(drifted[cols_to_show].to_markdown(index=False))
            else:
                print("✅ No concept drift detected!")
        
        print("\n" + "="*70)
        
        # Create charts
        print("\n📈 Creating charts...")
        
        # === DATA DRIFT CHARTS ===
        if 'data_drift' in results:
            # 1. Heatmap
            save_path = f"{save_dir}/data_drift_heatmap.png" if save_dir else None
            plot_drift_heatmap(results['data_drift'], save_path=save_path)
            print(f"   ✅ Data Drift Heatmap {'saved' if save_path else 'created'}")
            
            # 2. P-Value Bars
            save_path = f"{save_dir}/data_drift_pvalues.png" if save_dir else None
            plot_pvalue_bars(results['data_drift'], save_path=save_path)
            print(f"   ✅ P-Value Bar Chart {'saved' if save_path else 'created'}")
        
        # === TEMPORAL DRIFT CHARTS ===
        if 'temporal_drift' in results:
            # 3. Temporal Line Chart
            save_path = f"{save_dir}/temporal_drift_line.png" if save_dir else None
            plot_temporal_drift(results['temporal_drift'], save_path=save_path)
            print(f"   ✅ Temporal Drift Line Chart {'saved' if save_path else 'created'}")
            
            # 4. Temporal Heatmap
            save_path = f"{save_dir}/temporal_drift_heatmap.png" if save_dir else None
            plot_temporal_heatmap(results['temporal_drift'], save_path=save_path)
            print(f"   ✅ Temporal Drift Heatmap {'saved' if save_path else 'created'}")
        
        # === CONCEPT DRIFT CHARTS ===
        if 'concept_drift' in results:
            # 5. Correlation Comparison
            save_path = f"{save_dir}/concept_correlation_comparison.png" if save_dir else None
            plot_correlation_comparison(results['concept_drift'], save_path=save_path)
            print(f"   ✅ Correlation Comparison {'saved' if save_path else 'created'}")
            
            # 6. Relationship Change
            save_path = f"{save_dir}/concept_relationship_change.png" if save_dir else None
            plot_relationship_change(results['concept_drift'], save_path=save_path)
            print(f"   ✅ Relationship Change {'saved' if save_path else 'created'}")
            
            # 7. P-Value Significance
            save_path = f"{save_dir}/concept_pvalue.png" if save_dir else None
            plot_pvalue_significance(results['concept_drift'], save_path=save_path)
            print(f"   ✅ Concept P-Value Chart {'saved' if save_path else 'created'}")
        
        # === WITHIN-TRAIN CONCEPT DRIFT ===
        if 'concept_drift_within_train' in results:
            # 8. Temporal Correlation
            save_path = f"{save_dir}/concept_temporal_correlation.png" if save_dir else None
            plot_temporal_correlation(results['concept_drift_within_train'], save_path=save_path)
            print(f"   ✅ Temporal Correlation {'saved' if save_path else 'created'}")
            
            # 9. Concept Drift Heatmap
            save_path = f"{save_dir}/concept_drift_heatmap.png" if save_dir else None
            plot_concept_drift_heatmap(results['concept_drift_within_train'], save_path=save_path)
            print(f"   ✅ Concept Drift Heatmap {'saved' if save_path else 'created'}")
        
        # === DASHBOARDS ===
        print("\n📈 Creating Dashboards...")
        
        # Data Drift Dashboard
        if 'data_drift' in results:
            save_path = f"{save_dir}/dashboard_data_drift.png" if save_dir else None
            create_drift_dashboard(
                drift_results=results['data_drift'],
                temporal_results=results.get('temporal_drift'),
                save_path=save_path
            )
            print(f"   ✅ Data Drift Dashboard {'saved' if save_path else 'created'}")
            
        # Concept Drift Dashboard
        if 'concept_drift' in results:
            save_path = f"{save_dir}/dashboard_concept_drift.png" if save_dir else None
            create_concept_drift_dashboard(
                analysis_results=results['concept_drift'],
                temporal_results=results.get('concept_drift_within_train'),
                save_path=save_path
            )
            print(f"   ✅ Concept Drift Dashboard {'saved' if save_path else 'created'}")
        
        if show_plots:
            plt.show()
        else:
            plt.close('all')
        
        print("\n✅ Report complete!")

    def generate_html_report(
        self,
        results: Dict[str, pd.DataFrame],
        save_dir: str = './reports',
        report_name: str = 'drift_report.html',
        ai_advice: str = None
    ) -> str:
        """
        Creates an HTML dashboard containing all charts.
        
        Parameters:
        -----------
        results : Dict[str, pd.DataFrame]
            Output of full_analysis()
        save_dir : str
            Directory to save charts and HTML
        report_name : str
            HTML file name
        ai_advice : str, optional
            Actionable advice generated by LLM
        
        Returns:
        --------
        str: Path to the created HTML file
        """
        import matplotlib.pyplot as plt
        from .html_report import generate_html_report as _generate_html_report
        
        os.makedirs(save_dir, exist_ok=True)
        
        # Create charts first
        print("📈 Creating charts...")
        self.print_report(results, save_dir=save_dir, show_plots=False)
        
        # Create HTML report
        return _generate_html_report(
            results=results,
            save_dir=save_dir,
            report_name=report_name,
            ai_advice=ai_advice
        )

    # ==================== AI ADVISOR ====================

    def get_ai_advice(
        self,
        results: Dict[str, pd.DataFrame],
        language: str = 'en',
        base_url: str = "http://localhost:11434/v1",
        api_key: str = "ollama",
        model: str = "qwen2.5"
    ) -> str:
        """
        Generates actionable recommendations using an LLM.
        """
        from .advisor import DriftAdvisor
        
        advisor = DriftAdvisor(base_url=base_url, api_key=api_key, model=model)
        print(f"🧠 Consulting AI Advisor ({model})...")
        
        return advisor.get_advice(results, language=language)
