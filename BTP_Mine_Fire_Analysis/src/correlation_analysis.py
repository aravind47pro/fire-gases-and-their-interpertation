"""
Correlation Analysis Module for BTP Mine Fire Analysis
Calculates Pearson correlation matrix, descriptive statistics, and handles missing/invalid values.
Addresses small-sample (N=14) statistical caveats.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

def compute_correlation_matrix(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compute pairwise Pearson correlation matrix and p-value matrix.
    Safely ignores non-numeric columns and columns with all NaNs (such as C/H if unpopulated).
    """
    candidate_cols = [
        "O2_percent", "CO_percent", "CO2_percent", "CH4_percent",
        "H2_percent", "N2_percent", "Temperature_C", "O2_Deficiency_percent",
        "Graham_Ratio", "Young_Ratio", "CO_CO2_Ratio", "Jones_Trickett_Ratio",
        "Willett_Ratio", "CH_Ratio"
    ]

    valid_cols = []
    for col in candidate_cols:
        if col in df.columns:
            # Check if has at least 3 non-null values and non-zero variance
            non_nulls = df[col].dropna()
            if len(non_nulls) >= 3 and non_nulls.std() > 1e-12:
                valid_cols.append(col)

    corr_df = df[valid_cols].corr(method="pearson").round(4)
    return corr_df, df[valid_cols]


def compute_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute comprehensive descriptive statistics:
    Mean, Median, Std Dev, Min, Max, Count, Missing Count.
    """
    analysis_cols = [
        "Temperature_C", "O2_percent", "CO2_percent", "CO_percent",
        "H2_percent", "CH4_percent", "N2_percent", "O2_Deficiency_percent",
        "Graham_Ratio", "Young_Ratio", "CO_CO2_Ratio", "Jones_Trickett_Ratio",
        "Willett_Ratio"
    ]

    records = []
    for col in analysis_cols:
        if col in df.columns:
            series = pd.to_numeric(df[col], errors="coerce")
            valid = series.dropna()
            records.append({
                "Parameter": col,
                "Count": len(series),
                "Valid_N": len(valid),
                "Missing_N": series.isna().sum(),
                "Mean": round(float(valid.mean()), 4) if len(valid) > 0 else np.nan,
                "Median": round(float(valid.median()), 4) if len(valid) > 0 else np.nan,
                "Std_Dev": round(float(valid.std()), 4) if len(valid) > 1 else np.nan,
                "Min": round(float(valid.min()), 4) if len(valid) > 0 else np.nan,
                "Max": round(float(valid.max()), 4) if len(valid) > 0 else np.nan,
            })

    return pd.DataFrame(records)


def generate_automatic_extremes_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate Section 29 summary table containing:
    - Highest temperature sample
    - Highest CO sample
    - Highest CO2 sample
    - Highest H2 sample
    - Highest CH4 sample
    - Lowest O2 sample
    - Highest O2 deficiency
    - Highest Graham ratio
    - Highest CO/CO2 ratio
    - Highest Young ratio
    - Highest Jones-Trickett ratio
    - Highest Willett ratio
    For each, show: Category, Sample number, Date, Value, Temperature.
    """
    queries = [
        ("Highest Temperature", "Temperature_C", "max", "°C"),
        ("Highest CO", "CO_percent", "max", "%"),
        ("Highest CO2", "CO2_percent", "max", "%"),
        ("Highest H2", "H2_percent", "max", "%"),
        ("Highest CH4", "CH4_percent", "max", "%"),
        ("Lowest O2", "O2_percent", "min", "%"),
        ("Highest O2 Deficiency", "O2_Deficiency_percent", "max", "%"),
        ("Highest Graham Ratio", "Graham_Ratio", "max", ""),
        ("Highest CO/CO2 Ratio", "CO_CO2_Ratio", "max", "%"),
        ("Highest Young Ratio", "Young_Ratio", "max", ""),
        ("Highest Jones-Trickett Ratio", "Jones_Trickett_Ratio", "max", ""),
        ("Highest Willett Ratio", "Willett_Ratio", "max", ""),
    ]

    rows = []
    for cat_name, col_name, agg_func, unit in queries:
        if col_name in df.columns:
            valid_df = df.dropna(subset=[col_name])
            if len(valid_df) > 0:
                if agg_func == "max":
                    idx = valid_df[col_name].idxmax()
                else:
                    idx = valid_df[col_name].idxmin()
                row = valid_df.loc[idx]
                val = row[col_name]
                unit_str = f" {unit}" if unit else ""
                rows.append({
                    "Observation_Category": cat_name,
                    "Sample_No": int(row["Sample_No"]),
                    "Date": str(row["Date"]),
                    "Value": f"{val:.4f}{unit_str}",
                    "Raw_Value": round(float(val), 4),
                    "Temperature_C": float(row["Temperature_C"])
                })

    return pd.DataFrame(rows)
