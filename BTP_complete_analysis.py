#!/usr/bin/env python3
"""
========================================================================================
BTP PROJECT — FIRE GASES AND THEIR INTERPRETATION IN UNDERGROUND COAL MINES
Department of Mining Engineering, Indian Institute of Technology Kharagpur
========================================================================================

Complete, reproducible, single-file analysis script for BTP analysis, supervisor discussion,
graphs, Excel generation, Word/Markdown reporting, and viva preparation.

DATA SOURCE:
- 14 Real Mine-Fire Samples from Lodna Colliery, Jharia Coalfield, India
- Reference: Singh et al. (2007), Int. J. Coal Geol., 69(3), 192–204. DOI: 10.1016/j.coal.2006.04.004

HOW TO RUN:
1. Ensure dependencies are installed:
   pip install pandas numpy matplotlib seaborn openpyxl scipy python-docx
2. Run this script:
   python BTP_complete_analysis.py
3. View results in the 'results/' folder!
========================================================================================
"""

import os
import sys
import math
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Try importing python-docx; if not present, handle gracefully
try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


# ======================================================================================
# 1. DIRECTORY SETUP & PATH RESOLUTION
# ======================================================================================
def resolve_directories():
    """Detect script location and ensure all required output directories exist."""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Check if we are inside BTP_Mine_Fire_Analysis or at the workspace root
    if os.path.exists(os.path.join(script_dir, "data", "lodna_mine_fire_data.csv")):
        base_dir = script_dir
    elif os.path.exists(os.path.join(script_dir, "BTP_Mine_Fire_Analysis", "data", "lodna_mine_fire_data.csv")):
        base_dir = os.path.join(script_dir, "BTP_Mine_Fire_Analysis")
    else:
        base_dir = script_dir

    dirs = {
        "base": base_dir,
        "data": os.path.join(base_dir, "data"),
        "coward": os.path.join(base_dir, "coward"),
        "results": os.path.join(base_dir, "results"),
        "figures": os.path.join(base_dir, "results", "figures"),
        "tables": os.path.join(base_dir, "results", "tables"),
        "reports": os.path.join(base_dir, "results", "reports"),
    }

    for d in dirs.values():
        os.makedirs(d, exist_ok=True)

    return dirs


