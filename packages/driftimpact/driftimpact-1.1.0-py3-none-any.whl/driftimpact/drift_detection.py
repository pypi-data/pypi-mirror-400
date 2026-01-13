"""
Drift Detection Module

Kolmogorov-Smirnov (KS) Test (Numerical): Checks if two datasets' distributions are the same. Sensitive to overall distribution differences.
Mann-Whitney U Test (Numerical): Tests if the medians (central tendencies) of two groups are different. Catches location shifts.
Levene Test (Numerical): Tests if the variances (variabilities) of two groups are equal. Catches changes in data spread.
Chi-Square Test (Categorical): Tests if the frequency distributions of categorical variables differ between training and scoring data.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any

class DriftDetector:
    def __init__(self, threshold: float = 0.05):
        self.threshold = threshold

    def run_tests(self, train_df: pd.DataFrame, score_df: pd.DataFrame) -> pd.DataFrame:
        """
        Runs statistical tests to detect drift between train and score datasets.
        """
        results = []
        
        # Identify common columns
        common_cols = list(set(train_df.columns) & set(score_df.columns))
        
        for col in common_cols:
            # Check data type
            is_numeric = pd.api.types.is_numeric_dtype(train_df[col])
            
            if is_numeric:
                self._test_numerical(train_df[col], score_df[col], col, results)
            else:
                self._test_categorical(train_df[col], score_df[col], col, results)
                
        return pd.DataFrame(results)

    def _test_numerical(self, train_series, score_series, col_name, results):
        # Drop NaNs for statistical tests
        t_clean = train_series.dropna()
        s_clean = score_series.dropna()
        
        if len(t_clean) < 2 or len(s_clean) < 2:
            return

        # 1. Kolmogorov-Smirnov Test (Distribution similarity)
        # H0: The two samples are drawn from the same distribution.
        ks_stat, ks_p = stats.ks_2samp(t_clean, s_clean)
        results.append({
            'Column': col_name,
            'Test': 'Kolmogorov-Smirnov',
            'Statistic': ks_stat,
            'P-Value': ks_p,
            'Drift Detected': ks_p < self.threshold
        })

        # 2. Mann-Whitney U Test (Location/Median shift)
        # H0: The distributions of both populations are equal.
        mw_stat, mw_p = stats.mannwhitneyu(t_clean, s_clean, alternative='two-sided')
        results.append({
            'Column': col_name,
            'Test': 'Mann-Whitney U',
            'Statistic': mw_stat,
            'P-Value': mw_p,
            'Drift Detected': mw_p < self.threshold
        })
        
        # 3. Levene's Test (Variance shift)
        # H0: The populations have equal variances.
        # Using 'median' (Brown-Forsythe) is more robust to non-normality
        lev_stat, lev_p = stats.levene(t_clean, s_clean, center='median')
        results.append({
            'Column': col_name,
            'Test': 'Levene (Variance)',
            'Statistic': lev_stat,
            'P-Value': lev_p,
            'Drift Detected': lev_p < self.threshold
        })

    def _test_categorical(self, train_series, score_series, col_name, results):
        # 4. Chi-Square Test (Frequency distribution)
        # H0: The categorical variables are independent (distributions are same).
        
        # Align categories
        t_counts = train_series.value_counts(normalize=False)
        s_counts = score_series.value_counts(normalize=False)
        
        # Get all unique categories
        all_cats = set(t_counts.index) | set(s_counts.index)
        
        # Create contingency table
        # We need expected frequencies. For drift, we often compare proportions.
        # Standard Chi-Square for homogeneity:
        # We construct a contingency table: [[Train_Cat1, Train_Cat2...], [Score_Cat1, Score_Cat2...]]
        
        # Reindex to ensure alignment and fill missing with 0
        t_aligned = t_counts.reindex(all_cats, fill_value=0)
        s_aligned = s_counts.reindex(all_cats, fill_value=0)
        
        # Remove categories with 0 total count (shouldn't happen if union is used)
        # Also, Chi-square is sensitive to small frequencies (<5).
        
        contingency = np.array([t_aligned.values, s_aligned.values])
        
        # Only run if we have valid data
        if contingency.sum() > 0:
            chi2_stat, chi2_p, dof, ex = stats.chi2_contingency(contingency)
            results.append({
                'Column': col_name,
                'Test': 'Chi-Square',
                'Statistic': chi2_stat,
                'P-Value': chi2_p,
                'Drift Detected': chi2_p < self.threshold
            })

class TemporalDriftDetector:
    """
    Temporal Drift Detection
    
    This class detects drift in each time segment by dividing the data into time slices.
    This helps determine when the drift started.
    
    Methods:
    1. Sliding Window: Divides the data by window size and compares each window with the training data.
    2. Cumulative: Compares cumulatively up to each time point.
    """
    
    def __init__(self, threshold: float = 0.05):
        self.threshold = threshold
        self.base_detector = DriftDetector(threshold=threshold)
    
    def detect_drift_by_time(
        self, 
        train_df: pd.DataFrame, 
        score_df: pd.DataFrame,
        time_col: str,
        feature_cols: list = None,
        method: str = 'sliding',  # 'sliding' or 'cumulative'
        window_size: int = None,
        n_windows: int = 10
    ) -> pd.DataFrame:
        """
        Performs time-based drift detection.
        
        Parameters:
        -----------
        train_df : pd.DataFrame
            Training data
        score_df : pd.DataFrame
            Scoring/prediction data (must contain time column)
        time_col : str
            Name of the time column (datetime or ordered numeric)
        feature_cols : list, optional
            Columns to analyze. If None, all common columns are used.
        method : str
            'sliding': Analysis with sliding window
            'cumulative': Cumulative analysis (from the beginning)
        window_size : int, optional
            Window size (number of rows). If None, it is calculated automatically.
        n_windows : int
            Number of windows to create (used if window_size is None)
        
        Returns:
        --------
        pd.DataFrame: Drift results for each time window and variable
        """
        # Sort by time column
        score_df = score_df.sort_values(time_col).reset_index(drop=True)
        
        # Determine feature columns
        if feature_cols is None:
            feature_cols = [c for c in train_df.columns if c in score_df.columns and c != time_col]
        
        # Calculate window size
        if window_size is None:
            window_size = max(len(score_df) // n_windows, 50)  # At least 50 rows
        
        results = []
        
        if method == 'sliding':
            results = self._sliding_window_analysis(train_df, score_df, time_col, feature_cols, window_size)
        elif method == 'cumulative':
            results = self._cumulative_analysis(train_df, score_df, time_col, feature_cols, window_size)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'sliding' or 'cumulative'.")
        
        return pd.DataFrame(results)
    
    def _sliding_window_analysis(self, train_df, score_df, time_col, feature_cols, window_size):
        """
        Compares each time window separately with train using sliding window.
        """
        results = []
        n_rows = len(score_df)
        
        window_start = 0
        while window_start < n_rows:
            window_end = min(window_start + window_size, n_rows)
            window_df = score_df.iloc[window_start:window_end]
            
            if len(window_df) < 10:  # Skip very small windows
                break
            
            # Determine time range
            time_start = window_df[time_col].iloc[0]
            time_end = window_df[time_col].iloc[-1]
            
            for col in feature_cols:
                is_numeric = pd.api.types.is_numeric_dtype(train_df[col])
                
                t_clean = train_df[col].dropna()
                s_clean = window_df[col].dropna()
                
                if len(t_clean) < 2 or len(s_clean) < 2:
                    continue
                
                if is_numeric:
                    # Kolmogorov-Smirnov Test
                    ks_stat, ks_p = stats.ks_2samp(t_clean, s_clean)
                    results.append({
                        'Window_Start': time_start,
                        'Window_End': time_end,
                        'Window_Index': window_start // window_size,
                        'Column': col,
                        'Test': 'Kolmogorov-Smirnov',
                        'Statistic': ks_stat,
                        'P-Value': ks_p,
                        'Drift_Detected': ks_p < self.threshold
                    })
                else:
                    # Chi-Square Test
                    t_counts = t_clean.value_counts(normalize=False)
                    s_counts = s_clean.value_counts(normalize=False)
                    all_cats = set(t_counts.index) | set(s_counts.index)
                    t_aligned = t_counts.reindex(all_cats, fill_value=0)
                    s_aligned = s_counts.reindex(all_cats, fill_value=0)
                    contingency = np.array([t_aligned.values, s_aligned.values])
                    
                    if contingency.sum() > 0 and len(all_cats) > 1:
                        chi2_stat, chi2_p, _, _ = stats.chi2_contingency(contingency)
                        results.append({
                            'Window_Start': time_start,
                            'Window_End': time_end,
                            'Window_Index': window_start // window_size,
                            'Column': col,
                            'Test': 'Chi-Square',
                            'Statistic': chi2_stat,
                            'P-Value': chi2_p,
                            'Drift_Detected': chi2_p < self.threshold
                        })
            
            window_start += window_size
        
        return results

    def _cumulative_analysis(self, train_df, score_df, time_col, feature_cols, step_size):
        """
        Cumulative analysis: Compares data from start to each step with train.
        Useful for detecting the first point where drift is seen.
        """
        results = []
        n_rows = len(score_df)
        
        for end_idx in range(step_size, n_rows + 1, step_size):
            cumulative_df = score_df.iloc[:end_idx]
            time_end = cumulative_df[time_col].iloc[-1]
            
            for col in feature_cols:
                is_numeric = pd.api.types.is_numeric_dtype(train_df[col])
                
                t_clean = train_df[col].dropna()
                s_clean = cumulative_df[col].dropna()
                
                if len(t_clean) < 2 or len(s_clean) < 2:
                    continue
                
                if is_numeric:
                    ks_stat, ks_p = stats.ks_2samp(t_clean, s_clean)
                    results.append({
                        'Cumulative_End': time_end,
                        'Sample_Size': end_idx,
                        'Column': col,
                        'Test': 'Kolmogorov-Smirnov',
                        'Statistic': ks_stat,
                        'P-Value': ks_p,
                        'Drift_Detected': ks_p < self.threshold
                    })
        
        return results

    def find_first_drift_point(self, temporal_results: pd.DataFrame, column: str = None) -> pd.DataFrame:
        """
        Finds the first point where drift was detected.
        
        Parameters:
        -----------
        temporal_results : pd.DataFrame
            Output of detect_drift_by_time()
        column : str, optional
            For a specific column. If None, for all columns.
        
        Returns:
        --------
        pd.DataFrame: First drift point for each column
        """
        df = temporal_results[temporal_results['Drift_Detected'] == True]
        
        if column:
            df = df[df['Column'] == column]
        
        if df.empty:
            return pd.DataFrame({'Message': ['No drift detected in the specified time range']})
        
        # Find first drift point for each column
        time_col = 'Window_Start' if 'Window_Start' in df.columns else 'Cumulative_End'
        first_drifts = df.groupby('Column').first().reset_index()
        
        return first_drifts[['Column', time_col, 'Test', 'Statistic', 'P-Value']]


# Example Usage
if __name__ == "__main__":
    # Create dummy data
    np.random.seed(42)
    
    # Train data
    train = pd.DataFrame({
        'age': np.random.normal(30, 5, 1000),
        'income': np.random.exponential(5000, 1000),
        'segment': np.random.choice(['A', 'B', 'C'], 1000, p=[0.2, 0.5, 0.3])
    })
    
    # Score data (Drifted)
    score = pd.DataFrame({
        'age': np.random.normal(35, 5, 1000), # Mean shift (Drift!)
        'income': np.random.exponential(5000, 1000), # No drift
        'segment': np.random.choice(['A', 'B', 'C'], 1000, p=[0.1, 0.4, 0.5]) # Distribution shift (Drift!)
    })
    
    detector = DriftDetector(threshold=0.05)
    drift_report = detector.run_tests(train, score)
    
    print("--- Drift Detection Report ---")
    print(drift_report.to_markdown(index=False))
    
    # -------- TEMPORAL DRIFT EXAMPLE --------
    print("\n" + "="*60)
    print("--- Temporal Drift Detection Example ---")
    print("="*60)
    
    # Create temporal data (scenario where drift starts in the middle)
    np.random.seed(42)
    
    # Train data
    train_temporal = pd.DataFrame({
        'feature_x': np.random.normal(50, 10, 1000),
        'category': np.random.choice(['A', 'B'], 1000, p=[0.6, 0.4])
    })
    
    # Score data: First half normal, second half drifted
    dates = pd.date_range(start='2024-01-01', periods=1000, freq='D')
    
    # First 500 days: Normal (same distribution as train)
    normal_part = pd.DataFrame({
        'date': dates[:500],
        'feature_x': np.random.normal(50, 10, 500),
        'category': np.random.choice(['A', 'B'], 500, p=[0.6, 0.4])
    })
    
    # Last 500 days: Drifted (different distribution)
    drifted_part = pd.DataFrame({
        'date': dates[500:],
        'feature_x': np.random.normal(70, 10, 500),  # Mean shift!
        'category': np.random.choice(['A', 'B'], 500, p=[0.3, 0.7])  # Distribution shift!
    })
    
    score_temporal = pd.concat([normal_part, drifted_part], ignore_index=True)
    
    # Temporal drift detection
    temporal_detector = TemporalDriftDetector(threshold=0.05)
    
    temporal_results = temporal_detector.detect_drift_by_time(
        train_df=train_temporal,
        score_df=score_temporal,
        time_col='date',
        method='sliding',
        n_windows=10
    )
    
    print("\n--- Sliding Window Results ---")
    print(temporal_results.to_markdown(index=False))
    
    # Find first drift point
    first_drift = temporal_detector.find_first_drift_point(temporal_results)
    print("\n--- First Drift Points ---")
    print(first_drift.to_markdown(index=False))
