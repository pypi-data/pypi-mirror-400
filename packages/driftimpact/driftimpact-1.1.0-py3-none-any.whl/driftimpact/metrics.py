import numpy as np
import pandas as pd
from typing import Union, List, Optional

def _get_categorical_probs(data: Union[List, np.ndarray, pd.Series], categories: Optional[Union[List, np.ndarray]] = None) -> np.ndarray:
    """
    Calculates probability distribution for categorical data.
    Ensures both distributions share the same support (categories).
    """
    if not isinstance(data, pd.Series):
        data = pd.Series(data)
    
    if categories is None:
        categories = data.unique()
        
    # Calculate counts and reindex to ensure all categories are present
    counts = data.value_counts().reindex(categories, fill_value=0)
    probs = counts / counts.sum()
    return probs.values

def calculate_tvd(p_data: Union[List, np.ndarray, pd.Series], q_data: Union[List, np.ndarray, pd.Series]) -> float:
    """
    Calculates Total Variation Distance (TVD) for categorical variables.
    TVD = 0.5 * sum(|P(x) - Q(x)|)
    """
    # Unify categories to ensure same support
    all_data = pd.concat([pd.Series(p_data), pd.Series(q_data)])
    categories = all_data.unique()
    
    p_probs = _get_categorical_probs(p_data, categories)
    q_probs = _get_categorical_probs(q_data, categories)
    
    tvd = 0.5 * np.sum(np.abs(p_probs - q_probs))
    return tvd

def _get_numerical_probs(p_data: np.ndarray, q_data: np.ndarray, bins: Union[int, str] = 'auto') -> tuple[np.ndarray, np.ndarray]:
    """
    Calculates probability distributions for numerical data using histogram binning.
    Returns probabilities for p and q over the same bins.
    """
    # Combine data to determine bin edges that cover both distributions
    p_data = np.asarray(p_data)
    q_data = np.asarray(q_data)
    
    # Filter out NaNs if any
    p_data = p_data[~np.isnan(p_data)]
    q_data = q_data[~np.isnan(q_data)]
    
    combined = np.concatenate([p_data, q_data])
    
    # Calculate histogram to get bin edges
    _, bin_edges = np.histogram(combined, bins=bins)
    
    # Calculate probabilities using the same bin edges
    p_hist, _ = np.histogram(p_data, bins=bin_edges)
    q_hist, _ = np.histogram(q_data, bins=bin_edges)
    
    # Normalize to get probabilities
    p_probs = p_hist / p_hist.sum()
    q_probs = q_hist / q_hist.sum()
    
    return p_probs, q_probs

def calculate_kl_divergence(p_data: Union[List, np.ndarray], q_data: Union[List, np.ndarray], bins: Union[int, str] = 'auto', epsilon: float = 1e-10) -> float:
    """
    Calculates Kullback-Leibler (KL) Divergence for numerical variables.
    KL(P || Q) = sum(P(x) * log(P(x) / Q(x)))
    
    Note: Adds epsilon to probabilities to avoid division by zero or log(0).
    """
    p_probs, q_probs = _get_numerical_probs(p_data, q_data, bins)
    
    # Add epsilon to avoid numerical issues
    p_probs = p_probs + epsilon
    q_probs = q_probs + epsilon
    
    # Renormalize
    p_probs = p_probs / p_probs.sum()
    q_probs = q_probs / q_probs.sum()
    
    kl_div = np.sum(p_probs * np.log(p_probs / q_probs))
    return kl_div

def calculate_js_divergence(p_data: Union[List, np.ndarray], q_data: Union[List, np.ndarray], bins: Union[int, str] = 'auto', epsilon: float = 1e-10) -> float:
    """
    Calculates Jensen-Shannon (JS) Divergence for numerical variables.
    JS(P || Q) = 0.5 * KL(P || M) + 0.5 * KL(Q || M)
    where M = 0.5 * (P + Q)
    """
    p_probs, q_probs = _get_numerical_probs(p_data, q_data, bins)
    
    # Add epsilon
    p_probs = p_probs + epsilon
    q_probs = q_probs + epsilon
    
    # Renormalize
    p_probs = p_probs / p_probs.sum()
    q_probs = q_probs / q_probs.sum()
    
    m_probs = 0.5 * (p_probs + q_probs)
    
    kl_p_m = np.sum(p_probs * np.log(p_probs / m_probs))
    kl_q_m = np.sum(q_probs * np.log(q_probs / m_probs))
    
    js_div = 0.5 * kl_p_m + 0.5 * kl_q_m
    return js_div
