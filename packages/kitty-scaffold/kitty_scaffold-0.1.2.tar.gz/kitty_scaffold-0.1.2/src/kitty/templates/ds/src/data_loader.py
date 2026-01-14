"""Data loading utilities."""
import pandas as pd
from pathlib import Path


def load_raw_data(filename: str) -> pd.DataFrame:
    """
    Load raw data from data/raw directory.
    
    Args:
        filename: Name of the file to load
        
    Returns:
        DataFrame with loaded data
    """
    data_path = Path(__file__).parent.parent / "data" / "raw" / filename
    
    if filename.endswith('.csv'):
        return pd.read_csv(data_path)
    elif filename.endswith('.xlsx'):
        return pd.read_excel(data_path)
    else:
        raise ValueError(f"Unsupported file type: {filename}")


def save_processed_data(df: pd.DataFrame, filename: str) -> None:
    """
    Save processed data to data/processed directory.
    
    Args:
        df: DataFrame to save
        filename: Name for the output file
    """
    output_path = Path(__file__).parent.parent / "data" / "processed" / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")
