"""
Gas Indices Module for BTP Mine Fire Analysis
Calculates oxygen deficiency and standard mining engineering fire-gas ratios.
Handles zero/negative values safely without crashing or emitting misleading values.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

# Standard air reference factors (Volume-based)
STD_O2_VOL = 20.93
STD_N2_VOL = 79.04
O2_N2_RATIO = STD_O2_VOL / STD_N2_VOL  # 0.2648026... ≈ 0.265


def calculate_oxygen_deficiency(n2_percent: float, o2_percent: float) -> Tuple[float, str]:
    """
    Calculate literature-based oxygen deficiency:
    ΔO2 = (20.93 / 79.04) * N2 - O2

    Returns:
        (delta_o2, flag_status)
    """
    if pd.isna(n2_percent) or pd.isna(o2_percent):
        return np.nan, "Missing Data"

    delta_o2 = (O2_N2_RATIO * n2_percent) - o2_percent

    if delta_o2 <= 0:
        return round(delta_o2, 4), "Non-positive (ΔO2 ≤ 0)"
    elif delta_o2 < 0.3:
        return round(delta_o2, 4), "Low (< 0.3%, Graham ratio unreliable)"
    else:
        return round(delta_o2, 4), "Valid"


def calculate_graham_ratio(co_percent: float, delta_o2: float) -> Tuple[float, str, str]:
    """
    Graham Ratio = 100 * CO / ΔO2

    Returns:
        (ratio_value, status_flag, indicative_interpretation)
    """
    if pd.isna(co_percent) or pd.isna(delta_o2):
        return np.nan, "Missing Data", "No Data"

    if delta_o2 <= 0:
        return np.nan, "Invalid (ΔO2 ≤ 0)", "Cannot calculate (non-positive oxygen deficiency)"

    if delta_o2 < 0.3:
        # Literature warning: Graham ratio is numerically unstable when ΔO2 < 0.3%
        ratio = (100.0 * co_percent) / delta_o2
        return round(ratio, 4), "Unreliable (ΔO2 < 0.3%)", "Unreliable due to small ΔO2 (< 0.3%)"

    ratio = (100.0 * co_percent) / delta_o2

    # Indicative literature interpretation (Singh et al., 2007; Banerjee, 1985; Ray et al., 2004)
    if ratio <= 0.4:
        interp = "Normal / Background range (≤ 0.4)"
    elif ratio <= 0.5:
        interp = "Check condition (0.4 - 0.5)"
    elif ratio <= 1.0:
        interp = "Heating indication (0.5 - 1.0)"
    elif ratio <= 2.0:
        interp = "Serious heating (1.0 - 2.0)"
    elif ratio <= 7.0:
        interp = "Active fire indication (2.0 - 7.0)"
    else:
        interp = "Blazing / Advanced fire condition (≥ 7.0)"

    return round(ratio, 4), "Valid", interp


def calculate_young_ratio(co2_percent: float, delta_o2: float) -> Tuple[float, str]:
    """
    Young Ratio = 100 * CO2 / ΔO2

    Returns:
        (ratio_value, status_flag)
    Note: Young ratio alone does not prove fire severity due to carbonate reactions,
    strata gas, and CO2 solubility in mine waters.
    """
    if pd.isna(co2_percent) or pd.isna(delta_o2):
        return np.nan, "Missing Data"

    if delta_o2 <= 0:
        return np.nan, "Invalid (ΔO2 ≤ 0)"

    ratio = (100.0 * co2_percent) / delta_o2
    return round(ratio, 4), "Valid"


def calculate_co_co2_ratio(co_percent: float, co2_percent: float) -> Tuple[float, str]:
    """
    CO / CO2 Ratio = 100 * CO / CO2

    Returns:
        (ratio_value, status_flag)
    """
    if pd.isna(co_percent) or pd.isna(co2_percent):
        return np.nan, "Missing Data"

    if co2_percent <= 0:
        return np.nan, "Undefined (CO2 = 0)"

    ratio = (100.0 * co_percent) / co2_percent
    return round(ratio, 4), "Valid"


def calculate_jones_trickett_ratio(co2_percent: float, co_percent: float,
                                    h2_percent: float, delta_o2: float) -> Tuple[float, str, str]:
    """
    Jones-Trickett Ratio = (CO2 + 0.75 * CO - 0.25 * H2) / ΔO2

    Indicative fuel ranges:
    ~0.4 - 0.5: Methane combustion
    ~0.5 - 1.0: Coal, oil, or conveyor belt
    ~0.9 - 1.6: Timber / wood

    Returns:
        (ratio_value, status_flag, indicative_fuel)
    """
    if any(pd.isna(x) for x in [co2_percent, co_percent, h2_percent, delta_o2]):
        return np.nan, "Missing Data", "No Data"

    if delta_o2 <= 0:
        return np.nan, "Invalid (ΔO2 ≤ 0)", "Cannot calculate (non-positive ΔO2)"

    numerator = co2_percent + (0.75 * co_percent) - (0.25 * h2_percent)
    ratio = numerator / delta_o2

    if ratio < 0.4:
        fuel = "Below standard range (< 0.4, possible dilution/absorption)"
    elif ratio <= 0.5:
        fuel = "Methane-related range (0.4 - 0.5)"
    elif ratio <= 1.0:
        fuel = "Coal / oil / conveyor belt range (0.5 - 1.0)"
    elif ratio <= 1.6:
        fuel = "Timber / wood combustion range (0.9 - 1.6)"
    else:
        fuel = "Above standard range (> 1.6, possible external CO2 source)"

    return round(ratio, 4), "Valid", fuel


def calculate_willett_ratio(n2_percent: float, o2_percent: float,
                            co2_percent: float, co_percent: float,
                            h2_percent: float, ch4_percent: float) -> Tuple[float, str]:
    """
    Willett Ratio:
    Excess N2 = N2 - 3.8 * O2
    Combustibles = CO + H2 + CH4 (documented operational definition)
    Willett Ratio = CO2 / (Excess N2 + CO2 + Combustibles)

    Returns:
        (ratio_value, status_flag)
    """
    if any(pd.isna(x) for x in [n2_percent, o2_percent, co2_percent, co_percent, h2_percent, ch4_percent]):
        return np.nan, "Missing Data"

    excess_n2 = n2_percent - (3.8 * o2_percent)
    combustibles = co_percent + h2_percent + ch4_percent
    denominator = excess_n2 + co2_percent + combustibles

    if denominator <= 0:
        return np.nan, "Invalid (Denominator ≤ 0)"

    ratio = co2_percent / denominator
    return round(ratio, 4), "Valid"


def calculate_all_indices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process full dataframe and append all fire gas calculations, flags, and interpretations.
    """
    result = df.copy()

    # Lists for new columns
    o2_def_list, o2_def_flag = [], []
    graham_list, graham_flag, graham_interp = [], [], []
    young_list, young_flag = [], []
    co_co2_list, co_co2_flag = [], []
    jt_list, jt_flag, jt_fuel = [], [], []
    willett_list, willett_flag = [], []
    excess_n2_list = []
    ch_list, ch_note = [], []

    for _, row in result.iterrows():
        n2 = row["N2_percent"]
        o2 = row["O2_percent"]
        co2 = row["CO2_percent"]
        co = row["CO_percent"]
        h2 = row["H2_percent"]
        ch4 = row["CH4_percent"]

        # 1. Oxygen Deficiency
        d_o2, d_flag = calculate_oxygen_deficiency(n2, o2)
        o2_def_list.append(d_o2)
        o2_def_flag.append(d_flag)

        # 2. Graham Ratio
        g_val, g_flag, g_desc = calculate_graham_ratio(co, d_o2)
        graham_list.append(g_val)
        graham_flag.append(g_flag)
        graham_interp.append(g_desc)

        # 3. Young Ratio
        y_val, y_flag = calculate_young_ratio(co2, d_o2)
        young_list.append(y_val)
        young_flag.append(y_flag)

        # 4. CO / CO2 Ratio
        c_val, c_flag = calculate_co_co2_ratio(co, co2)
        co_co2_list.append(c_val)
        co_co2_flag.append(c_flag)

        # 5. Jones-Trickett Ratio
        jt_val, jt_fl, jt_desc = calculate_jones_trickett_ratio(co2, co, h2, d_o2)
        jt_list.append(jt_val)
        jt_flag.append(jt_fl)
        jt_fuel.append(jt_desc)

        # 6. Willett Ratio
        exc_n2 = n2 - (3.8 * o2)
        excess_n2_list.append(round(exc_n2, 4))
        w_val, w_fl = calculate_willett_ratio(n2, o2, co2, co, h2, ch4)
        willett_list.append(w_val)
        willett_flag.append(w_fl)

        # 7. C/H Ratio (Do not invent formula without verified reference)
        ch_list.append(np.nan)
        ch_note.append("REFERENCE REQUIRED (Definition varies across mining literature)")

    result["O2_Deficiency_percent"] = o2_def_list
    result["O2_Deficiency_Flag"] = o2_def_flag
    result["Graham_Ratio"] = graham_list
    result["Graham_Flag"] = graham_flag
    result["Graham_Interpretation"] = graham_interp
    result["Young_Ratio"] = young_list
    result["Young_Flag"] = young_flag
    result["CO_CO2_Ratio"] = co_co2_list
    result["CO_CO2_Flag"] = co_co2_flag
    result["Jones_Trickett_Ratio"] = jt_list
    result["Jones_Trickett_Flag"] = jt_flag
    result["Jones_Trickett_Fuel"] = jt_fuel
    result["Excess_N2_percent"] = excess_n2_list
    result["Willett_Ratio"] = willett_list
    result["Willett_Flag"] = willett_flag
    result["CH_Ratio"] = ch_list
    result["CH_Ratio_Note"] = ch_note

    return result
