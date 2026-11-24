"""
Data Loader Module for BTP Mine Fire Gas Analysis
Safely loads real mine-fire datasets, atmospheric references, and Coward boundary definitions.
"""

import os
import pandas as pd
from typing import Tuple, Dict, Any, Optional

def get_default_paths(base_dir: Optional[str] = None) -> Dict[str, str]:
    """Resolve standard project directory paths."""
    if base_dir is None:
        # Check if we are inside src or project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.basename(current_dir) == "src":
            base_dir = os.path.abspath(os.path.join(current_dir, ".."))
        else:
            base_dir = os.path.abspath(current_dir)

    paths = {
        "base_dir": base_dir,
        "data_dir": os.path.join(base_dir, "data"),
        "lodna_csv": os.path.join(base_dir, "data", "lodna_mine_fire_data.csv"),
        "normal_air_csv": os.path.join(base_dir, "data", "normal_air_reference.csv"),
        "coward_csv": os.path.join(base_dir, "coward", "coward_boundaries.csv"),
        "coward_template_csv": os.path.join(base_dir, "coward", "coward_boundaries_template.csv"),
        "results_dir": os.path.join(base_dir, "results"),
        "figures_dir": os.path.join(base_dir, "results", "figures"),
        "tables_dir": os.path.join(base_dir, "results", "tables"),
        "reports_dir": os.path.join(base_dir, "results", "reports"),
    }
    return paths


def load_lodna_data(filepath: Optional[str] = None) -> pd.DataFrame:
    """
    Load the 14 real mine fire gas samples from Lodna Colliery, Jharia Coalfield.
    Source: Singh et al. (2007), Int. J. Coal Geol., 69(3), 192-204.
    """
    if filepath is None:
        paths = get_default_paths()
        filepath = paths["lodna_csv"]

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Lodna mine fire dataset not found at: {filepath}\n"
            f"Please verify the file exists in the data directory."
        )

    required_columns = [
        "Sample_No", "Date", "CO2_percent", "O2_percent",
        "CO_percent", "H2_percent", "CH4_percent", "N2_percent", "Temperature_C"
    ]

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        raise ValueError(f"Failed to read CSV file at {filepath}: {str(e)}")

    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset missing required columns: {missing_cols}")

    # Ensure numeric types
    numeric_cols = [
        "CO2_percent", "O2_percent", "CO_percent",
        "H2_percent", "CH4_percent", "N2_percent", "Temperature_C"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Parse date column for chronological ordering and plotting
    df["Date_Parsed"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")

    return df


def load_normal_air_reference(filepath: Optional[str] = None) -> pd.DataFrame:
    """Load standard atmospheric air baseline (volume and mass percentages)."""
    if filepath is None:
        paths = get_default_paths()
        filepath = paths["normal_air_csv"]

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Atmospheric reference file not found at: {filepath}")

    return pd.read_csv(filepath)


def load_coward_boundaries(filepath: Optional[str] = None) -> Tuple[pd.DataFrame, bool, str]:
    """
    Load Coward diagram boundaries.
    Returns:
        (DataFrame, is_verified, reference_note)
    """
    if filepath is None:
        paths = get_default_paths()
        filepath = paths["coward_csv"]

    if not os.path.exists(filepath):
        # Fall back to template note
        return pd.DataFrame(), False, "Coward zone boundaries pending verification from selected reference."

    try:
        df = pd.read_csv(filepath)
        # Check if coordinates are present
        if "CH4_percent" in df.columns and df["CH4_percent"].dropna().shape[0] > 0:
            is_verified = True
            ref_note = "Published USBM Bulletin 503 (Coward & Jones, 1952) / USBM Bulletin 627 (Zabetakis, 1965)"
            return df, is_verified, ref_note
        else:
            return df, False, "Coward zone boundaries pending verification from selected reference."
    except Exception as e:
        return pd.DataFrame(), False, f"Error reading boundary file: {str(e)}"
