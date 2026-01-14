"""Feature engineering functions."""
import pandas as pd


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create new features from existing data.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with new features
    """
    df_features = df.copy()
    
    # Add your feature engineering logic here
    # Example:
    # df_features['feature_ratio'] = df['col1'] / df['col2']
    
    return df_features


def select_features(df: pd.DataFrame, target: str, k: int = 10) -> list:
    """
    Select top k features based on correlation with target.
    
    Args:
        df: Input DataFrame
        target: Target column name
        k: Number of features to select
        
    Returns:
        List of selected feature names
    """
    correlations = df.corr()[target].abs().sort_values(ascending=False)
    return correlations[1:k+1].index.tolist()
