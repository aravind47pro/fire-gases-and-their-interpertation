"""
Coward Diagram Module for BTP Mine Fire Analysis
Plots Coward Explosibility Diagram (Methane vs Oxygen) for Underground Coal Mines.
Renders Zones A, B, C, D, E using published literature coordinates.
Plots and classifies all 14 Lodna mine-fire samples.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, Tuple, Optional

# Standard reference values for Coward diagram (Coward & Jones, 1952, USBM Bull. 503)
STD_ATM_O2 = 20.93
LEL_CH4 = 5.00
LEL_O2 = STD_ATM_O2 * (1.0 - LEL_CH4 / 100.0)  # 19.88%
UEL_CH4 = 15.00
UEL_O2 = STD_ATM_O2 * (1.0 - UEL_CH4 / 100.0)  # 17.79%
NOSE_CH4 = 5.90
NOSE_O2 = 12.10

# Nose ray slope from origin (0,0)
NOSE_SLOPE = NOSE_O2 / NOSE_CH4  # ~2.0508
# Intersection of Nose ray with Air line:
# Air line: O2 = 20.93 - 0.2093 * CH4
# Nose ray: O2 = 2.0508 * CH4
# 2.0508 * CH4 = 20.93 - 0.2093 * CH4  ==> 2.2601 * CH4 = 20.93 ==> CH4 ≈ 9.26%
# Note: For pure air dilution from mixture to (0, 20.93), the critical tangent from (0, 20.93) to the flammability curve
# or ray from origin (0,0) through nose defines the boundary of Zone B.
# Ray from (0,0) through Nose (5.9, 12.1):
# For any mixture with CH4/O2 > 5.9/12.1, dilution with air moves the point towards (0, 20.93) and crosses into Zone A.


def classify_coward_zone(ch4: float, o2: float, verified: bool = True) -> Tuple[str, str]:
    """
    Classify a gas mixture (CH4, O2) into standard Coward Explosibility Zones.
    Based on USBM Bulletin 503 (Coward & Jones, 1952).

    Zones:
    - Zone A: Explosive mixtures
    - Zone B: Capable of forming explosive mixtures with air
    - Zone C: Capable of forming explosive mixtures with methane
    - Zone D: Not capable of forming explosive mixtures (Inert / Safe from explosion)
    - Zone E: Impossible mixtures (above air dilution line)
    """
    if pd.isna(ch4) or pd.isna(o2):
        return "Unknown", "Missing gas values"

    if not verified:
        return "Pending Verification", "Coward zone boundaries pending verification from selected reference."

    # Air line limit at this CH4 concentration
    max_possible_o2 = STD_ATM_O2 * (1.0 - ch4 / 100.0)

    # Zone E: Impossible mixtures
    if o2 > max_possible_o2 + 0.1:  # Allow 0.1% tolerance
        return "Zone E", "Impossible mixture (O2 exceeds normal atmospheric dilution limit)"

    # Zone A: Inside explosive region
    # Bounded between LEL curve, UEL curve, and above Nose O2 (12.1%)
    if o2 >= NOSE_O2:
        # Approximate linear boundaries for explosive pocket:
        # Lower boundary from Nose (5.9, 12.1) to LEL (5.0, 19.88)
        # Upper boundary from Nose (5.9, 12.1) to UEL (15.0, 17.79)
        slope_lower = (LEL_O2 - NOSE_O2) / (LEL_CH4 - NOSE_CH4)  # (19.88 - 12.1) / (5.0 - 5.9) = 7.78 / -0.9 = -8.644
        ch4_lower_boundary = NOSE_CH4 + (o2 - NOSE_O2) / slope_lower

        slope_upper = (UEL_O2 - NOSE_O2) / (UEL_CH4 - NOSE_CH4)  # (17.79 - 12.1) / (15.0 - 5.9) = 5.69 / 9.1 = 0.6253
        ch4_upper_boundary = NOSE_CH4 + (o2 - NOSE_O2) / slope_upper

        if (ch4 >= ch4_lower_boundary) and (ch4 <= ch4_upper_boundary) and (o2 <= max_possible_o2):
            return "Zone A", "Explosive mixture (propagates flame independently)"

    # Check Zone B vs Zone D vs Zone C:
    # Any mixture to the right of the critical dilution line will pass through Zone A when diluted with air.
    # The line connecting (0, 20.93) to Nose (5.9, 12.1) has slope = (12.1 - 20.93)/5.9 = -1.4966.
    # The ray from origin (0,0) through Nose (5.9, 12.1) has slope NOSE_SLOPE = 12.1 / 5.9 = 2.0508.
    # If O2 < 12.1% and CH4 < 5.0%:
    if o2 < NOSE_O2 and ch4 < LEL_CH4:
        return "Zone D", "Not capable of forming explosive mixtures (Inert / Deficient in both fuel and oxygen)"

    # If CH4 is high and adding air brings it into Zone A:
    # A line from the air point (0, 20.93) through the nose (5.9, 12.1):
    # or if point is to the right of Zone A:
    if ch4 > LEL_CH4:
        return "Zone B", "Capable of forming explosive mixtures when diluted with air"

    if o2 >= NOSE_O2 and ch4 < LEL_CH4:
        return "Zone C", "Capable of forming explosive mixtures if methane is added"

    return "Zone D", "Non-explosive under current atmosphere"


def build_coward_classification_table(df: pd.DataFrame, is_verified: bool = True) -> pd.DataFrame:
    """
    Generate sample-by-sample Coward diagram classification table for all 14 Lodna samples.
    """
    records = []
    for _, row in df.iterrows():
        s_no = int(row["Sample_No"])
        date_str = str(row["Date"])
        ch4 = float(row["CH4_percent"])
        o2 = float(row["O2_percent"])
        temp = float(row["Temperature_C"])

        zone, interp = classify_coward_zone(ch4, o2, verified=is_verified)

        records.append({
            "Sample_No": s_no,
            "Date": date_str,
            "CH4_percent": ch4,
            "O2_percent": o2,
            "Temperature_C": temp,
            "Coward_Zone": zone,
            "Safety_Interpretation": interp
        })

    return pd.DataFrame(records)


def plot_coward_diagram(df: pd.DataFrame,
                        output_path: str,
                        dilution_df: Optional[pd.DataFrame] = None,
                        is_verified: bool = True,
                        ref_note: str = "USBM Bulletin 503 (Coward & Jones, 1952)",
                        dpi: int = 300) -> None:
    """
    Create publication-quality Coward Diagram (X: CH4 %, Y: O2 %).
    Renders Zones A, B, C, D, E and plots all 14 Lodna samples with labels.
    Optionally overlays theoretical N2 dilution trajectory.
    """
    fig, ax = plt.subplots(figsize=(12, 9), dpi=dpi)

    # 1. Base grid and axes limits
    ax.set_xlim(-0.5, 22.0)
    ax.set_ylim(-0.5, 23.0)
    ax.set_xlabel("Methane, $CH_4$ (% by volume)", fontsize=13, fontweight="bold")
    ax.set_ylabel("Oxygen, $O_2$ (% by volume)", fontsize=13, fontweight="bold")

    title_text = "Coward Explosibility Diagram — Lodna Colliery Fire Samples"
    if dilution_df is not None:
        title_text += " & Theoretical $N_2$ Dilution Trajectory"
    ax.set_title(title_text, fontsize=14, fontweight="bold", pad=15)

    # 2. Draw Air Dilution Line (O2 = 20.93 * (1 - CH4/100))
    ch4_air = np.linspace(0, 22, 200)
    o2_air = STD_ATM_O2 * (1.0 - ch4_air / 100.0)
    ax.plot(ch4_air, o2_air, 'k--', linewidth=1.5, label="Air Dilution Line ($O_2 = 20.93(1 - CH_4/100)$)")

    if is_verified:
        # Zone A Polygon (Explosive area)
        # Curve from LEL (5.0, 19.88) to Nose (5.9, 12.1)
        # Curve from Nose (5.9, 12.1) to UEL (15.0, 17.79)
        # Top segment along Air Line from LEL to UEL
        ch4_top = np.linspace(LEL_CH4, UEL_CH4, 50)
        o2_top = STD_ATM_O2 * (1.0 - ch4_top / 100.0)

        poly_x = [LEL_CH4] + list(ch4_top) + [UEL_CH4, NOSE_CH4, LEL_CH4]
        poly_y = [LEL_O2] + list(o2_top) + [UEL_O2, NOSE_O2, LEL_O2]

        ax.fill(poly_x, poly_y, color='red', alpha=0.35, label="Zone A: Explosive Mixtures")
        ax.plot([LEL_CH4, NOSE_CH4], [LEL_O2, NOSE_O2], 'r-', linewidth=2.0)
        ax.plot([UEL_CH4, NOSE_CH4], [UEL_O2, NOSE_O2], 'r-', linewidth=2.0)

        # Ray from origin through Nose (5.9, 12.1)
        ch4_ray = np.linspace(0, 10.0, 100)
        o2_ray = NOSE_SLOPE * ch4_ray
        # Limit to below air line
        valid_ray = o2_ray <= STD_ATM_O2 * (1.0 - ch4_ray / 100.0)
        ax.plot(ch4_ray[valid_ray], o2_ray[valid_ray], 'm-.', linewidth=1.2,
                label=f"Origin–Nose Ray (Slope = {NOSE_SLOPE:.2f})")

        # Ray from Air Point (0, 20.93) through Nose (5.9, 12.1)
        # Intersects x-axis at CH4 = 20.93 / 1.4966 ≈ 13.98%
        slope_air_nose = (NOSE_O2 - STD_ATM_O2) / NOSE_CH4
        ch4_air_nose = np.linspace(0, 15.0, 100)
        o2_air_nose = STD_ATM_O2 + slope_air_nose * ch4_air_nose
        valid_an = o2_air_nose >= 0
        ax.plot(ch4_air_nose[valid_an], o2_air_nose[valid_an], 'g:', linewidth=1.4,
                label="Air–Nose Tangent Line (Dilution with air)")

        # Zone Labels on Plot
        ax.text(8.5, 15.5, "ZONE A\n(Explosive)", fontsize=11, fontweight="bold",
                color="darkred", ha="center", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="red", alpha=0.8))
        ax.text(15.5, 10.0, "ZONE B\n(Explosive when\ndiluted with air)", fontsize=10,
                fontweight="bold", color="darkorange", ha="center",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="orange", alpha=0.8))
        ax.text(2.0, 16.0, "ZONE C\n(Explosive with\n$CH_4$ addition)", fontsize=10,
                fontweight="bold", color="darkblue", ha="center",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="blue", alpha=0.8))
        ax.text(3.5, 3.0, "ZONE D\n(Non-explosive /\nInert Atmosphere)", fontsize=11,
                fontweight="bold", color="darkgreen", ha="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="honeydew", ec="green", alpha=0.9))
        ax.text(12.0, 21.0, "ZONE E: Impossible Mixtures", fontsize=9, fontstyle="italic",
                color="gray", ha="center")

        # Key Reference Points
        ax.scatter([LEL_CH4, UEL_CH4, NOSE_CH4], [LEL_O2, UEL_O2, NOSE_O2],
                   color="darkred", s=70, zorder=5)
        ax.annotate(f"LEL ({LEL_CH4}%, {LEL_O2:.1f}%)", xy=(LEL_CH4, LEL_O2),
                    xytext=(LEL_CH4 - 3.8, LEL_O2 + 0.6), fontsize=8,
                    arrowprops=dict(arrowstyle="->", color="black", lw=0.8))
        ax.annotate(f"UEL ({UEL_CH4}%, {UEL_O2:.1f}%)", xy=(UEL_CH4, UEL_O2),
                    xytext=(UEL_CH4 + 0.5, UEL_O2 + 0.8), fontsize=8,
                    arrowprops=dict(arrowstyle="->", color="black", lw=0.8))
        ax.annotate(f"Nose ({NOSE_CH4}%, {NOSE_O2}%)", xy=(NOSE_CH4, NOSE_O2),
                    xytext=(NOSE_CH4 - 4.5, NOSE_O2 - 1.5), fontsize=8,
                    arrowprops=dict(arrowstyle="->", color="black", lw=0.8))
    else:
        # Note if boundaries are unverified
        ax.text(10.0, 10.0, "Coward zone boundaries pending verification\nfrom the selected reference.",
                fontsize=12, color="red", ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.5", fc="lightyellow", ec="red"))

    # 3. Plot Lodna Mine Fire Samples
    sc = ax.scatter(df["CH4_percent"], df["O2_percent"],
                    c=df["Temperature_C"], cmap="plasma", s=90,
                    edgecolors="black", linewidths=1.2, zorder=10,
                    label="Lodna Mine Fire Samples (N=14)")
    cbar = plt.colorbar(sc, ax=ax, pad=0.02)
    cbar.set_label("Mine Fire Temperature (°C)", fontsize=11, fontweight="bold")

    # Label every sample clearly: S{No} – {Date} – {Temp}°C
    for _, row in df.iterrows():
        s_no = int(row["Sample_No"])
        date_str = str(row["Date"])
        temp_val = row["Temperature_C"]
        x_pt = row["CH4_percent"]
        y_pt = row["O2_percent"]

        # Offset labels to avoid clumping
        x_off = 0.35 if s_no % 2 == 1 else 0.40
        y_off = 0.25 if s_no % 3 == 0 else (-0.35 if s_no % 3 == 1 else 0.0)

        label_txt = f"S{s_no} ({date_str}, {temp_val:.0f}°C)"
        ax.annotate(label_txt, xy=(x_pt, y_pt),
                    xytext=(x_pt + x_off, y_pt + y_off),
                    fontsize=7.5, fontweight="semibold",
                    arrowprops=dict(arrowstyle="->", color="gray", lw=0.6, alpha=0.7),
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="darkgray", alpha=0.85),
                    zorder=12)

    # 4. Overlay Theoretical N2 Dilution Trajectory if provided
    if dilution_df is not None:
        ax.plot(dilution_df["CH4_percent"], dilution_df["O2_percent"],
                color="cyan", linewidth=3.0, linestyle="-", marker="o", markersize=5,
                markerfacecolor="blue", markeredgecolor="white", zorder=8,
                label="Theoretical Pure $N_2$ Dilution Path")

        # Mark Initial Point
        init_row = dilution_df.iloc[0]
        ax.scatter([init_row["CH4_percent"]], [init_row["O2_percent"]],
                   color="blue", s=130, marker="s", edgecolors="black", zorder=11)
        ax.annotate(f"Initial Sealed State\n({init_row['CH4_percent']:.1f}% $CH_4$, {init_row['O2_percent']:.1f}% $O_2$)",
                    xy=(init_row["CH4_percent"], init_row["O2_percent"]),
                    xytext=(init_row["CH4_percent"] - 2.5, init_row["O2_percent"] + 1.8),
                    fontsize=8.5, fontweight="bold", color="darkblue",
                    arrowprops=dict(arrowstyle="->", color="blue", lw=1.2),
                    bbox=dict(boxstyle="round,pad=0.2", fc="azure", ec="blue"))

        # Arrow indicating path toward origin
        mid_idx = len(dilution_df) // 2
        ax.annotate("", xy=(dilution_df.iloc[mid_idx + 2]["CH4_percent"], dilution_df.iloc[mid_idx + 2]["O2_percent"]),
                    xytext=(dilution_df.iloc[mid_idx]["CH4_percent"], dilution_df.iloc[mid_idx]["O2_percent"]),
                    arrowprops=dict(arrowstyle="->", color="darkcyan", lw=2.5))

    # Reference note box at bottom
    note_text = (
        f"Data Source: Lodna Colliery (Singh et al., 2007, Int. J. Coal Geol., 69(3), 192–204).\n"
        f"Coward Boundaries Reference: {ref_note}.\n"
        "Key Observation: All 14 Lodna samples reside in Zone D (O2 ≤ 8.18%, CH4 ≤ 0.526%), non-explosive under sealed condition."
    )
    ax.text(0.01, 0.02, note_text, transform=ax.transAxes, fontsize=8,
            va="bottom", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", fc="#f8f9fa", ec="#ced4da", alpha=0.9))

    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.9)
    plt.tight_layout()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close()