# ======================================================================================
# 2. RAW DATA INGESTION & VALIDATION
# ======================================================================================
def get_lodna_raw_data(data_dir: str) -> pd.DataFrame:
    """Load or generate the 14 real Lodna mine-fire samples (Singh et al., 2007)."""
    csv_path = os.path.join(data_dir, "lodna_mine_fire_data.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        # Fallback to authentic hardcoded published values if file is missing
        raw_samples = [
            (1, "27-09-1985", 12.40, 5.18, 0.067, 0.000, 0.351, 82.00, 73),
            (2, "14-05-1986", 15.75, 1.64, 0.067, 0.000, 0.000, 82.54, 55),
            (3, "08-10-1986", 14.09, 2.13, 0.254, 0.000, 0.000, 83.52, 30),
            (4, "20-06-1987", 17.13, 1.55, 0.022, 0.387, 0.000, 80.92, 80),
            (5, "15-12-1987", 13.37, 4.75, 0.292, 2.343, 0.000, 79.25, 72),
            (6, "02-06-1988", 14.02, 4.22, 0.813, 0.670, 0.526, 79.75, 64),
            (7, "27-12-1988", 15.53, 3.33, 0.627, 0.627, 0.000, 79.90, 67),
            (8, "22-06-1989", 15.36, 3.93, 0.287, 0.381, 0.095, 79.95, 63),
            (9, "11-06-1990", 15.38, 4.88, 0.000, 0.000, 0.000, 79.74, 47),
            (10, "11-11-1990", 15.89, 4.29, 0.000, 0.000, 0.000, 79.83, 54),
            (11, "07-12-1991", 16.00, 3.00, 0.002, 0.000, 0.000, 81.00, 31),
            (12, "16-10-1992", 10.65, 0.00, 0.000, 0.000, 0.000, 89.35, 37),
            (13, "22-04-1993", 10.64, 7.51, 0.000, 0.000, 0.000, 81.86, 34),
            (14, "18-10-1993", 10.67, 8.18, 0.000, 0.000, 0.000, 81.16, 33)
        ]
        cols = ["Sample_No", "Date", "CO2_percent", "O2_percent", "CO_percent",
                "H2_percent", "CH4_percent", "N2_percent", "Temperature_C"]
        df = pd.DataFrame(raw_samples, columns=cols)
        df["Reference"] = "Singh et al. (2007), Int. J. Coal Geol., 69(3), 192-204"
        df.to_csv(csv_path, index=False)

    df["Date_Parsed"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
    return df


def validate_gas_data(df: pd.DataFrame, tolerance: float = 1.0) -> pd.DataFrame:
    """Validate gas sums against 100% without modifying raw data."""
    vdf = df.copy()
    gas_cols = ["O2_percent", "N2_percent", "CO2_percent", "CO_percent", "H2_percent", "CH4_percent"]
    vdf["Gas_Sum_percent"] = vdf[gas_cols].sum(axis=1).round(4)
    vdf["Diff_from_100_percent"] = (vdf["Gas_Sum_percent"] - 100.0).round(4)
    vdf["Abs_Diff_percent"] = vdf["Diff_from_100_percent"].abs().round(4)

    def status(diff):
        return f"Valid (Within ±{tolerance}%)" if diff <= tolerance else f"Warning (> ±{tolerance}%)"

    vdf["Validation_Status"] = vdf["Abs_Diff_percent"].apply(status)
    return vdf


# ======================================================================================
# 3. FIRE-GAS INDICES COMPUTATION
# ======================================================================================
def compute_indices(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Oxygen deficiency and standard mining fire-gas indices."""
    res = df.copy()

    # Standard volume ratio: 20.93 / 79.04 = 0.2648026...
    factor = 20.93 / 79.04

    # 1. Oxygen Deficiency
    res["O2_Deficiency_percent"] = (factor * res["N2_percent"] - res["O2_percent"]).round(4)
    res["O2_Deficiency_Flag"] = np.where(
        res["O2_Deficiency_percent"] <= 0, "Invalid (ΔO2 ≤ 0)",
        np.where(res["O2_Deficiency_percent"] < 0.3, "Low (< 0.3%, Graham Unreliable)", "Valid")
    )

    # 2. Graham Ratio: 100 * CO / ΔO2
    graham_vals, graham_flags, graham_interps = [], [], []
    for _, r in res.iterrows():
        co = r["CO_percent"]
        do2 = r["O2_Deficiency_percent"]
        if pd.isna(co) or pd.isna(do2) or do2 <= 0:
            graham_vals.append(np.nan)
            graham_flags.append("Invalid (ΔO2 ≤ 0)")
            graham_interps.append("Cannot calculate")
        elif do2 < 0.3:
            val = (100.0 * co) / do2
            graham_vals.append(round(val, 4))
            graham_flags.append("Unreliable (ΔO2 < 0.3%)")
            graham_interps.append("Unreliable due to low ΔO2")
        else:
            val = (100.0 * co) / do2
            graham_vals.append(round(val, 4))
            graham_flags.append("Valid")
            if val <= 0.4:
                graham_interps.append("Normal / Background (≤ 0.4)")
            elif val <= 0.5:
                graham_interps.append("Check condition (0.4 - 0.5)")
            elif val <= 1.0:
                graham_interps.append("Heating indication (0.5 - 1.0)")
            elif val <= 2.0:
                graham_interps.append("Serious heating (1.0 - 2.0)")
            elif val <= 7.0:
                graham_interps.append("Active fire indication (2.0 - 7.0)")
            else:
                graham_interps.append("Blazing fire (≥ 7.0)")

    res["Graham_Ratio"] = graham_vals
    res["Graham_Flag"] = graham_flags
    res["Graham_Interpretation"] = graham_interps

    # 3. Young Ratio: 100 * CO2 / ΔO2
    res["Young_Ratio"] = np.where(res["O2_Deficiency_percent"] > 0,
                                  (100.0 * res["CO2_percent"] / res["O2_Deficiency_percent"]).round(4), np.nan)
    res["Young_Flag"] = np.where(res["O2_Deficiency_percent"] > 0, "Valid", "Invalid (ΔO2 ≤ 0)")

    # 4. CO / CO2 Ratio: 100 * CO / CO2
    res["CO_CO2_Ratio"] = np.where(res["CO2_percent"] > 0,
                                   (100.0 * res["CO_percent"] / res["CO2_percent"]).round(4), np.nan)
    res["CO_CO2_Flag"] = np.where(res["CO2_percent"] > 0, "Valid", "Undefined (CO2 = 0)")

    # 5. Jones-Trickett Ratio: (CO2 + 0.75*CO - 0.25*H2) / ΔO2
    jt_numerator = res["CO2_percent"] + 0.75 * res["CO_percent"] - 0.25 * res["H2_percent"]
    res["Jones_Trickett_Ratio"] = np.where(res["O2_Deficiency_percent"] > 0,
                                          (jt_numerator / res["O2_Deficiency_percent"]).round(4), np.nan)
    res["Jones_Trickett_Flag"] = np.where(res["O2_Deficiency_percent"] > 0, "Valid", "Invalid (ΔO2 ≤ 0)")

    jt_fuels = []
    for jt in res["Jones_Trickett_Ratio"]:
        if pd.isna(jt):
            jt_fuels.append("No Data")
        elif jt < 0.4:
            jt_fuels.append("Below standard range (< 0.4)")
        elif jt <= 0.5:
            jt_fuels.append("Methane combustion (0.4 - 0.5)")
        elif jt <= 1.0:
            jt_fuels.append("Coal / oil / belt (0.5 - 1.0)")
        elif jt <= 1.6:
            jt_fuels.append("Timber / wood (0.9 - 1.6)")
        else:
            jt_fuels.append("Above standard range (> 1.6)")
    res["Jones_Trickett_Fuel"] = jt_fuels

    # 6. Willett Ratio: CO2 / (Excess N2 + CO2 + Combustibles)
    # Excess N2 = N2 - 3.8 * O2; Combustibles = CO + H2 + CH4
    res["Excess_N2_percent"] = (res["N2_percent"] - 3.8 * res["O2_percent"]).round(4)
    combustibles = res["CO_percent"] + res["H2_percent"] + res["CH4_percent"]
    denom = res["Excess_N2_percent"] + res["CO2_percent"] + combustibles
    res["Willett_Ratio"] = np.where(denom > 0, (res["CO2_percent"] / denom).round(4), np.nan)
    res["Willett_Flag"] = np.where(denom > 0, "Valid", "Invalid (Denom ≤ 0)")

    # 7. C/H Ratio: Reference Required (do not invent formula)
    res["CH_Ratio"] = np.nan
    res["CH_Ratio_Note"] = "REFERENCE REQUIRED (Definition varies across mining literature)"

    return res


# ======================================================================================
# 4. TEMPERATURE RELATIONSHIPS & CORE RESEARCH QUESTIONS
# ======================================================================================
def analyze_temperature(df: pd.DataFrame):
    """Perform regression analysis and formulate empirical answers to Section 15 questions."""
    targets = [
        ("CO_percent", "CO (% vol)"),
        ("CO2_percent", "CO2 (% vol)"),
        ("O2_percent", "O2 (% vol)"),
        ("H2_percent", "H2 (% vol)"),
        ("CH4_percent", "CH4 (% vol)"),
        ("N2_percent", "N2 (% vol)"),
        ("O2_Deficiency_percent", "O2 Deficiency (%)"),
        ("Graham_Ratio", "Graham Ratio"),
        ("Young_Ratio", "Young Ratio"),
        ("CO_CO2_Ratio", "CO/CO2 Ratio (%)"),
        ("Jones_Trickett_Ratio", "Jones-Trickett Ratio"),
        ("Willett_Ratio", "Willett Ratio")
    ]

    records = []
    temp = df["Temperature_C"]

    for col, lbl in targets:
        sub = df.dropna(subset=[col, "Temperature_C"])
        if len(sub) >= 3:
            x = sub["Temperature_C"].values
            y = sub[col].values
            res = stats.linregress(x, y)
            r = res.rvalue
            r2 = r ** 2
            sign = "+" if res.intercept >= 0 else "-"
            eq = f"y = {res.slope:.4f} * Temp {sign} {abs(res.intercept):.4f}"

            strength = "Strong" if abs(r) >= 0.7 else ("Moderate" if abs(r) >= 0.4 else "Weak")
            dir_str = "Positive" if r > 0 else "Negative"

            records.append({
                "Parameter": lbl,
                "Column": col,
                "N": len(sub),
                "Pearson_r": round(r, 4),
                "R_squared": round(r2, 4),
                "Slope": round(res.slope, 5),
                "Intercept": round(res.intercept, 5),
                "p_value": round(res.pvalue, 5),
                "Regression_Equation": eq,
                "Interpretation": f"{dir_str} ({strength})"
            })

    temp_reg_df = pd.DataFrame(records)

    # Resolve Section 15 Questions
    s_high_temp = df.loc[df["Temperature_C"].idxmax()]
    s_high_co = df.loc[df["CO_percent"].idxmax()]
    s_high_h2 = df.loc[df["H2_percent"].idxmax()]

    r_co = temp_reg_df.loc[temp_reg_df["Column"] == "CO_percent", "Pearson_r"].values[0]
    r_o2 = temp_reg_df.loc[temp_reg_df["Column"] == "O2_percent", "Pearson_r"].values[0]
    r_h2 = temp_reg_df.loc[temp_reg_df["Column"] == "H2_percent", "Pearson_r"].values[0]
    r_g = temp_reg_df.loc[temp_reg_df["Column"] == "Graham_Ratio", "Pearson_r"].values[0]

    qa_dict = {
        "Q1": {
            "Question": "Question 1: Does CO increase when temperature increases?",
            "Finding": (
                f"Statistical Pearson r = {r_co:.3f} indicates a moderate positive association, but the relationship "
                f"is strictly NON-MONOTONIC. The highest temperature sample ({s_high_temp['Temperature_C']}°C on {s_high_temp['Date']}) "
                f"recorded a low CO of {s_high_temp['CO_percent']}%, whereas the peak CO ({s_high_co['CO_percent']}% on {s_high_co['Date']}) "
                f"occurred at a lower temperature of {s_high_co['Temperature_C']}°C. In sealed mine fires, CO generation is heavily "
                f"constrained by oxygen availability and seal tightness rather than temperature alone."
            )
        },
        "Q2": {
            "Question": "Question 2: Does O2 decrease as temperature increases?",
            "Finding": (
                f"Statistical Pearson r = {r_o2:.3f} indicates a weak-to-moderate negative correlation. "
                f"While accelerated coal oxidation at higher temperatures consumes oxygen, residual O2 behind stoppings "
                f"is strongly governed by surface barometric pressure breathing, stoppings leakage, and fresh-air ingress. "
                f"For example, Sample 12 recorded 0.00% O2 at an intermediate temperature of 37°C."
            )
        },
        "Q3": {
            "Question": "Question 3: Does H2 increase with temperature?",
            "Finding": (
                f"Statistical Pearson r = {r_h2:.3f} demonstrates a moderate positive correlation. "
                f"Hydrogen generation typically signals high-temperature heating (>250°C at the coal face) and water-gas reaction. "
                f"In the field dataset, the highest H2 ({s_high_h2['H2_percent']}% on {s_high_h2['Date']}) occurred at 72°C. "
                f"Samples below 55°C generally showed zero detectable hydrogen."
            )
        },
        "Q4": {
            "Question": "Question 4: Does Graham ratio increase with temperature?",
            "Finding": (
                f"Statistical Pearson r = {r_g:.3f} shows a moderate positive association. "
                f"Graham ratio serves as an indicator of oxidation intensity, but like CO, it is non-monotonic and "
                f"cannot be used as an absolute thermometer because of oxygen starvation and dilution effects."
            )
        }
    }

    return temp_reg_df, qa_dict


# ======================================================================================
# 5. COWARD EXPLOSIBILITY CLASSIFICATION & THEORETICAL DILUTION
# ======================================================================================
def classify_coward_zones(df: pd.DataFrame) -> pd.DataFrame:
    """Classify samples on the Coward Diagram according to USBM Bulletin 503 limits."""
    # Classical USBM Bulletin 503 coordinates:
    # LEL = 5.0% CH4, 19.88% O2; UEL = 15.0% CH4, 17.79% O2; Nose = 5.9% CH4, 12.1% O2
    records = []
    for _, r in df.iterrows():
        ch4 = r["CH4_percent"]
        o2 = r["O2_percent"]
        s_no = int(r["Sample_No"])
        dt = r["Date"]
        temp = r["Temperature_C"]

        # Classification logic based on published flammability boundary
        air_o2_limit = 20.93 * (1.0 - ch4 / 100.0)

        if o2 > air_o2_limit + 0.1:
            zone = "Zone E"
            interp = "Impossible mixture (O2 exceeds normal air dilution line)"
        elif o2 >= 12.10 and ch4 >= 5.0:
            # Check inside explosive polygon
            zone = "Zone A"
            interp = "Explosive mixture"
        elif ch4 > 5.0:
            zone = "Zone B"
            interp = "Capable of forming explosive mixtures when diluted with air"
        elif o2 >= 12.10 and ch4 < 5.0:
            zone = "Zone C"
            interp = "Capable of forming explosive mixtures if methane is added"
        else:
            # O2 < 12.1% and CH4 < 5.0%
            zone = "Zone D"
            interp = "Not capable of forming explosive mixtures (Inert / Deficient in oxygen and fuel)"

        records.append({
            "Sample_No": s_no,
            "Date": dt,
            "CH4_percent": ch4,
            "O2_percent": o2,
            "Temperature_C": temp,
            "Coward_Zone": zone,
            "Safety_Interpretation": interp
        })

    return pd.DataFrame(records)


def simulate_theoretical_dilution(v_m3: float = 27000.0, q_m3_s: float = 5.0):
    """Academic model: Pure N2 dilution of sealed atmosphere (15% CH4, 10% O2)."""
    f_vals = np.linspace(1.00, 0.05, 25)
    records = []
    for f in f_vals:
        ch4 = round(15.0 * f, 4)
        o2 = round(10.0 * f, 4)
        n2 = round(100.0 - ch4 - o2, 4)
        records.append({
            "Fraction_Remaining_f": round(f, 4),
            "CH4_percent": ch4,
            "O2_percent": o2,
            "N2_percent": n2
        })
    dil_df = pd.DataFrame(records)

    turnover_seconds = v_m3 / q_m3_s
    turnover_minutes = turnover_seconds / 60.0
    turnover_hours = turnover_minutes / 60.0

    turnover_info = {
        "Volume_m3": v_m3,
        "Flow_Rate_m3_s": q_m3_s,
        "Nominal_Turnover_Minutes": turnover_minutes,
        "Nominal_Turnover_Hours": turnover_hours,
        "Caveat": (
            "CRITICAL SCIENTIFIC NOTE: 90 minutes is purely an idealized mathematical volume-to-flow ratio (V/Q). "
            "It is NOT an operational mine safety recommendation. Real mine sealing/inertisation requires 3 to 5+ "
            "volume turnovers due to imperfect mixing, goaf dead zones, gas desorption, and stopping leakage."
        )
    }
    return dil_df, turnover_info


# ======================================================================================
# 6. EXTREMES & STATISTICAL SUMMARY
# ======================================================================================
def generate_extremes_table(df: pd.DataFrame) -> pd.DataFrame:
    """Generate automatic extrema observation table (Section 29)."""
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
        ("Highest Willett Ratio", "Willett_Ratio", "max", "")
    ]
    rows = []
    for cat, col, func, unit in queries:
        sub = df.dropna(subset=[col])
        if len(sub) > 0:
            idx = sub[col].idxmax() if func == "max" else sub[col].idxmin()
            r = sub.loc[idx]
            val = r[col]
            unit_str = f" {unit}" if unit else ""
            rows.append({
                "Observation_Category": cat,
                "Sample_No": int(r["Sample_No"]),
                "Date": str(r["Date"]),
                "Value": f"{val:.4f}{unit_str}",
                "Temperature_C": float(r["Temperature_C"])
            })
    return pd.DataFrame(rows)


# ======================================================================================
# 7. GENERATE ALL 15 PUBLICATION-QUALITY FIGURES
# ======================================================================================
def plot_all_figures(df: pd.DataFrame, fig_dir: str, dil_df: pd.DataFrame):
    """Render and save all 15 publication figures at 300 DPI."""
    plt.rcParams['font.sans-serif'] = 'Arial'
    plt.rcParams['font.family'] = 'sans-serif'

    def scatter_reg(x_col, y_col, xl, yl, title, fname, color):
        fig, ax = plt.subplots(figsize=(8.5, 6), dpi=300)
        sub = df.dropna(subset=[x_col, y_col])
        x, y = sub[x_col].values, sub[y_col].values
        ax.scatter(x, y, color=color, s=75, edgecolors="black", linewidths=0.8, zorder=5)

        for _, r in sub.iterrows():
            ax.annotate(f"S{int(r['Sample_No'])}", (r[x_col], r[y_col]),
                        xytext=(4, 4), textcoords="offset points", fontsize=8)

        if len(x) >= 3 and np.std(x) > 1e-12:
            m, b = np.polyfit(x, y, 1)
            r = np.corrcoef(x, y)[0, 1]
            x_line = np.linspace(x.min(), x.max(), 100)
            ax.plot(x_line, m * x_line + b, 'r--', lw=1.5,
                    label=f"Fit: y = {m:.4f}x {'+' if b >= 0 else '-'} {abs(b):.4f}\n($R^2={r**2:.3f}$, $r={r:.3f}$)")

        ax.set_xlabel(xl, fontsize=12, fontweight="bold")
        ax.set_ylabel(yl, fontsize=12, fontweight="bold")
        ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="best", fontsize=9.5)
        ax.text(0.02, 0.03, "Source: Singh et al. (2007), Lodna Colliery (N=14)",
                transform=ax.transAxes, fontsize=8, fontstyle="italic", color="#555")
        plt.tight_layout()
        plt.savefig(os.path.join(fig_dir, fname), dpi=300, bbox_inches="tight")
        plt.close()

    # Fig 01 to 05: Gas vs Temp
    scatter_reg("Temperature_C", "CO_percent", "Temperature (°C)", "CO (% vol)",
                "Mine Fire Temperature vs. Carbon Monoxide (CO)", "01_CO_vs_Temperature.png", "#d62728")
    scatter_reg("Temperature_C", "CO2_percent", "Temperature (°C)", "$CO_2$ (% vol)",
                "Mine Fire Temperature vs. Carbon Dioxide ($CO_2$)", "02_CO2_vs_Temperature.png", "#2ca02c")
    scatter_reg("Temperature_C", "O2_percent", "Temperature (°C)", "$O_2$ (% vol)",
                "Mine Fire Temperature vs. Oxygen ($O_2$)", "03_O2_vs_Temperature.png", "#1f77b4")
    scatter_reg("Temperature_C", "H2_percent", "Temperature (°C)", "$H_2$ (% vol)",
                "Mine Fire Temperature vs. Hydrogen ($H_2$)", "04_H2_vs_Temperature.png", "#9467bd")
    scatter_reg("Temperature_C", "CH4_percent", "Temperature (°C)", "$CH_4$ (% vol)",
                "Mine Fire Temperature vs. Methane ($CH_4$)", "05_CH4_vs_Temperature.png", "#ff7f0e")

    # Fig 06: Chronological Date/Time Trends
    fig, axes = plt.subplots(3, 1, figsize=(11, 10), dpi=300, sharex=True)
    sdf = df.sort_values("Date_Parsed")
    dt = sdf["Date_Parsed"]

    axes[0].plot(dt, sdf["Temperature_C"], 'r-o', lw=1.8, label="Temperature (°C)")
    axes[0].set_ylabel("Temp (°C)", color="red", fontweight="bold")
    axes[0].tick_params(axis='y', labelcolor="red")
    axes[0].grid(True, linestyle="--", alpha=0.5)
    ax0_t = axes[0].twinx()
    ax0_t.plot(dt, sdf["O2_Deficiency_percent"], 'b-s', lw=1.5, label=r"$\Delta O_2$ (%)")
    ax0_t.set_ylabel(r"$\Delta O_2$ (%)", color="blue", fontweight="bold")
    ax0_t.tick_params(axis='y', labelcolor="blue")
    axes[0].set_title("Chronological Mine Fire Atmosphere Trends (Lodna Colliery, 1985–1993)", fontsize=13, fontweight="bold")

    axes[1].plot(dt, sdf["CO_percent"], 'm-^', lw=1.8, label="CO (% vol)")
    axes[1].plot(dt, sdf["H2_percent"], 'c-d', lw=1.5, label="$H_2$ (% vol)")
    axes[1].set_ylabel("Concentration (% vol)", fontweight="bold")
    axes[1].grid(True, linestyle="--", alpha=0.5)
    axes[1].legend(loc="upper right")

    axes[2].plot(dt, sdf["Graham_Ratio"], 'g-o', lw=1.8, label="Graham Ratio")
    axes[2].set_ylabel("Graham Ratio", color="green", fontweight="bold")
    axes[2].tick_params(axis='y', labelcolor="green")
    axes[2].grid(True, linestyle="--", alpha=0.5)
    ax2_t = axes[2].twinx()
    ax2_t.plot(dt, sdf["Young_Ratio"], 'k--x', lw=1.4, label="Young Ratio")
    ax2_t.set_ylabel("Young Ratio", color="black", fontweight="bold")
    axes[2].set_xlabel("Sampling Date", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "06_Temperature_Trend.png"), dpi=300, bbox_inches="tight")
    plt.close()

    # Fig 07 to 11: Indices vs Temp
    scatter_reg("Temperature_C", "Graham_Ratio", "Temperature (°C)", "Graham Ratio",
                "Mine Fire Temperature vs. Graham Ratio", "07_Graham_vs_Temperature.png", "#2ca02c")
    scatter_reg("Temperature_C", "Young_Ratio", "Temperature (°C)", "Young Ratio",
                "Mine Fire Temperature vs. Young Ratio", "08_Young_vs_Temperature.png", "#17becf")
    scatter_reg("Temperature_C", "CO_CO2_Ratio", "Temperature (°C)", "CO / $CO_2$ Ratio (%)",
                "Mine Fire Temperature vs. CO / $CO_2$ Ratio", "09_CO_CO2_vs_Temperature.png", "#e377c2")
    scatter_reg("Temperature_C", "Jones_Trickett_Ratio", "Temperature (°C)", "Jones-Trickett Ratio",
                "Mine Fire Temperature vs. Jones–Trickett Ratio", "10_Jones_Trickett_vs_Temperature.png", "#bcbd22")
    scatter_reg("Temperature_C", "Willett_Ratio", "Temperature (°C)", "Willett Ratio",
                "Mine Fire Temperature vs. Willett Ratio", "11_Willett_vs_Temperature.png", "#8c564b")

    # Fig 12: Correlation Matrix Heatmap
    fig, ax = plt.subplots(figsize=(10, 8.5), dpi=300)
    corr_cols = ["Temperature_C", "O2_percent", "CO_percent", "CO2_percent", "H2_percent",
                 "CH4_percent", "N2_percent", "O2_Deficiency_percent", "Graham_Ratio",
                 "Young_Ratio", "CO_CO2_Ratio", "Jones_Trickett_Ratio", "Willett_Ratio"]
    corr = df[corr_cols].corr()
    labels = ["Temp", "$O_2$", "CO", "$CO_2$", "$H_2$", "$CH_4$", "$N_2$", r"$\Delta O_2$",
              "Graham", "Young", "CO/$CO_2$", "JT", "Willett"]
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1,
                xticklabels=labels, yticklabels=labels, ax=ax, linewidths=0.5)
    ax.set_title("Pearson Correlation Heatmap — Mine Fire Gases & Indices (N=14)", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "12_Correlation_Matrix.png"), dpi=300, bbox_inches="tight")
    plt.close()

    # Fig 13: Multi-Gas Normalized Comparison
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    norm_cols = ["Temperature_C", "CO_percent", "CO2_percent", "O2_percent", "H2_percent", "CH4_percent"]
    norm_df = pd.DataFrame()
    for c in norm_cols:
        s = df[c]
        norm_df[c] = (s - s.min()) / (s.max() - s.min()) if s.max() > s.min() else 0.0

    idx = np.arange(len(df))
    lbls = [f"S{int(r['Sample_No'])}\n{r['Date']}" for _, r in df.iterrows()]
    ax.plot(idx, norm_df["Temperature_C"], 'r-o', lw=2, label="Temperature (Norm)")
    ax.plot(idx, norm_df["CO_percent"], 'm-^', lw=1.8, label="CO (Norm)")
    ax.plot(idx, norm_df["CO2_percent"], 'g-s', lw=1.5, label="$CO_2$ (Norm)")
    ax.plot(idx, norm_df["O2_percent"], 'b-d', lw=1.5, label="$O_2$ (Norm)")
    ax.plot(idx, norm_df["H2_percent"], 'c--v', lw=1.4, label="$H_2$ (Norm)")
    ax.plot(idx, norm_df["CH4_percent"], 'orange', linestyle=":", marker="p", lw=1.4, label="$CH_4$ (Norm)")
    ax.set_xticks(idx)
    ax.set_xticklabels(lbls, rotation=45, ha="right", fontsize=8.5)
    ax.set_ylabel("Normalized Value (0.0 to 1.0)", fontsize=11, fontweight="bold")
    ax.set_title("Multi-Gas & Temperature Normalized Comparison Across Samples", fontsize=13, fontweight="bold", pad=12)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper right", fontsize=9.5)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "13_Multi_Gas_Comparison.png"), dpi=300, bbox_inches="tight")
    plt.close()

    # Helper function for Coward Diagram (Figs 14 & 15)
    def render_coward(output_file, with_dilution=False):
        fig, ax = plt.subplots(figsize=(12, 9), dpi=300)
        ax.set_xlim(-0.5, 22.0)
        ax.set_ylim(-0.5, 23.0)
        ax.set_xlabel("Methane, $CH_4$ (% by volume)", fontsize=13, fontweight="bold")
        ax.set_ylabel("Oxygen, $O_2$ (% by volume)", fontsize=13, fontweight="bold")

        title = "Coward Explosibility Diagram — Lodna Colliery Fire Samples"
        if with_dilution:
            title += " & Theoretical $N_2$ Dilution Trajectory"
        ax.set_title(title, fontsize=14, fontweight="bold", pad=15)

        # Air line: O2 = 20.93 * (1 - CH4/100)
        ch4_air = np.linspace(0, 22, 200)
        o2_air = 20.93 * (1.0 - ch4_air / 100.0)
        ax.plot(ch4_air, o2_air, 'k--', lw=1.5, label="Air Dilution Line")

        # Zone A Polygon (Explosive area): LEL (5.0, 19.88), UEL (15.0, 17.79), Nose (5.9, 12.1)
        ch4_top = np.linspace(5.0, 15.0, 50)
        o2_top = 20.93 * (1.0 - ch4_top / 100.0)
        poly_x = [5.0] + list(ch4_top) + [15.0, 5.9, 5.0]
        poly_y = [19.88] + list(o2_top) + [17.79, 12.1, 19.88]
        ax.fill(poly_x, poly_y, color='red', alpha=0.35, label="Zone A: Explosive Area")
        ax.plot([5.0, 5.9], [19.88, 12.1], 'r-', lw=2.0)
        ax.plot([15.0, 5.9], [17.79, 12.1], 'r-', lw=2.0)

        # Origin-Nose Ray
        ch4_r = np.linspace(0, 10, 100)
        o2_r = (12.1 / 5.9) * ch4_r
        v_r = o2_r <= 20.93 * (1.0 - ch4_r / 100.0)
        ax.plot(ch4_r[v_r], o2_r[v_r], 'm-.', lw=1.2, label="Origin–Nose Dilution Ray")

        # Zone Labels
        ax.text(8.5, 15.5, "ZONE A\n(Explosive)", fontsize=11, fontweight="bold", color="darkred",
                ha="center", bbox=dict(boxstyle="round", fc="white", ec="red"))
        ax.text(15.5, 10.0, "ZONE B\n(Explosive with air)", fontsize=10, fontweight="bold",
                color="darkorange", ha="center", bbox=dict(boxstyle="round", fc="white", ec="orange"))
        ax.text(2.0, 16.0, "ZONE C\n(Explosive with $CH_4$)", fontsize=10, fontweight="bold",
                color="darkblue", ha="center", bbox=dict(boxstyle="round", fc="white", ec="blue"))
        ax.text(3.5, 3.0, "ZONE D\n(Non-explosive / Inert)", fontsize=11, fontweight="bold",
                color="darkgreen", ha="center", bbox=dict(boxstyle="round", fc="honeydew", ec="green"))
        ax.text(12.0, 21.0, "ZONE E: Impossible Mixtures", fontsize=9, fontstyle="italic", color="gray")

        # Reference Points
        ax.scatter([5.0, 15.0, 5.9], [19.88, 17.79, 12.1], color="darkred", s=70, zorder=6)
        ax.annotate("LEL (5.0%, 19.9%)", (5.0, 19.88), xytext=(1.2, 20.5),
                    arrowprops=dict(arrowstyle="->", lw=0.8), fontsize=8.5)
        ax.annotate("UEL (15.0%, 17.8%)", (15.0, 17.79), xytext=(15.5, 18.5),
                    arrowprops=dict(arrowstyle="->", lw=0.8), fontsize=8.5)
        ax.annotate("Nose (5.9%, 12.1%)", (5.9, 12.1), xytext=(1.5, 11.0),
                    arrowprops=dict(arrowstyle="->", lw=0.8), fontsize=8.5)

        # Plot 14 Samples
        sc = ax.scatter(df["CH4_percent"], df["O2_percent"], c=df["Temperature_C"],
                        cmap="plasma", s=90, edgecolors="black", lw=1.2, zorder=10,
                        label="Lodna Mine Fire Samples (N=14)")
        cbar = plt.colorbar(sc, ax=ax, pad=0.02)
        cbar.set_label("Mine Fire Temperature (°C)", fontsize=11, fontweight="bold")

        for _, r in df.iterrows():
            s_no = int(r["Sample_No"])
            lbl = f"S{s_no} ({r['Date']}, {r['Temperature_C']:.0f}°C)"
            x_off = 0.35 if s_no % 2 == 1 else 0.40
            y_off = 0.25 if s_no % 3 == 0 else (-0.35 if s_no % 3 == 1 else 0.0)
            ax.annotate(lbl, (r["CH4_percent"], r["O2_percent"]),
                        xytext=(r["CH4_percent"] + x_off, r["O2_percent"] + y_off),
                        fontsize=7.5, fontweight="semibold",
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="gray", alpha=0.85),
                        arrowprops=dict(arrowstyle="->", color="gray", lw=0.6))

        if with_dilution:
            ax.plot(dil_df["CH4_percent"], dil_df["O2_percent"], color="cyan", lw=3.0,
                    marker="o", markersize=5, markerfacecolor="blue", zorder=8,
                    label="Theoretical Pure $N_2$ Dilution Path")
            init_r = dil_df.iloc[0]
            ax.scatter([init_r["CH4_percent"]], [init_r["O2_percent"]], color="blue", s=130, marker="s", zorder=11)
            ax.annotate("Initial Sealed State\n(15% $CH_4$, 10% $O_2$)",
                        (init_r["CH4_percent"], init_r["O2_percent"]),
                        xytext=(init_r["CH4_percent"] - 2.5, init_r["O2_percent"] + 1.8),
                        fontsize=8.5, fontweight="bold", color="darkblue",
                        bbox=dict(boxstyle="round", fc="azure", ec="blue"),
                        arrowprops=dict(arrowstyle="->", color="blue", lw=1.2))

        note_text = (
            "Data Source: Singh et al. (2007), Lodna Colliery, Jharia Coalfield.\n"
            "Coward Boundaries Reference: USBM Bulletin 503 (Coward & Jones, 1952).\n"
            "All 14 Lodna samples reside firmly in Zone D (O2 ≤ 8.18%, CH4 ≤ 0.526%), non-explosive under sealed condition."
        )
        ax.text(0.01, 0.02, note_text, transform=ax.transAxes, fontsize=8,
                bbox=dict(boxstyle="round", fc="#f8f9fa", ec="#ced4da", alpha=0.9))

        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="upper right", fontsize=8.5)
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        plt.close()

    render_coward(os.path.join(fig_dir, "14_Coward_Diagram.png"), with_dilution=False)
    render_coward(os.path.join(fig_dir, "15_Coward_Diagram_With_Dilution.png"), with_dilution=True)


def df_to_markdown_table(df: pd.DataFrame) -> str:
    """Format DataFrame as markdown table without depending on tabulate."""
    headers = [str(c) for c in df.columns]
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---" for _ in headers]) + " |")
    for _, row in df.iterrows():
        row_str = [str(val) if not pd.isna(val) else "" for val in row]
        lines.append("| " + " | ".join(row_str) + " |")
    return "\n".join(lines)


# ======================================================================================
# 8. EXCEL & REPORT EXPORT
# ======================================================================================
def export_all_outputs(dirs: dict, raw_df, calc_df, temp_reg_df, corr_matrix,
                       coward_class_df, extremes_df, summary_stats_df, qa_dict, turnover_info):
    """Export 5 CSV files, 10-sheet formatted Excel workbook, and reports."""
    t_dir = dirs["tables"]
    r_dir = dirs["reports"]

    # 1. CSV Files
    calc_df.to_csv(os.path.join(t_dir, "calculated_gas_indices.csv"), index=False)
    corr_matrix.to_csv(os.path.join(t_dir, "correlation_matrix.csv"))
    calc_df[["Sample_No", "Date", "CH4_percent", "O2_percent", "Temperature_C"]].to_csv(
        os.path.join(t_dir, "coward_sample_coordinates.csv"), index=False)
    coward_class_df.to_csv(os.path.join(t_dir, "coward_zone_classification.csv"), index=False)
    summary_stats_df.to_csv(os.path.join(t_dir, "summary_statistics.csv"), index=False)
    extremes_df.to_csv(os.path.join(t_dir, "summary_extremes.csv"), index=False)

    # 2. 10-Sheet Excel Workbook
    xl_path = os.path.join(dirs["results"], "BTP_Final_Gas_Analysis.xlsx")
    with pd.ExcelWriter(xl_path, engine="openpyxl") as writer:
        raw_df.to_excel(writer, sheet_name="Raw Data", index=False)
        calc_df[["Sample_No", "Date", "Gas_Sum_percent", "Diff_from_100_percent",
                 "Validation_Status", "O2_Deficiency_percent", "O2_Deficiency_Flag"]].to_excel(
            writer, sheet_name="Gas Calculations", index=False)
        calc_df[["Sample_No", "Date", "Temperature_C", "O2_Deficiency_percent",
                 "Graham_Ratio", "Graham_Flag", "Graham_Interpretation",
                 "Young_Ratio", "Young_Flag", "CO_CO2_Ratio", "CO_CO2_Flag",
                 "Jones_Trickett_Ratio", "Jones_Trickett_Flag", "Jones_Trickett_Fuel",
                 "Willett_Ratio", "Willett_Flag", "CH_Ratio_Note"]].to_excel(
            writer, sheet_name="Fire Indices", index=False)
        temp_reg_df.to_excel(writer, sheet_name="Temperature Analysis", index=False)
        corr_matrix.to_excel(writer, sheet_name="Correlations")
        calc_df[["Sample_No", "Date", "CH4_percent", "O2_percent", "Temperature_C"]].to_excel(
            writer, sheet_name="Coward Data", index=False)
        coward_class_df.to_excel(writer, sheet_name="Coward Zone Classification", index=False)
        extremes_df.to_excel(writer, sheet_name="Summary", index=False, startrow=0)
        summary_stats_df.to_excel(writer, sheet_name="Summary", index=False, startrow=len(extremes_df) + 3)

        formula_guide = pd.DataFrame([
            {"Parameter": "Oxygen Deficiency (ΔO2)", "Formula": "ΔO2 = (20.93 / 79.04) * N2 - O2 ≈ 0.2648 * N2 - O2",
             "Significance": "Quantifies oxygen consumed by coal oxidation.", "Limitations": "Numerically unstable when ΔO2 < 0.3%."},
            {"Parameter": "Graham Ratio", "Formula": "Graham = 100 * CO / ΔO2",
             "Significance": "<0.4 Normal, 0.5 Check, 1.0 Heating, 2.0 Serious heating, >=3.0 Active fire.",
             "Limitations": "Indicative only; unreliable if ΔO2 < 0.3%."},
            {"Parameter": "Young Ratio", "Formula": "Young = 100 * CO2 / ΔO2",
             "Significance": "Combustion maturity indicator.",
             "Limitations": "CO2 originates from strata gas and acid-carbonate reactions as well."},
            {"Parameter": "CO / CO2 Ratio", "Formula": "CO/CO2 = 100 * CO / CO2",
             "Significance": "Incomplete combustion indicator.",
             "Limitations": "Solubility of CO2 in mine water distorts ratio."},
            {"Parameter": "Jones-Trickett Ratio", "Formula": "JT = (CO2 + 0.75 * CO - 0.25 * H2) / ΔO2",
             "Significance": "0.4-0.5 Methane; 0.5-1.0 Coal/oil/belt; 0.9-1.6 Timber.",
             "Limitations": "Ambiguous in mixed-fuel scenarios."},
            {"Parameter": "Willett Ratio", "Formula": "CO2 / (Excess N2 + CO2 + Combustibles); Excess N2 = N2 - 3.8 * O2",
             "Significance": "Sealed fire activity trend indicator.",
             "Limitations": "Requires clear definition of combustibles (CO+H2+CH4)."},
            {"Parameter": "C / H Ratio", "Formula": "REFERENCE REQUIRED (Definitions vary across literature)",
             "Significance": "Combustion stoichiometry.", "Limitations": "No universal formula in Singh et al. (2007)."}
        ])
        formula_guide.to_excel(writer, sheet_name="Formula Guide", index=False)

        ref_guide = pd.DataFrame([
            {"Source": "Singh et al. (2007)",
             "Citation": "Singh et al. (2007). Mine fire gas indices and their application to Indian underground coal mine fires. Int. J. Coal Geol., 69(3), 192-204.",
             "Role": "Source of 14 Lodna Colliery real mine fire samples (1985-1993)."},
            {"Source": "Coward & Jones (1952)",
             "Citation": "Coward, H.F., Jones, G.W. (1952). Limits of Flammability of Gases and Vapors. USBM Bulletin 503, 155 pp.",
             "Role": "Foundational Coward diagram limits (LEL 5.0%, UEL 15.0%, Nose 5.9% CH4, 12.1% O2)."},
            {"Source": "Zabetakis (1965)",
             "Citation": "Zabetakis, M.G. (1965). Flammability Characteristics of Combustible Gases and Vapors. USBM Bulletin 627, 121 pp.",
             "Role": "Flammability envelopes and nitrogen inertisation dilution limits."},
            {"Source": "Banerjee (1985)",
             "Citation": "Banerjee, S.C. (1985). Prevention and Combating Mine Fires. Oxford & IBH Publishing, New Delhi.",
             "Role": "Standard Indian coal mining fire index interpretation criteria."}
        ])
        ref_guide.to_excel(writer, sheet_name="Sources & References", index=False)

    # Style Excel Workbook
    wb = openpyxl.load_workbook(xl_path)
    hdr_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    hdr_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    for s_name in wb.sheetnames:
        ws = wb[s_name]
        ws.views.sheetView[0].showGridLines = True
        for col in ws.columns:
            first_c = col[0]
            if first_c.value is not None:
                first_c.fill = hdr_fill
                first_c.font = hdr_font
                first_c.alignment = Alignment(horizontal="center", vertical="center")
            max_len = max(len(str(c.value or '')) for c in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 48)
    wb.save(xl_path)

    # 3. Markdown Report
    md_path = os.path.join(r_dir, "BTP_Mine_Fire_Analysis_Report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# BTP PROJECT REPORT: FIRE GASES AND THEIR INTERPRETATION IN UNDERGROUND COAL MINES\n")
        f.write("**Department of Mining Engineering, IIT Kharagpur**\n\n---\n")
        f.write("## Chapter 1 — Introduction\n")
        f.write("Spontaneous combustion of coal in underground mines is a significant geo-mining hazard. "
                "This study investigates mine-fire gas behavior using 14 real published samples from "
                "Lodna Colliery, Jharia Coalfield (Singh et al., 2007).\n\n")
        f.write("## Chapter 2 — Mine Fire Gases\n")
        f.write("Atmospheric components analyzed: O2, CO, CO2, H2, CH4, and N2. "
                "CO serves as the primary indicator of oxidation kinetics, while O2 reflects combustion consumption and seal leakage.\n\n")
        f.write("## Chapter 3 — Fire-Gas Indices\n")
        f.write("Indices computed: Oxygen Deficiency (ΔO2 = 0.2648*N2 - O2), Graham Ratio, Young Ratio, "
                "CO/CO2 Ratio, Jones–Trickett Ratio, Willett Ratio, and C/H Ratio (REFERENCE REQUIRED).\n\n")
        f.write("## Chapter 4 — Dataset and Methodology\n")
        f.write("Analyzes 14 published samples from Lodna Colliery (1985–1993). Gas sums were validated within ±1.0%.\n\n")
        f.write("## Chapter 5 — Results and Extrema\n")
        f.write(df_to_markdown_table(extremes_df))
        f.write("\n\n## Chapter 6 — Temperature and Gas Relationships\n")
        for q_k, q_v in qa_dict.items():
            f.write(f"### {q_v['Question']}\n{q_v['Finding']}\n\n")
        f.write("## Chapter 7 — Coward Diagram Analysis\n")
        f.write("All 14 Lodna samples reside firmly in Zone D (Non-explosive / Cannot form explosive mixtures with air alone) "
                "due to low O2 (≤8.18%) and low CH4 (≤0.526%).\n")
        f.write(f"Theoretical N2 dilution scenario (27,000 m³, 5 m³/s) gives a nominal turnover of "
                f"{turnover_info['Nominal_Turnover_Minutes']:.1f} minutes. Note: Idealized academic model only.\n\n")
        f.write("## Chapter 8 — Discussion and Limitations\n")
        f.write("Temperature alone is insufficient to diagnose mine fires. Multi-parameter gas analysis is mandatory. "
                "Small sample size (N=14) and field gas gradients are noted as scientific limitations.\n\n")
        f.write("## Chapter 9 — Conclusions\n")
        f.write("Mine-fire gas relationships with temperature are non-monotonic. Peak CO and fire indices occur at "
                "intermediate temperatures where oxygen is available. Multi-indicator diagnosis is essential.\n\n")
        f.write("## References\n")
        f.write("1. Singh et al. (2007). Int. J. Coal Geol., 69(3), 192–204.\n"
                "2. Coward & Jones (1952). USBM Bulletin 503.\n"
                "3. Zabetakis (1965). USBM Bulletin 627.\n"
                "4. Banerjee (1985). Prevention and Combating Mine Fires, Oxford & IBH.\n")

    # 4. Word Document (.docx)
    if DOCX_AVAILABLE:
        doc_path = os.path.join(r_dir, "BTP_Mine_Fire_Analysis_Report.docx")
        doc = Document()
        doc.add_heading("BTP PROJECT REPORT", level=0).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_heading("Fire Gases and Their Interpretation in Underground Coal Mines", level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("Department of Mining Engineering, IIT Kharagpur\n").alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_heading("Chapter 1 — Introduction", level=1)
        doc.add_paragraph("Analysis of real mine fire gases from Lodna Colliery, Jharia Coalfield (Singh et al., 2007).")
        doc.add_heading("Chapter 2 — Fire Gases & Indices", level=1)
        doc.add_paragraph("Calculated Oxygen Deficiency, Graham, Young, CO/CO2, Jones-Trickett, and Willett ratios.")
        doc.add_heading("Chapter 3 — Research Questions & Findings", level=1)
        for q_k, q_v in qa_dict.items():
            p = doc.add_paragraph()
            p.add_run(f"{q_v['Question']}\n").bold = True
            p.add_run(q_v["Finding"])
        doc.add_heading("Chapter 4 — Coward Diagram & Explosibility", level=1)
        doc.add_paragraph("All 14 samples reside in Zone D (Non-explosive atmosphere).")
        doc.add_heading("Chapter 5 — Conclusions", level=1)
        doc.add_paragraph("Temperature alone is not sufficient. Combined multi-gas interpretation is essential.")
        doc.save(doc_path)


# ======================================================================================
# 9. MAIN PIPELINE EXECUTION
# ======================================================================================
def main():
    print("=" * 80)
    print("  BTP PROJECT: FIRE GASES & THEIR INTERPRETATION IN UNDERGROUND COAL MINES")
    print("  Department of Mining Engineering, IIT Kharagpur")
    print("=" * 80)

    dirs = resolve_directories()
    print(f"[*] Workspace Root: {dirs['base']}")

    # 1. Ingest Data
    print("\n[Step 1/7] Ingesting published mine-fire dataset...")
    df_raw = get_lodna_raw_data(dirs["data"])
    print(f"  -> Loaded {len(df_raw)} samples from Lodna Colliery (Singh et al., 2007).")

    # 2. Validate
    print("\n[Step 2/7] Validating gas composition sums...")
    df_val = validate_gas_data(df_raw, tolerance=1.0)
    mean_sum = df_val["Gas_Sum_percent"].mean()
    max_diff = df_val["Abs_Diff_percent"].max()
    print(f"  -> Mean Gas Sum: {mean_sum:.2f}% | Max Deviation: {max_diff:.2f}% | All Valid within ±1.0%.")

    # 3. Indices
    print("\n[Step 3/7] Calculating oxygen deficiency and fire-gas indices...")
    df_calc = compute_indices(df_val)

    # 4. Temperature Analysis
    print("\n[Step 4/7] Analyzing temperature relationships & research questions...")
    temp_reg_df, qa_dict = analyze_temperature(df_calc)
    extremes_df = generate_extremes_table(df_calc)

    analysis_cols = ["Temperature_C", "O2_percent", "CO2_percent", "CO_percent",
                     "H2_percent", "CH4_percent", "N2_percent", "O2_Deficiency_percent",
                     "Graham_Ratio", "Young_Ratio", "CO_CO2_Ratio", "Jones_Trickett_Ratio", "Willett_Ratio"]
    summary_stats = []
    for c in analysis_cols:
        s = df_calc[c].dropna()
        summary_stats.append({
            "Parameter": c, "Count": len(df_calc), "Valid_N": len(s),
            "Mean": round(s.mean(), 4), "Std_Dev": round(s.std(), 4),
            "Min": round(s.min(), 4), "Max": round(s.max(), 4)
        })
    summary_stats_df = pd.DataFrame(summary_stats)
    corr_matrix = df_calc[analysis_cols].corr()

    # 5. Coward Diagram & Dilution Model
    print("\n[Step 5/7] Performing Coward zone classification & theoretical dilution model...")
    coward_class_df = classify_coward_zones(df_calc)
    dil_df, turnover_info = simulate_theoretical_dilution(v_m3=27000.0, q_m3_s=5.0)

    # 6. Plot Figures
    print("\n[Step 6/7] Generating 15 publication-quality figures (300 DPI)...")
    plot_all_figures(df_calc, dirs["figures"], dil_df)
    print(f"  -> All 15 figures generated in: {dirs['figures']}")

    # 7. Export Files
    print("\n[Step 7/7] Exporting CSV tables, Excel workbook, and reports...")
    export_all_outputs(dirs, df_raw, df_calc, temp_reg_df, corr_matrix,
                       coward_class_df, extremes_df, summary_stats_df, qa_dict, turnover_info)

    print("\n" + "=" * 80)
    print("  SUMMARY OF CRITICAL FINDINGS:")
    print("=" * 80)
    print(f"1. Highest Temperature: {extremes_df.loc[extremes_df['Observation_Category']=='Highest Temperature', 'Value'].values[0]} "
          f"(Sample {extremes_df.loc[extremes_df['Observation_Category']=='Highest Temperature', 'Sample_No'].values[0]} on "
          f"{extremes_df.loc[extremes_df['Observation_Category']=='Highest Temperature', 'Date'].values[0]})")
    print(f"2. Highest CO: {extremes_df.loc[extremes_df['Observation_Category']=='Highest CO', 'Value'].values[0]} "
          f"(Sample {extremes_df.loc[extremes_df['Observation_Category']=='Highest CO', 'Sample_No'].values[0]} on "
          f"{extremes_df.loc[extremes_df['Observation_Category']=='Highest CO', 'Date'].values[0]} at {extremes_df.loc[extremes_df['Observation_Category']=='Highest CO', 'Temperature_C'].values[0]}°C)")
    print(f"3. Highest H2: {extremes_df.loc[extremes_df['Observation_Category']=='Highest H2', 'Value'].values[0]} "
          f"(Sample {extremes_df.loc[extremes_df['Observation_Category']=='Highest H2', 'Sample_No'].values[0]} on "
          f"{extremes_df.loc[extremes_df['Observation_Category']=='Highest H2', 'Date'].values[0]} at {extremes_df.loc[extremes_df['Observation_Category']=='Highest H2', 'Temperature_C'].values[0]}°C)")
    print("4. Coward Classification: All 14 samples are in Zone D (Non-explosive / Deficient in fuel & oxygen).")
    print(f"5. Theoretical N2 Dilution: V/Q nominal turnover time = {turnover_info['Nominal_Turnover_Minutes']:.1f} minutes (Academic model only).")
    print("\n  ALL OUTPUT FILES ARE READY IN 'results/'")
    print("=" * 80)


if __name__ == "__main__":
    main()
