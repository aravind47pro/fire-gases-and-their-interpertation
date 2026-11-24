"""
Plotting Module for BTP Mine Fire Gas Analysis
Generates all 15 required publication-quality figures at 300 DPI.
Includes regression trends, R2, correlation statistics, and date/time trends.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

# Style settings for publication/BTP report
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8


def save_scatter_with_regression(df: pd.DataFrame,
                                 x_col: str,
                                 y_col: str,
                                 x_label: str,
                                 y_label: str,
                                 title: str,
                                 output_path: str,
                                 dpi: int = 300,
                                 color: str = "#1f77b4",
                                 show_sample_labels: bool = True) -> None:
    """Helper to generate scatter plot with linear regression fit, equation, and R2."""
    fig, ax = plt.subplots(figsize=(8.5, 6), dpi=dpi)

    valid_mask = (~df[x_col].isna()) & (~df[y_col].isna())
    sub_df = df[valid_mask]

    x = sub_df[x_col].values
    y = sub_df[y_col].values

    # Scatter points
    ax.scatter(x, y, color=color, s=70, edgecolors="black", linewidths=0.8, alpha=0.9, zorder=5)

    if show_sample_labels:
        for _, row in sub_df.iterrows():
            ax.annotate(f"S{int(row['Sample_No'])}", (row[x_col], row[y_col]),
                        xytext=(4, 4), textcoords="offset points", fontsize=8, alpha=0.85)

    # Linear regression fit if at least 3 points
    if len(x) >= 3 and np.std(x) > 1e-12:
        m, b = np.polyfit(x, y, 1)
        r_val = np.corrcoef(x, y)[0, 1]
        r_sq = r_val ** 2

        x_line = np.linspace(x.min() - 0.05 * (x.max() - x.min()),
                             x.max() + 0.05 * (x.max() - x.min()), 100)
        y_line = m * x_line + b
        ax.plot(x_line, y_line, color="#d62728", linestyle="--", linewidth=1.5,
                label=f"Linear Fit: y = {m:.4f}x {'+' if b >= 0 else '-'} {abs(b):.4f}\n($R^2 = {r_sq:.3f}$, $r = {r_val:.3f}$)")

    ax.set_xlabel(x_label, fontsize=12, fontweight="bold")
    ax.set_ylabel(y_label, fontsize=12, fontweight="bold")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="best", fontsize=9.5, framealpha=0.9)

    # Note
    ax.text(0.02, 0.03, "Source: Singh et al. (2007), Lodna Colliery (N=14)",
            transform=ax.transAxes, fontsize=8, fontstyle="italic", color="#555555")

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close()


def generate_all_btp_figures(df: pd.DataFrame,
                             figures_dir: str,
                             dilution_df: Optional[pd.DataFrame] = None,
                             is_verified: bool = True,
                             ref_note: str = "USBM Bulletin 503 (Coward & Jones, 1952)",
                             dpi: int = 300) -> Dict[str, str]:
    """Generate all 15 required figures and return dictionary of file paths."""
    os.makedirs(figures_dir, exist_ok=True)
    generated = {}

    # Figure 01: CO vs Temperature
    p01 = os.path.join(figures_dir, "01_CO_vs_Temperature.png")
    save_scatter_with_regression(df, "Temperature_C", "CO_percent",
                                 "Temperature (°C)", "Carbon Monoxide, CO (% by volume)",
                                 "Mine Fire Temperature vs. Carbon Monoxide (CO)",
                                 p01, dpi=dpi, color="#d62728")
    generated["01_CO_vs_Temperature"] = p01

    # Figure 02: CO2 vs Temperature
    p02 = os.path.join(figures_dir, "02_CO2_vs_Temperature.png")
    save_scatter_with_regression(df, "Temperature_C", "CO2_percent",
                                 "Temperature (°C)", "Carbon Dioxide, $CO_2$ (% by volume)",
                                 "Mine Fire Temperature vs. Carbon Dioxide ($CO_2$)",
                                 p02, dpi=dpi, color="#2ca02c")
    generated["02_CO2_vs_Temperature"] = p02

    # Figure 03: O2 vs Temperature
    p03 = os.path.join(figures_dir, "03_O2_vs_Temperature.png")
    save_scatter_with_regression(df, "Temperature_C", "O2_percent",
                                 "Temperature (°C)", "Oxygen, $O_2$ (% by volume)",
                                 "Mine Fire Temperature vs. Oxygen ($O_2$)",
                                 p03, dpi=dpi, color="#1f77b4")
    generated["03_O2_vs_Temperature"] = p03

    # Figure 04: H2 vs Temperature
    p04 = os.path.join(figures_dir, "04_H2_vs_Temperature.png")
    save_scatter_with_regression(df, "Temperature_C", "H2_percent",
                                 "Temperature (°C)", "Hydrogen, $H_2$ (% by volume)",
                                 "Mine Fire Temperature vs. Hydrogen ($H_2$)",
                                 p04, dpi=dpi, color="#9467bd")
    generated["04_H2_vs_Temperature"] = p04

    # Figure 05: CH4 vs Temperature
    p05 = os.path.join(figures_dir, "05_CH4_vs_Temperature.png")
    save_scatter_with_regression(df, "Temperature_C", "CH4_percent",
                                 "Temperature (°C)", "Methane, $CH_4$ (% by volume)",
                                 "Mine Fire Temperature vs. Methane ($CH_4$)",
                                 p05, dpi=dpi, color="#ff7f0e")
    generated["05_CH4_vs_Temperature"] = p05

    # Figure 06: Chronological Date/Time Trends (Multi-panel)
    p06 = os.path.join(figures_dir, "06_Temperature_Trend.png")
    fig, axes = plt.subplots(3, 1, figsize=(11, 10), dpi=dpi, sharex=True)

    sorted_df = df.sort_values("Date_Parsed").copy()
    dates = sorted_df["Date_Parsed"]

    # Panel A: Temperature & O2 Deficiency
    axes[0].plot(dates, sorted_df["Temperature_C"], 'r-o', linewidth=1.8, markersize=6, label="Temperature (°C)")
    axes[0].set_ylabel("Temperature (°C)", color="red", fontweight="bold")
    axes[0].tick_params(axis='y', labelcolor="red")
    axes[0].grid(True, linestyle="--", alpha=0.5)

    ax0_twin = axes[0].twinx()
    ax0_twin.plot(dates, sorted_df["O2_Deficiency_percent"], 'b-s', linewidth=1.5, markersize=5, label=r"$\Delta O_2$ (%)")
    ax0_twin.set_ylabel(r"$\Delta O_2$ (%)", color="blue", fontweight="bold")
    ax0_twin.tick_params(axis='y', labelcolor="blue")
    axes[0].set_title("Chronological Mine Fire Atmosphere Trends (1985 – 1993)", fontsize=13, fontweight="bold")

    # Panel B: CO and H2
    axes[1].plot(dates, sorted_df["CO_percent"], 'm-^', linewidth=1.8, markersize=6, label="CO (% vol)")
    axes[1].plot(dates, sorted_df["H2_percent"], 'c-d', linewidth=1.5, markersize=5, label="$H_2$ (% vol)")
    axes[1].set_ylabel("Concentration (% vol)", fontweight="bold")
    axes[1].legend(loc="upper right", framealpha=0.9)
    axes[1].grid(True, linestyle="--", alpha=0.5)

    # Panel C: Fire Ratios (Graham & Young)
    axes[2].plot(dates, sorted_df["Graham_Ratio"], 'g-o', linewidth=1.8, markersize=6, label=r"Graham Ratio ($100 \cdot CO / \Delta O_2$)")
    axes[2].set_ylabel("Graham Ratio", color="green", fontweight="bold")
    axes[2].tick_params(axis='y', labelcolor="green")
    axes[2].grid(True, linestyle="--", alpha=0.5)

    ax2_twin = axes[2].twinx()
    ax2_twin.plot(dates, sorted_df["Young_Ratio"], 'k--x', linewidth=1.4, markersize=5, label=r"Young Ratio ($100 \cdot CO_2 / \Delta O_2$)")
    ax2_twin.set_ylabel("Young Ratio", color="black", fontweight="bold")
    ax2_twin.tick_params(axis='y', labelcolor="black")
    axes[2].set_xlabel("Sampling Date (Year)", fontsize=11, fontweight="bold")

    plt.tight_layout()
    plt.savefig(p06, dpi=dpi, bbox_inches="tight")
    plt.close()
    generated["06_Temperature_Trend"] = p06

    # Figure 07: Graham Ratio vs Temperature
    p07 = os.path.join(figures_dir, "07_Graham_vs_Temperature.png")
    save_scatter_with_regression(df, "Temperature_C", "Graham_Ratio",
                                 "Temperature (°C)", r"Graham Ratio ($100 \cdot CO / \Delta O_2$)",
                                 "Mine Fire Temperature vs. Graham Ratio",
                                 p07, dpi=dpi, color="#2ca02c")
    generated["07_Graham_vs_Temperature"] = p07

    # Figure 08: Young Ratio vs Temperature
    p08 = os.path.join(figures_dir, "08_Young_vs_Temperature.png")
    save_scatter_with_regression(df, "Temperature_C", "Young_Ratio",
                                 "Temperature (°C)", r"Young Ratio ($100 \cdot CO_2 / \Delta O_2$)",
                                 "Mine Fire Temperature vs. Young Ratio",
                                 p08, dpi=dpi, color="#17becf")
    generated["08_Young_vs_Temperature"] = p08

    # Figure 09: CO/CO2 Ratio vs Temperature
    p09 = os.path.join(figures_dir, "09_CO_CO2_vs_Temperature.png")
    save_scatter_with_regression(df, "Temperature_C", "CO_CO2_Ratio",
                                 "Temperature (°C)", "$CO / CO_2$ Ratio (%)",
                                 "Mine Fire Temperature vs. $CO / CO_2$ Ratio",
                                 p09, dpi=dpi, color="#e377c2")
    generated["09_CO_CO2_vs_Temperature"] = p09

    # Figure 10: Jones-Trickett Ratio vs Temperature
    p10 = os.path.join(figures_dir, "10_Jones_Trickett_vs_Temperature.png")
    save_scatter_with_regression(df, "Temperature_C", "Jones_Trickett_Ratio",
                                 "Temperature (°C)", "Jones–Trickett Ratio",
                                 "Mine Fire Temperature vs. Jones–Trickett Ratio",
                                 p10, dpi=dpi, color="#bcbd22")
    generated["10_Jones_Trickett_vs_Temperature"] = p10

    # Figure 11: Willett Ratio vs Temperature
    p11 = os.path.join(figures_dir, "11_Willett_vs_Temperature.png")
    save_scatter_with_regression(df, "Temperature_C", "Willett_Ratio",
                                 "Temperature (°C)", "Willett Ratio",
                                 "Mine Fire Temperature vs. Willett Ratio",
                                 p11, dpi=dpi, color="#8c564b")
    generated["11_Willett_vs_Temperature"] = p11

    # Figure 12: Correlation Matrix Heatmap
    p12 = os.path.join(figures_dir, "12_Correlation_Matrix.png")
    fig, ax = plt.subplots(figsize=(10, 8.5), dpi=dpi)

    candidate_cols = [
        "Temperature_C", "O2_percent", "CO_percent", "CO2_percent",
        "H2_percent", "CH4_percent", "N2_percent", "O2_Deficiency_percent",
        "Graham_Ratio", "Young_Ratio", "CO_CO2_Ratio", "Jones_Trickett_Ratio",
        "Willett_Ratio"
    ]
    sub_df = df[candidate_cols].dropna(how="all", axis=1)
    corr = sub_df.corr(method="pearson")

    # Rename for cleaner plot labels
    display_names = {
        "Temperature_C": "Temp (°C)",
        "O2_percent": "$O_2$ (%)",
        "CO_percent": "CO (%)",
        "CO2_percent": "$CO_2$ (%)",
        "H2_percent": "$H_2$ (%)",
        "CH4_percent": "$CH_4$ (%)",
        "N2_percent": "$N_2$ (%)",
        "O2_Deficiency_percent": r"$\Delta O_2$ (%)",
        "Graham_Ratio": "Graham",
        "Young_Ratio": "Young",
        "CO_CO2_Ratio": "$CO/CO_2$",
        "Jones_Trickett_Ratio": "Jones-Trickett",
        "Willett_Ratio": "Willett"
    }
    corr_renamed = corr.rename(index=display_names, columns=display_names)

    sns.heatmap(corr_renamed, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1,
                linewidths=0.5, ax=ax, cbar_kws={'label': 'Pearson Correlation Coefficient (r)'})
    ax.set_title("Pearson Correlation Heatmap — Mine Fire Gases & Indices (N=14)", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(p12, dpi=dpi, bbox_inches="tight")
    plt.close()
    generated["12_Correlation_Matrix"] = p12

    # Figure 13: Multi-Gas Comparison (Normalized 0-1 across samples)
    p13 = os.path.join(figures_dir, "13_Multi_Gas_Comparison.png")
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=dpi)

    norm_df = pd.DataFrame()
    norm_cols = ["Temperature_C", "CO_percent", "CO2_percent", "O2_percent", "H2_percent", "CH4_percent"]
    for col in norm_cols:
        series = df[col]
        min_v, max_v = series.min(), series.max()
        if max_v > min_v:
            norm_df[col] = (series - min_v) / (max_v - min_v)
        else:
            norm_df[col] = 0.0

    sample_labels = [f"S{int(r['Sample_No'])}\n{r['Date']}" for _, r in df.iterrows()]
    x_indices = np.arange(len(df))

    ax.plot(x_indices, norm_df["Temperature_C"], 'r-o', linewidth=2.0, label="Temperature (Normalized)")
    ax.plot(x_indices, norm_df["CO_percent"], 'm-^', linewidth=1.8, label="CO (Normalized)")
    ax.plot(x_indices, norm_df["CO2_percent"], 'g-s', linewidth=1.5, label="$CO_2$ (Normalized)")
    ax.plot(x_indices, norm_df["O2_percent"], 'b-d', linewidth=1.5, label="$O_2$ (Normalized)")
    ax.plot(x_indices, norm_df["H2_percent"], 'c--v', linewidth=1.4, label="$H_2$ (Normalized)")
    ax.plot(x_indices, norm_df["CH4_percent"], 'orange', linestyle=":", marker="p", linewidth=1.4, label="$CH_4$ (Normalized)")

    ax.set_xticks(x_indices)
    ax.set_xticklabels(sample_labels, rotation=45, ha="right", fontsize=8.5)
    ax.set_ylabel("Normalized Value (0.0 to 1.0)", fontsize=11, fontweight="bold")
    ax.set_title("Multi-Gas & Temperature Normalized Profile across Lodna Mine Fire Samples",
                 fontsize=13, fontweight="bold", pad=12)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper right", framealpha=0.9, fontsize=9.5)

    note_msg = "Note: Min-Max normalization is performed solely for visual cross-comparison and does not alter original gas values."
    ax.text(0.01, 0.02, note_msg, transform=ax.transAxes, fontsize=8, fontstyle="italic")

    plt.tight_layout()
    plt.savefig(p13, dpi=dpi, bbox_inches="tight")
    plt.close()
    generated["13_Multi_Gas_Comparison"] = p13

    # Import coward diagram module function
    from src.coward_diagram import plot_coward_diagram

    # Figure 14: Coward Diagram with 14 Samples
    p14 = os.path.join(figures_dir, "14_Coward_Diagram.png")
    plot_coward_diagram(df, p14, dilution_df=None, is_verified=is_verified, ref_note=ref_note, dpi=dpi)
    generated["14_Coward_Diagram"] = p14

    # Figure 15: Coward Diagram with Dilution Trajectory
    p15 = os.path.join(figures_dir, "15_Coward_Diagram_With_Dilution.png")
    plot_coward_diagram(df, p15, dilution_df=dilution_df, is_verified=is_verified, ref_note=ref_note, dpi=dpi)
    generated["15_Coward_Diagram_With_Dilution"] = p15

    return generated
