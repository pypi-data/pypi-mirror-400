"""
Concept Drift Detector

Numerical Variables (vs Numerical Target):
Method: Pearson Correlation Coefficient comparison.
Test: Fisher Z-Test. Tests if the difference between correlation coefficients in training and scoring data is statistically significant.
If P_Value < 0.05, the relationship strength or direction has changed significantly (Drift Exists).

Categorical Variables (vs Categorical Target):
Method: Cramer's V (Association Strength).
Test: Checks the difference between Cramer's V values in the two datasets. Instead of a statistical p-value test, it decides on drift based on the magnitude of the difference (e.g., > 0.1).

Functions:
1. run_analysis(): Concept drift analysis between Train and Score (labeled) data
2. analyze_within_train(): Temporal concept drift analysis within Train data itself
3. analyze_with_actuals(): Concept drift analysis between Train and production data when realized labels are available
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import List, Optional, Union


class ConceptDriftDetector:
    def __init__(self, target_col: str, threshold: float = 0.05):
        self.target_col = target_col
        self.threshold = threshold

    # ==================== HELPER METHODS ====================
    
    def _calculate_correlation(self, df: pd.DataFrame, feature_col: str) -> float:
        """Calculates Pearson correlation between feature and target."""
        clean = df[[feature_col, self.target_col]].dropna()
        if len(clean) < 3:
            return np.nan
        r, _ = stats.pearsonr(clean[feature_col], clean[self.target_col])
        return r

    def _calculate_cramers_v(self, df: pd.DataFrame, feature_col: str) -> float:
        """Calculates Cramer's V between categorical feature and target."""
        clean = df[[feature_col, self.target_col]].dropna()
        if len(clean) < 2:
            return np.nan
        
        confusion_matrix = pd.crosstab(clean[feature_col], clean[self.target_col])
        if confusion_matrix.shape[0] < 2 or confusion_matrix.shape[1] < 2:
            return np.nan
            
        chi2 = stats.chi2_contingency(confusion_matrix)[0]
        n = confusion_matrix.sum().sum()
        phi2 = chi2 / n
        r, k = confusion_matrix.shape
        phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))    
        rcorr = r - ((r-1)**2)/(n-1)
        kcorr = k - ((k-1)**2)/(n-1)
        
        denom = min((kcorr-1), (rcorr-1))
        if denom <= 0:
            return np.nan
        return np.sqrt(phi2corr / denom)

    def _fisher_z_test(self, r1: float, n1: int, r2: float, n2: int) -> tuple:
        """Performs Fisher Z-test to compare two correlation coefficients."""
        if np.isnan(r1) or np.isnan(r2):
            return np.nan, np.nan
        
        r1 = np.clip(r1, -0.99999, 0.99999)
        r2 = np.clip(r2, -0.99999, 0.99999)
        
        z1 = 0.5 * np.log((1 + r1) / (1 - r1))
        z2 = 0.5 * np.log((1 + r2) / (1 - r2))
        
        se_diff = np.sqrt(1/(n1 - 3) + 1/(n2 - 3))
        z_stat = (z1 - z2) / se_diff
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        
        return z_stat, p_value

    # ==================== MAIN ANALYSIS METHODS ====================

    def run_analysis(self, train_df: pd.DataFrame, score_df: pd.DataFrame) -> pd.DataFrame:
        """
        [ORIGINAL] Analyzes concept drift by comparing feature-target relationships 
        in Train vs Score datasets.
        
        Requires 'target_col' to be present in both DataFrames.
        """
        if self.target_col not in train_df.columns or self.target_col not in score_df.columns:
            raise ValueError(f"Target column '{self.target_col}' must be in both datasets.")

        results = []
        feature_cols = [c for c in train_df.columns if c != self.target_col and c in score_df.columns]

        for col in feature_cols:
            is_numeric_feature = pd.api.types.is_numeric_dtype(train_df[col])
            is_numeric_target = pd.api.types.is_numeric_dtype(train_df[self.target_col])

            if is_numeric_feature and is_numeric_target:
                self._test_correlation_drift(train_df, score_df, col, results)
            elif not is_numeric_feature and not is_numeric_target:
                self._test_cramers_v_drift(train_df, score_df, col, results)

        return pd.DataFrame(results)

    def analyze_within_train(
        self, 
        train_df: pd.DataFrame, 
        time_col: str,
        n_periods: int = 4,
        feature_cols: List[str] = None
    ) -> pd.DataFrame:
        """
        Temporal concept drift analysis within Train data itself.
        
        Splits the Train data into time periods and compares each period's 
        feature-target relationship with the previous period.
        
        Parameters:
        -----------
        train_df : pd.DataFrame
            Training data (including target column)
        time_col : str
            Name of the time column
        n_periods : int
            Number of periods to split into (default: 4, e.g., quarters)
        feature_cols : List[str], optional
            Feature columns to analyze. If None, all numerical/categorical columns.
        
        Returns:
        --------
        pd.DataFrame: Concept drift results for each period and feature
        """
        if self.target_col not in train_df.columns:
            raise ValueError(f"Target column '{self.target_col}' must be in train_df.")
        
        # Sort by time
        df = train_df.sort_values(time_col).reset_index(drop=True)
        
        # Split into periods
        df['_period'] = pd.qcut(range(len(df)), n_periods, labels=False)
        
        # Get feature columns
        if feature_cols is None:
            feature_cols = [c for c in df.columns if c not in [self.target_col, time_col, '_period']]
        
        results = []
        is_numeric_target = pd.api.types.is_numeric_dtype(df[self.target_col])
        
        for period in range(1, n_periods):
            prev_df = df[df['_period'] == period - 1]
            curr_df = df[df['_period'] == period]
            
            period_start = curr_df[time_col].iloc[0]
            period_end = curr_df[time_col].iloc[-1]
            
            for col in feature_cols:
                is_numeric_feature = pd.api.types.is_numeric_dtype(df[col])
                
                if is_numeric_feature and is_numeric_target:
                    # Correlation comparison
                    r_prev = self._calculate_correlation(prev_df, col)
                    r_curr = self._calculate_correlation(curr_df, col)
                    
                    n_prev = len(prev_df[[col, self.target_col]].dropna())
                    n_curr = len(curr_df[[col, self.target_col]].dropna())
                    
                    z_stat, p_value = self._fisher_z_test(r_prev, n_prev, r_curr, n_curr)
                    
                    results.append({
                        'Period': period,
                        'Period_Start': period_start,
                        'Period_End': period_end,
                        'Feature': col,
                        'Method': 'Fisher Z-Test',
                        'Prev_Period_Metric': r_prev,
                        'Curr_Period_Metric': r_curr,
                        'Drift_Stat': z_stat,
                        'P_Value': p_value,
                        'Drift_Detected': p_value < self.threshold if not np.isnan(p_value) else False
                    })
                
                elif not is_numeric_feature and not is_numeric_target:
                    # Cramer's V comparison
                    v_prev = self._calculate_cramers_v(prev_df, col)
                    v_curr = self._calculate_cramers_v(curr_df, col)
                    
                    if not np.isnan(v_prev) and not np.isnan(v_curr):
                        diff = abs(v_prev - v_curr)
                        results.append({
                            'Period': period,
                            'Period_Start': period_start,
                            'Period_End': period_end,
                            'Feature': col,
                            'Method': "Cramer's V Diff",
                            'Prev_Period_Metric': v_prev,
                            'Curr_Period_Metric': v_curr,
                            'Drift_Stat': diff,
                            'P_Value': np.nan,
                            'Drift_Detected': diff > 0.1
                        })
        
        return pd.DataFrame(results)

    def analyze_with_actuals(
        self, 
        train_df: pd.DataFrame, 
        actuals_df: pd.DataFrame,
        time_col: str = None,
        feature_cols: List[str] = None
    ) -> pd.DataFrame:
        """
        Performs concept drift analysis when realized labels (actuals) are available.
        
        When actual results are obtained after making predictions in production
        (e.g., churn prediction was made, actual churn info arrived 3 months later),
        this function compares the train data with the production data.
        
        Parameters:
        -----------
        train_df : pd.DataFrame
            Training data (including target)
        actuals_df : pd.DataFrame
            Production data with realized labels (including target)
        time_col : str, optional
            If provided, splits production data into time windows
        feature_cols : List[str], optional
            Feature columns to analyze
        
        Returns:
        --------
        pd.DataFrame: Concept drift results
        """
        if self.target_col not in train_df.columns:
            raise ValueError(f"Target column '{self.target_col}' must be in train_df.")
        if self.target_col not in actuals_df.columns:
            raise ValueError(f"Target column '{self.target_col}' must be in actuals_df (with realized labels).")
        
        # Get feature columns
        if feature_cols is None:
            feature_cols = [c for c in train_df.columns 
                           if c != self.target_col and c in actuals_df.columns and c != time_col]
        
        results = []
        is_numeric_target = pd.api.types.is_numeric_dtype(train_df[self.target_col])
        
        # If time_col provided, do temporal analysis
        if time_col and time_col in actuals_df.columns:
            actuals_df = actuals_df.sort_values(time_col).reset_index(drop=True)
            actuals_df['_window'] = pd.qcut(range(len(actuals_df)), min(5, len(actuals_df)//100 + 1), labels=False, duplicates='drop')
            
            for window in actuals_df['_window'].unique():
                window_df = actuals_df[actuals_df['_window'] == window]
                window_start = window_df[time_col].iloc[0]
                window_end = window_df[time_col].iloc[-1]
                
                for col in feature_cols:
                    self._compare_feature_relationship(
                        train_df, window_df, col, is_numeric_target, results,
                        window_info={'Window': window, 'Window_Start': window_start, 'Window_End': window_end}
                    )
        else:
            # Single comparison (all actuals vs train)
            for col in feature_cols:
                self._compare_feature_relationship(
                    train_df, actuals_df, col, is_numeric_target, results
                )
        
        return pd.DataFrame(results)

    def _compare_feature_relationship(
        self, 
        train_df: pd.DataFrame, 
        compare_df: pd.DataFrame, 
        col: str, 
        is_numeric_target: bool,
        results: list,
        window_info: dict = None
    ):
        """Helper to compare feature-target relationship between two datasets."""
        is_numeric_feature = pd.api.types.is_numeric_dtype(train_df[col])
        
        base_result = window_info.copy() if window_info else {}
        base_result['Feature'] = col
        
        if is_numeric_feature and is_numeric_target:
            r_train = self._calculate_correlation(train_df, col)
            r_compare = self._calculate_correlation(compare_df, col)
            
            n_train = len(train_df[[col, self.target_col]].dropna())
            n_compare = len(compare_df[[col, self.target_col]].dropna())
            
            z_stat, p_value = self._fisher_z_test(r_train, n_train, r_compare, n_compare)
            
            base_result.update({
                'Method': 'Fisher Z-Test',
                'Train_Metric': r_train,
                'Actuals_Metric': r_compare,
                'Drift_Stat': z_stat,
                'P_Value': p_value,
                'Drift_Detected': p_value < self.threshold if not np.isnan(p_value) else False
            })
            results.append(base_result)
            
        elif not is_numeric_feature and not is_numeric_target:
            v_train = self._calculate_cramers_v(train_df, col)
            v_compare = self._calculate_cramers_v(compare_df, col)
            
            if not np.isnan(v_train) and not np.isnan(v_compare):
                diff = abs(v_train - v_compare)
                base_result.update({
                    'Method': "Cramer's V Diff",
                    'Train_Metric': v_train,
                    'Actuals_Metric': v_compare,
                    'Drift_Stat': diff,
                    'P_Value': np.nan,
                    'Drift_Detected': diff > 0.1
                })
                results.append(base_result)

    # ==================== LEGACY METHODS (for run_analysis) ====================
    
    def _test_correlation_drift(self, train_df, score_df, col, results):
        """Uses Fisher's Z-Transformation to test correlation difference."""
        t_clean = train_df[[col, self.target_col]].dropna()
        s_clean = score_df[[col, self.target_col]].dropna()
        
        if len(t_clean) < 3 or len(s_clean) < 3:
            return

        r_train, _ = stats.pearsonr(t_clean[col], t_clean[self.target_col])
        r_score, _ = stats.pearsonr(s_clean[col], s_clean[self.target_col])

        z_stat, p_value = self._fisher_z_test(r_train, len(t_clean), r_score, len(s_clean))

        results.append({
            'Feature': col,
            'Method': 'Fisher Z-Test (Correlation)',
            'Train_Metric': r_train,
            'Score_Metric': r_score,
            'Drift_Stat': z_stat,
            'P_Value': p_value,
            'Drift_Detected': p_value < self.threshold if not np.isnan(p_value) else False
        })

    def _test_cramers_v_drift(self, train_df, score_df, col, results):
        """Calculates Cramer's V for both datasets and reports the difference."""
        v_train = self._calculate_cramers_v(train_df, col)
        v_score = self._calculate_cramers_v(score_df, col)
        
        if np.isnan(v_train) or np.isnan(v_score):
            return

        diff = abs(v_train - v_score)

        results.append({
            'Feature': col,
            'Method': "Cramer's V Diff",
            'Train_Metric': v_train,
            'Score_Metric': v_score,
            'Drift_Stat': diff,
            'P_Value': np.nan,
            'Drift_Detected': diff > 0.1 
        })


# ==================== EXAMPLE USAGE ====================
if __name__ == "__main__":
    np.random.seed(42)
    
    print("="*70)
    print("EXAMPLE 1: analyze_within_train() - Within-Train Temporal Concept Drift")
    print("="*70)
    
    # Train data: Relationship changes over time
    dates = pd.date_range(start='2023-01-01', periods=1000, freq='D')
    
    train_temporal = pd.DataFrame({
        'date': dates,
        'feature_x': np.random.normal(0, 1, 1000),
        'category': np.random.choice(['A', 'B'], 1000)
    })
    
    # Strong relationship in first half, weak relationship in second half (concept drift!)
    train_temporal['target'] = np.where(
        train_temporal.index < 500,
        3 * train_temporal['feature_x'] + np.random.normal(0, 1, 1000),  # Strong
        0.2 * train_temporal['feature_x'] + np.random.normal(0, 1, 1000)  # Weak
    )
    
    detector = ConceptDriftDetector(target_col='target')
    within_train_report = detector.analyze_within_train(
        train_df=train_temporal,
        time_col='date',
        n_periods=4
    )
    
    print("\n--- Within-Train Concept Drift Report ---")
    print(within_train_report.to_markdown(index=False))
    
    print("\n" + "="*70)
    print("EXAMPLE 2: analyze_with_actuals() - Analysis with Realized Labels")
    print("="*70)
    
    # Train data
    train = pd.DataFrame({
        'feature_x': np.random.normal(0, 1, 1000),
        'target': np.zeros(1000)
    })
    train['target'] = 3 * train['feature_x'] + np.random.normal(0, 1, 1000)
    
    # Production data (with realized labels) - relationship changed
    actuals = pd.DataFrame({
        'date': pd.date_range(start='2024-01-01', periods=500, freq='D'),
        'feature_x': np.random.normal(0, 1, 500),
        'target': np.zeros(500)
    })
    actuals['target'] = 0.3 * actuals['feature_x'] + np.random.normal(0, 1, 500)  # Weakened relationship
    
    actuals_report = detector.analyze_with_actuals(
        train_df=train,
        actuals_df=actuals,
        time_col='date'
    )
    
    print("\n--- Actuals-Based Concept Drift Report ---")
    print(actuals_report.to_markdown(index=False))

