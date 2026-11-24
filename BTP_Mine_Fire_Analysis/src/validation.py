"""
Validation Module for BTP Mine Fire Gas Analysis
Validates gas composition sums against 100% tolerance without altering raw field data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

def validate_gas_composition(df: pd.DataFrame, tolerance_percent: float = 1.0) -> pd.DataFrame:
    """
    Validate the sum of mine fire gases:
    Gas Sum = O2 + N2 + CO2 + CO + H2 + CH4
    Difference from 100% = Gas Sum - 100.0%

    Rules:
    - Never modify raw data to force 100%.
    - Check if difference is within acceptable analytical tolerance (default 1.0%).
    - Assign clear status strings: 'Valid (Within Tolerance)' or 'Warning: Exceeds Tolerance'.
    """
    validated_df = df.copy()

    gas_cols = ["O2_percent", "N2_percent", "CO2_percent", "CO_percent", "H2_percent", "CH4_percent"]
    for col in gas_cols:
        if col not in validated_df.columns:
            raise KeyError(f"Missing gas column for validation: {col}")

    # Calculate sum
    validated_df["Gas_Sum_percent"] = validated_df[gas_cols].sum(axis=1).round(4)
    validated_df["Diff_from_100_percent"] = (validated_df["Gas_Sum_percent"] - 100.0).round(4)
    validated_df["Abs_Diff_percent"] = validated_df["Diff_from_100_percent"].abs().round(4)

    # Status assignment
    def get_status(diff):
        if np.isnan(diff):
            return "Invalid / Missing Data"
        elif diff <= tolerance_percent:
            return f"Valid (Within ±{tolerance_percent}%)"
        else:
            return f"Warning (Diff > ±{tolerance_percent}%)"

    validated_df["Validation_Status"] = validated_df["Abs_Diff_percent"].apply(get_status)

    return validated_df


def get_validation_summary(validated_df: pd.DataFrame) -> Dict[str, Any]:
    """Provide overall summary statistics of gas composition validation."""
    sums = validated_df["Gas_Sum_percent"]
    diffs = validated_df["Diff_from_100_percent"]

    summary = {
        "Total_Samples": len(validated_df),
        "Mean_Gas_Sum": round(float(sums.mean()), 4),
        "Min_Gas_Sum": round(float(sums.min()), 4),
        "Max_Gas_Sum": round(float(sums.max()), 4),
        "Std_Gas_Sum": round(float(sums.std()), 4),
        "Mean_Abs_Difference": round(float(validated_df["Abs_Diff_percent"].mean()), 4),
        "Max_Abs_Difference": round(float(validated_df["Abs_Diff_percent"].max()), 4),
        "All_Valid": bool((validated_df["Validation_Status"].str.startswith("Valid")).all()),
    }
    return summary
