"""
Model Performance Impact Analyzer

This module analyzes the relationship between data drift and model performance.
By using the model, it examines performance changes over time and their correlation with drift.
"""

import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, r2_score
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt

class PerformanceAnalyzer:
    def __init__(self, model, task_type='classification'):
        """
        Parameters:
        -----------
        model : object
            Sklearn-like model with a predict method
        task_type : str
            'classification' or 'regression'
        """
        self.model = model
        self.task_type = task_type
        
    def _calculate_metrics(self, y_true, y_pred) -> Dict[str, float]:
        """Calculates metrics based on task type."""
        metrics = {}
        if self.task_type == 'classification':
            metrics['accuracy'] = accuracy_score(y_true, y_pred)
            metrics['f1'] = f1_score(y_true, y_pred, average='weighted')
        else:
            metrics['rmse'] = np.sqrt(mean_squared_error(y_true, y_pred))
            metrics['r2'] = r2_score(y_true, y_pred)
        return metrics

    def _get_feature_importance(self, feature_names: List[str]) -> pd.DataFrame:
        """Attempts to extract feature importance from the model."""
        importance = None
        
        # Tree-based models (RandomForest, XGBoost, LGBM)
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
        # Linear models (Logistic Regression, Linear Regression)
        elif hasattr(self.model, 'coef_'):
            importance = np.abs(self.model.coef_)
            if importance.ndim > 1:
                importance = importance.mean(axis=0)  # Average for Multiclass
                
        if importance is not None and len(importance) == len(feature_names):
            return pd.DataFrame({
                'Feature': feature_names,
                'Importance': importance
            }).sort_values('Importance', ascending=False)
        
        # If not extractable, use equal weight
        return pd.DataFrame({
            'Feature': feature_names,
            'Importance': 1.0 / len(feature_names)
        })

    def analyze_impact(
        self,
        X_df: pd.DataFrame,
        y_true: pd.Series,
        time_col: pd.Series,
        drift_results: pd.DataFrame,
        window_size: int = None,
        n_windows: int = 10
    ) -> Dict[str, Any]:
        """
        Analyzes the relationship between drift and performance.
        
        Parameters:
        -----------
        X_df : pd.DataFrame
            Model inputs (Features)
        y_true : pd.Series
            Actual target values
        time_col : pd.Series
            Time column (same length as X_df)
        drift_results : pd.DataFrame
            DriftAnalyzer.detect_drift_by_time output (Drift statistics)
        """
        # Get feature importance
        feature_importance = self._get_feature_importance(X_df.columns.tolist())
        
        # Sort data by time
        df = X_df.copy()
        df['_target'] = y_true.values
        df['_time'] = time_col.values
        df = df.sort_values('_time').reset_index(drop=True)
        
        # Create windows
        if window_size is None:
            window_size = len(df) // n_windows
            
        analysis_results = []
        
        # Sliding window analysis
        for i in range(0, len(df), window_size):
            window_df = df.iloc[i:i+window_size]
            if len(window_df) < 20: continue
            
            # 1. Calculate Model Performance
            X_window = window_df.drop(['_target', '_time'], axis=1)
            y_window = window_df['_target']
            
            try:
                y_pred = self.model.predict(X_window)
                perf_metrics = self._calculate_metrics(y_window, y_pred)
            except Exception as e:
                print(f"Prediction error in window {i}: {e}")
                continue
                
            # 2. Calculate Weighted Drift Score
            # Find drift results corresponding to this window's time range
            # Note: Drift results come as already calculated, need to match them here
            # For simplicity: Find the one closest to the window in the drift_results table
            # OR simply recalculate the drift score here (Instantaneous drift, not cumulative)
            # More robust method: Compare X_window with Train data.
            # However, we can try using ready drift results for performance.
            
            # For now, get Weighted Drift Score from drift_results (time matching)
            # instead of calculating from the window data.
            
            window_start = window_df['_time'].iloc[0]
            
            # Find the window closest to this time in drift results
            # (drift_results should have 'Window_Start')
            if 'Window_Start' in drift_results.columns:
                # Find closest drift record by time (simple matching)
                # In a real scenario, time range overlap could be checked
                
                # Get drift statistics for ALL features in that window
                # Drift statistic (Normalize KS Statistic or Chi2 Statistic)
                
                # The structure of drift_results is important. Each row is a feature-window pair
                # Sum the drift scores of all features in the window (weighted)
                
                # Find matching windows (approximate)
                relevant_drift = drift_results[
                    (drift_results['Window_Start'] >= window_start) & 
                    (drift_results['Window_Start'] < window_df['_time'].iloc[-1])
                ]
                
                if not relevant_drift.empty:
                    # Merge with feature importance
                    merged = relevant_drift.merge(
                        feature_importance, 
                        left_on='Column', 
                        right_on='Feature', 
                        how='left'
                    )
                    
                    # Weighted Drift Score = Sum(Drift_Stat * Importance) / Sum(Importance)
                    # KS Stat is between 0-1, Chi2 should be normalized or only p-value used
                    # P-Value is inversely proportional (small p -> large drift), KS Stat is directly proportional
                    
                    # For those only with KS test (numerical) or via a general "Statistic"
                    # For simplicity, let's use the Statistic value (0-1 for KS)
                    
                    weighted_drift = (merged['Statistic'] * merged['Importance']).sum() / merged['Importance'].sum()
                else:
                    weighted_drift = 0
            else:
                weighted_drift = 0
            
            result_row = {
                'Window_Start': window_start,
                'Weighted_Drift_Score': weighted_drift,
                **perf_metrics
            }
            analysis_results.append(result_row)
            
        results_df = pd.DataFrame(analysis_results)
        return results_df

    def plot_impact(self, results_df: pd.DataFrame, metric_name='accuracy', save_path=None, show_plot=True):
        """Plots the relationship between Performance and Drift."""
        fig, ax1 = plt.subplots(figsize=(12, 6))

        color = 'tab:blue'
        ax1.set_xlabel('Time')
        ax1.set_ylabel(f'Model Performance ({metric_name})', color=color)
        ax1.plot(results_df['Window_Start'], results_df[metric_name], color=color, marker='o', label=metric_name)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, alpha=0.3)

        ax2 = ax1.twinx()  # Second axis
        color = 'tab:red'
        ax2.set_ylabel('Weighted Drift Score', color=color)
        ax2.plot(results_df['Window_Start'], results_df['Weighted_Drift_Score'], color=color, linestyle='--', marker='x', label='Drift Score')
        ax2.tick_params(axis='y', labelcolor=color)

        plt.title('Impact of Data Drift on Model Performance')
        fig.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        
        if show_plot:
            plt.show()
        else:
            plt.close()
