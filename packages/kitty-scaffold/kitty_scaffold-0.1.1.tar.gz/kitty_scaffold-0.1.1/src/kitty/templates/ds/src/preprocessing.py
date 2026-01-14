"""Data preprocessing functions."""
import pandas as pd
import numpy as np


def handle_missing_values(df: pd.DataFrame, strategy: str = 'drop') -> pd.DataFrame:
    """
    Handle missing values in the dataset.
    
    Args:
        df: Input DataFrame
        strategy: 'drop', 'mean', 'median', or 'mode'
        
    Returns:
        DataFrame with missing values handled
    """
    if strategy == 'drop':
        return df.dropna()
    elif strategy == 'mean':
        return df.fillna(df.mean())
    elif strategy == 'median':
        return df.fillna(df.median())
    elif strategy == 'mode':
        return df.fillna(df.mode().iloc[0])
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def remove_outliers(df: pd.DataFrame, columns: list, method: str = 'iqr') -> pd.DataFrame:
    """
    Remove outliers from specified columns.
    
    Args:
        df: Input DataFrame
        columns: Columns to check for outliers
        method: 'iqr' or 'zscore'
        
    Returns:
        DataFrame with outliers removed
    """
    df_clean = df.copy()
    
    for col in columns:
        if method == 'iqr':
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            df_clean = df_clean[
                (df_clean[col] >= Q1 - 1.5 * IQR) & 
                (df_clean[col] <= Q3 + 1.5 * IQR)
            ]
        elif method == 'zscore':
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            df_clean = df_clean[z_scores < 3]
    
    return df_clean
