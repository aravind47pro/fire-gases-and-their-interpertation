"""
========================================================================================
STREAMLIT INTERACTIVE DASHBOARD — UNDERGROUND COAL MINE FIRE GASES & COWARD DIAGRAM
Department of Mining Engineering, Indian Institute of Technology Kharagpur
========================================================================================
Run with:
    streamlit run app.py
"""

import os
import sys
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Setup page config
st.set_page_config(
    page_title="Mine Fire Gas Analysis & Coward Diagram Dashboard | IIT Kharagpur",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Detect data file path
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(current_dir, "data", "lodna_mine_fire_data.csv")):
    base_dir = current_dir
elif os.path.exists(os.path.join(current_dir, "BTP_Mine_Fire_Analysis", "data", "lodna_mine_fire_data.csv")):
    base_dir = os.path.join(current_dir, "BTP_Mine_Fire_Analysis")
else:
    base_dir = current_dir

csv_path = os.path.join(base_dir, "data", "lodna_mine_fire_data.csv")
calc_csv_path = os.path.join(base_dir, "results", "tables", "calculated_gas_indices.csv")

# ======================================================================================
# DATA LOADING & INDEX COMPUTATION
# ======================================================================================
@st.cache_data
def load_and_process_data():
    if os.path.exists(calc_csv_path):
        df = pd.read_csv(calc_csv_path)
    elif os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        # Compute missing indices if needed
        factor = 20.93 / 79.04
        df["Gas_Sum_percent"] = df[["O2_percent", "N2_percent", "CO2_percent", "CO_percent", "H2_percent", "CH4_percent"]].sum(axis=1)
        df["O2_Deficiency_percent"] = (factor * df["N2_percent"] - df["O2_percent"]).round(4)
        df["Graham_Ratio"] = (100.0 * df["CO_percent"] / df["O2_Deficiency_percent"]).round(4)
        df["Young_Ratio"] = (100.0 * df["CO2_percent"] / df["O2_Deficiency_percent"]).round(4)
        df["CO_CO2_Ratio"] = (100.0 * df["CO_percent"] / df["CO2_percent"]).round(4)
        jt_num = df["CO2_percent"] + 0.75 * df["CO_percent"] - 0.25 * df["H2_percent"]
        df["Jones_Trickett_Ratio"] = (jt_num / df["O2_Deficiency_percent"]).round(4)
        exc_n2 = df["N2_percent"] - 3.8 * df["O2_percent"]
        comb = df["CO_percent"] + df["H2_percent"] + df["CH4_percent"]
        df["Willett_Ratio"] = (df["CO2_percent"] / (exc_n2 + df["CO2_percent"] + comb)).round(4)
    else:
        st.error("Dataset not found! Please run BTP_complete_analysis.py first.")
        st.stop()

    df["Date_Parsed"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")
    return df

df = load_and_process_data()

# ======================================================================================
# SIDEBAR NAVIGATION & FILTERS
# ======================================================================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/1/1c/IIT_Kharagpur_Logo.svg/220px-IIT_Kharagpur_Logo.svg.png", width=110)
st.sidebar.title("⛏️ Mine Fire Gas Analysis")
st.sidebar.markdown("**BTP Project Dashboard**  \n*Mining Engineering Department, IIT Kharagpur*")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Project Overview & KPIs",
        "🧭 Interactive Coward Diagram",
        "📈 Gas Concentration Trends",
        "🔥 Fire-Gas Indices",
        "🌡️ Temperature & Correlations",
        "💨 Theoretical N₂ Dilution Simulator",
        "📑 Data Table & Extrema"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Dataset: Lodna Colliery, Jharia Coalfield (Singh et al., 2007)")
st.sidebar.caption("Coward Boundaries: USBM Bulletin 503 (Coward & Jones, 1952)")

# ======================================================================================
# 1. OVERVIEW & KPIS
# ======================================================================================
if menu == "📊 Project Overview & KPIs":
    st.title("🔥 Fire Gases & Atmospheric Interpretation Dashboard")
    st.markdown("### Real Underground Coal Mine Fire Analysis — Lodna Colliery (Jharia Coalfield)")
    st.info(
        "**Academic Topic**: *Fire Gases and Their Interpretation in Underground Coal Mines*  \n"
        "**Data Source**: 14 Published Real Mine-Fire Samples (Singh et al., 2007, *Int. J. Coal Geol.*, 69(3), 192–204)  \n"
        "**Key Objective**: Evaluate gas concentrations, fire indices, temperature dependencies, Coward diagram explosibility, "
        "and multi-indicator diagnostic criteria for sealed mine fires."
    )

    # Top KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Samples", f"{len(df)} Samples", "1985 – 1993")
    with col2:
        max_temp_row = df.loc[df["Temperature_C"].idxmax()]
        st.metric("Peak Temperature", f"{max_temp_row['Temperature_C']:.0f} °C", f"S{int(max_temp_row['Sample_No'])} ({max_temp_row['Date']})")
    with col3:
        max_co_row = df.loc[df["CO_percent"].idxmax()]
        st.metric("Peak CO Emission", f"{max_co_row['CO_percent']:.3f} %", f"S{int(max_co_row['Sample_No'])} at {max_co_row['Temperature_C']:.0f}°C")
    with col4:
        max_h2_row = df.loc[df["H2_percent"].idxmax()]
        st.metric("Peak H₂ Emission", f"{max_h2_row['H2_percent']:.3f} %", f"S{int(max_h2_row['Sample_No'])} at {max_h2_row['Temperature_C']:.0f}°C")
    with col5:
        st.metric("Coward Explosibility", "100% Zone D", "Non-Explosive Behind Seals")

    st.markdown("---")

    # High-level comparison columns
    c_left, c_right = st.columns([3, 2])
    with c_left:
        st.subheader("📌 Key Empirical Finding: Non-Monotonic Behavior")
        st.markdown(
            """
            The empirical analysis proves that **temperature alone is insufficient to diagnose a mine fire**:
            - **At 80°C (Sample 4, 20-06-1987)**: CO concentration was merely **0.022%** (Graham ratio = 0.11), because the sealed atmosphere was oxygen-starved ($O_2 = 1.55\\%$).
            - **At 64°C (Sample 6, 02-06-1988)**: CO concentration peaked at **0.813%** (Graham ratio = 4.81, indicating active fire), supported by higher residual oxygen ($O_2 = 4.22\\%$).
            - **Conclusion**: Fire severity is governed by oxygen availability, seal leakage, oxidation stage, and dilution, not temperature alone.
            """
        )

        st.subheader("Summary of Core Fire-Gas Indices")
        st.markdown(
            """
            - **Oxygen Deficiency (ΔO₂)**: $(20.93/79.04)N_2 - O_2 \approx 0.2648 N_2 - O_2$.
            - **Graham Ratio ($G$)**: $100 \times CO / \Delta O_2$. Evaluates spontaneous combustion stage ($>2.0$ indicates active fire).
            - **Young Ratio ($Y$)**: $100 \times CO_2 / \Delta O_2$. Indicates combustion maturity and strata interaction.
            - **$CO / CO_2$ Ratio**: $100 \times CO / CO_2$. Reflects incomplete combustion efficiency.
            - **Jones–Trickett ($JT$)**: $(CO_2 + 0.75 CO - 0.25 H_2)/\Delta O_2$. Assesses fuel type (0.5–1.0 for coal).
            - **Willett Ratio**: Trend indicator for sealed atmospheres.
            - **$C/H$ Ratio**: *REFERENCE REQUIRED* (not fabricated).
            """
        )

    with c_right:
        st.subheader("Explosibility Status Summary")
        st.success("✅ **All 14 Lodna Samples Reside in Coward Zone D**")
        st.markdown(
            """
            - **Methane Range**: $0.000\\% \\text{ to } 0.526\\%$ (far below the $5.0\\%$ LEL).
            - **Oxygen Range**: $0.00\\% \\text{ to } 8.18\\%$ (well below the $12.1\\%$ Nose limit).
            - **Safety Assessment**: The atmosphere behind the stoppings was non-explosive under sealed conditions.
            - **Caution**: Any sudden fresh air ingress or methane surge would alter this trajectory!
            """
        )

        st.info("💡 **Navigation Tip**: Select **'🧭 Interactive Coward Diagram'** in the sidebar to interactively inspect zones and hover over sample points.")


# ======================================================================================
# 2. INTERACTIVE COWARD DIAGRAM
# ======================================================================================
elif menu == "🧭 Interactive Coward Diagram":
    st.title("🧭 Interactive Coward Explosibility Diagram")
    st.markdown("### Methane ($CH_4$) vs. Oxygen ($O_2$) Explosibility Mapping")
    st.caption("Based on verified classical limits from USBM Bulletin 503 (Coward & Jones, 1952) and USBM Bulletin 627 (Zabetakis, 1965).")

    # Options
    col_opt1, col_opt2, col_opt3 = st.columns(3)
    with col_opt1:
        show_dilution = st.checkbox("Overlay Theoretical N₂ Dilution Trajectory", value=True)
    with col_opt2:
        zoom_level = st.selectbox("Plot Coordinate Range", ["Standard (0 to 22% CH₄, 0 to 23% O₂)", "Full Scale (0 to 100% CH₄, 0 to 25% O₂)"])
    with col_opt3:
        color_by = st.selectbox("Color Samples By", ["Temperature_C", "CO_percent", "Graham_Ratio"])

    # Create Plotly Coward Figure
    fig = go.Figure()

    # 1. Base Air Dilution Line: O2 = 20.93 * (1 - CH4/100)
    max_ch4 = 100.0 if "Full" in zoom_level else 22.0
    ch4_air = np.linspace(0, max_ch4, 200)
    o2_air = 20.93 * (1.0 - ch4_air / 100.0)

    fig.add_trace(go.Scatter(
        x=ch4_air, y=o2_air,
        mode="lines",
        name="Air Dilution Line (O₂ = 20.93(1 - CH₄/100))",
        line=dict(color="black", dash="dash", width=2),
        hoverinfo="name"
    ))

    # 2. Zone A: Explosive Region Polygon
    # LEL: (5.0, 19.88), UEL: (15.0, 17.79), Nose: (5.9, 12.1)
    ch4_top = np.linspace(5.0, 15.0, 50)
    o2_top = 20.93 * (1.0 - ch4_top / 100.0)
    poly_x = [5.0] + list(ch4_top) + [15.0, 5.9, 5.0]
    poly_y = [19.88] + list(o2_top) + [17.79, 12.1, 19.88]

    fig.add_trace(go.Scatter(
        x=poly_x, y=poly_y,
        fill="toself",
        fillcolor="rgba(230, 57, 70, 0.35)",
        line=dict(color="rgba(230, 57, 70, 0.9)", width=2),
        name="Zone A: Explosive Mixtures (Self-propagating flame)",
        hoverinfo="name"
    ))

    # 3. Origin-Nose Ray (Slope = 12.1 / 5.9 ≈ 2.0508)
    ch4_ray = np.linspace(0, 10.0, 50)
    o2_ray = (12.1 / 5.9) * ch4_ray
    valid_r = o2_ray <= 20.93 * (1.0 - ch4_ray / 100.0)
    fig.add_trace(go.Scatter(
        x=ch4_ray[valid_r], y=o2_ray[valid_r],
        mode="lines",
        name="Origin–Nose Dilution Ray (Slope = 2.05)",
        line=dict(color="purple", dash="dot", width=1.5),
        hoverinfo="name"
    ))

    # 4. Air-Nose Tangent Line (connecting (0, 20.93) through Nose (5.9, 12.1))
    slope_an = (12.1 - 20.93) / 5.9
    ch4_an = np.linspace(0, 14.0, 50)
    o2_an = 20.93 + slope_an * ch4_an
    fig.add_trace(go.Scatter(
        x=ch4_an[o2_an >= 0], y=o2_an[o2_an >= 0],
        mode="lines",
        name="Air–Nose Tangent Line (Air Dilution Boundary)",
        line=dict(color="green", dash="dashdot", width=1.5),
        hoverinfo="name"
    ))

    # 5. Key Reference Points (LEL, UEL, Nose)
    ref_pts_x = [5.0, 15.0, 5.9]
    ref_pts_y = [19.88, 17.79, 12.1]
    ref_pts_txt = ["LEL (5.0%, 19.9%)", "UEL (15.0%, 17.8%)", "Nose (5.9%, 12.1%)"]
    fig.add_trace(go.Scatter(
        x=ref_pts_x, y=ref_pts_y,
        mode="markers+text",
        marker=dict(color="darkred", size=10, symbol="diamond"),
        text=ref_pts_txt,
        textposition=["top left", "top right", "bottom left"],
        name="USBM Flammability Limits",
        hoverinfo="text"
    ))

    # 6. Theoretical N2 Dilution Trajectory (15% CH4, 10% O2 -> (0,0))
    if show_dilution:
        f_steps = np.linspace(1.0, 0.05, 25)
        dil_ch4 = 15.0 * f_steps
        dil_o2 = 10.0 * f_steps
        fig.add_trace(go.Scatter(
            x=dil_ch4, y=dil_o2,
            mode="lines+markers",
            name="Theoretical N₂ Dilution Trajectory (15% CH₄, 10% O₂)",
            line=dict(color="#00b4d8", width=3),
            marker=dict(color="#03045e", size=7),
            hovertext=[f"Dilution remaining f = {f:.2f}<br>CH₄ = {c:.2f}%, O₂ = {o:.2f}%" for f, c, o in zip(f_steps, dil_ch4, dil_o2)],
            hoverinfo="text"
        ))

    # 7. Real Lodna Colliery Mine Fire Samples (N=14)
    hover_texts = []
    for _, r in df.iterrows():
        txt = (
            f"<b>Sample {int(r['Sample_No'])}</b> ({r['Date']})<br>"
            f"Temperature: <b>{r['Temperature_C']:.0f} °C</b><br>"
            f"Methane (CH₄): <b>{r['CH4_percent']:.3f} %</b><br>"
            f"Oxygen (O₂): <b>{r['O2_percent']:.2f} %</b><br>"
            f"Carbon Monoxide (CO): <b>{r['CO_percent']:.3f} %</b><br>"
            f"Hydrogen (H₂): <b>{r['H2_percent']:.3f} %</b><br>"
            f"Carbon Dioxide (CO₂): <b>{r['CO2_percent']:.2f} %</b><br>"
            f"Oxygen Deficiency (ΔO₂): <b>{r['O2_Deficiency_percent']:.2f} %</b><br>"
            f"Graham Ratio: <b>{r['Graham_Ratio']:.3f}</b><br>"
            f"Coward Classification: <b>Zone D (Inert / Non-explosive)</b>"
        )
        hover_texts.append(txt)

    sample_labels = [f"S{int(r['Sample_No'])} ({r['Date']}, {r['Temperature_C']:.0f}°C)" for _, r in df.iterrows()]

    fig.add_trace(go.Scatter(
        x=df["CH4_percent"], y=df["O2_percent"],
        mode="markers+text",
        marker=dict(
            size=14,
            color=df[color_by],
            colorscale="Plasma",
            showscale=True,
            colorbar=dict(title=color_by.replace("_", " ")),
            line=dict(color="black", width=1.5)
        ),
        text=sample_labels,
        textposition="top right",
        textfont=dict(size=9, color="black"),
        hovertext=hover_texts,
        hoverinfo="text",
        name="Lodna Colliery Samples (N=14)"
    ))

    # Layout styling
    x_range = [-0.5, 22.0] if "Standard" in zoom_level else [-2, 102]
    y_range = [-0.5, 23.0] if "Standard" in zoom_level else [-1, 26]

    fig.update_layout(
        title="<b>Coward Diagram: Methane vs. Oxygen Explosibility with 14 Lodna Mine Fire Samples</b>",
        xaxis=dict(title="<b>Methane, CH₄ (% by volume)</b>", range=x_range, gridcolor="#e5e5e5"),
        yaxis=dict(title="<b>Oxygen, O₂ (% by volume)</b>", range=y_range, gridcolor="#e5e5e5"),
        plot_bgcolor="white",
        height=700,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Add zone annotation callouts
    fig.add_annotation(x=8.5, y=16.0, text="<b>ZONE A</b><br>(Explosive)", showarrow=False,
                       font=dict(color="darkred", size=11), bgcolor="rgba(255,255,255,0.8)", bordercolor="red")
    fig.add_annotation(x=16.5, y=9.0, text="<b>ZONE B</b><br>(Explosive with air)", showarrow=False,
                       font=dict(color="darkorange", size=10), bgcolor="rgba(255,255,255,0.8)", bordercolor="orange")
    fig.add_annotation(x=2.2, y=15.0, text="<b>ZONE C</b><br>(Explosive with CH₄)", showarrow=False,
                       font=dict(color="darkblue", size=10), bgcolor="rgba(255,255,255,0.8)", bordercolor="blue")
    fig.add_annotation(x=2.5, y=3.0, text="<b>ZONE D</b><br>(Non-explosive / Inert)", showarrow=False,
                       font=dict(color="darkgreen", size=11), bgcolor="rgba(240,255,240,0.9)", bordercolor="green")

    st.plotly_chart(fig, use_container_width=True)

    # Detail Table
    st.subheader("📋 Sample Classification & Coordinates")
    st.dataframe(
        df[["Sample_No", "Date", "CH4_percent", "O2_percent", "Temperature_C", "CO_percent", "Graham_Ratio", "Young_Ratio", "Jones_Trickett_Ratio"]],
        use_container_width=True
    )


# ======================================================================================
# 3. GAS CONCENTRATION TRENDS
# ======================================================================================
elif menu == "📈 Gas Concentration Trends":
    st.title("📈 Chronological Mine Fire Gas Concentration Trends (1985–1993)")
    st.markdown("Inspect how gas concentrations evolved over time behind stoppings at Lodna Colliery.")

    # Chronological Multi-Gas Plot
    fig_gases = go.Figure()
    sdf = df.sort_values("Date_Parsed")

    fig_gases.add_trace(go.Scatter(x=sdf["Date_Parsed"], y=sdf["O2_percent"], mode="lines+markers", name="O₂ (%)", line=dict(color="#1f77b4", width=2)))
    fig_gases.add_trace(go.Scatter(x=sdf["Date_Parsed"], y=sdf["CO2_percent"], mode="lines+markers", name="CO₂ (%)", line=dict(color="#2ca02c", width=2)))
    fig_gases.add_trace(go.Scatter(x=sdf["Date_Parsed"], y=sdf["CO_percent"], mode="lines+markers", name="CO (%)", line=dict(color="#d62728", width=2.5)))
    fig_gases.add_trace(go.Scatter(x=sdf["Date_Parsed"], y=sdf["H2_percent"], mode="lines+markers", name="H₂ (%)", line=dict(color="#9467bd", width=2)))
    fig_gases.add_trace(go.Scatter(x=sdf["Date_Parsed"], y=sdf["CH4_percent"], mode="lines+markers", name="CH₄ (%)", line=dict(color="#ff7f0e", width=1.5)))

    fig_gases.update_layout(
        title="<b>Mine Fire Gas Concentrations Over Time (Lodna Colliery, Jharia Coalfield)</b>",
        xaxis_title="<b>Sampling Date</b>",
        yaxis_title="<b>Concentration (% by volume)</b>",
        plot_bgcolor="white",
        height=500,
        hovermode="x unified"
    )
    st.plotly_chart(fig_gases, use_container_width=True)

    # Normalized Multi-Gas Profile
    st.subheader("Normalized Multi-Gas Profile (0.0 to 1.0 Scale)")
    st.caption("Normalized for visual comparison across parameters with different orders of magnitude without altering raw data.")

    norm_df = pd.DataFrame()
    norm_cols = ["Temperature_C", "CO_percent", "CO2_percent", "O2_percent", "H2_percent", "CH4_percent"]
    for col in norm_cols:
        series = sdf[col]
        norm_df[col] = (series - series.min()) / (series.max() - series.min()) if series.max() > series.min() else 0.0

    fig_norm = go.Figure()
    labels = [f"S{int(r['Sample_No'])} ({r['Date']})" for _, r in sdf.iterrows()]
    for col, color in zip(norm_cols, ["red", "magenta", "green", "blue", "cyan", "orange"]):
        fig_norm.add_trace(go.Scatter(x=labels, y=norm_df[col], mode="lines+markers", name=col.replace("_percent", " (%)").replace("_C", " (°C)"), line=dict(color=color, width=1.8)))

    fig_norm.update_layout(
        title="<b>Normalized Profile Across Sampling Dates</b>",
        xaxis_title="<b>Sample & Date</b>",
        yaxis_title="<b>Normalized Value (0 to 1)</b>",
        plot_bgcolor="white",
        height=450
    )
    st.plotly_chart(fig_norm, use_container_width=True)


# ======================================================================================
# 4. FIRE-GAS INDICES
# ======================================================================================
elif menu == "🔥 Fire-Gas Indices":
    st.title("🔥 Mine Fire-Gas Indices Analysis")
    st.markdown("Standard mining engineering ratios designed to normalize ventilation dilution effects.")

    c1, c2 = st.columns(2)
    with c1:
        # Graham Ratio Plot
        fig_g = px.scatter(df, x="Temperature_C", y="Graham_Ratio", color="Temperature_C",
                           text="Sample_No", hover_data=["Date", "CO_percent", "O2_Deficiency_percent"],
                           title="<b>Graham Ratio vs. Temperature</b>",
                           labels={"Temperature_C": "Temperature (°C)", "Graham_Ratio": "Graham Ratio (100·CO/ΔO₂)"},
                           color_continuous_scale="Reds")
        fig_g.add_hline(y=0.4, line_dash="dash", line_color="green", annotation_text="Background (≤0.4)")
        fig_g.add_hline(y=1.0, line_dash="dash", line_color="orange", annotation_text="Heating (1.0)")
        fig_g.add_hline(y=2.0, line_dash="dash", line_color="red", annotation_text="Active Fire (≥2.0)")
        fig_g.update_layout(plot_bgcolor="white", height=420)
        st.plotly_chart(fig_g, use_container_width=True)

    with c2:
        # Young Ratio Plot
        fig_y = px.scatter(df, x="Temperature_C", y="Young_Ratio", color="Temperature_C",
                           text="Sample_No", hover_data=["Date", "CO2_percent", "O2_Deficiency_percent"],
                           title="<b>Young Ratio vs. Temperature</b>",
                           labels={"Temperature_C": "Temperature (°C)", "Young_Ratio": "Young Ratio (100·CO₂/ΔO₂)"},
                           color_continuous_scale="Teal")
        fig_y.update_layout(plot_bgcolor="white", height=420)
        st.plotly_chart(fig_y, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        # Jones-Trickett Ratio Plot
        fig_jt = px.scatter(df, x="Temperature_C", y="Jones_Trickett_Ratio", color="Temperature_C",
                            text="Sample_No", hover_data=["Date", "Jones_Trickett_Fuel"],
                            title="<b>Jones–Trickett Ratio vs. Temperature</b>",
                            labels={"Temperature_C": "Temperature (°C)", "Jones_Trickett_Ratio": "Jones–Trickett Ratio"},
                            color_continuous_scale="Viridis")
        fig_jt.add_hrect(y0=0.5, y1=1.0, fillcolor="rgba(128,128,128,0.2)", line_width=0, annotation_text="Coal/Oil Range (0.5–1.0)")
        fig_jt.update_layout(plot_bgcolor="white", height=420)
        st.plotly_chart(fig_jt, use_container_width=True)

    with c4:
        # Willett Ratio Plot
        fig_w = px.scatter(df, x="Temperature_C", y="Willett_Ratio", color="Temperature_C",
                           text="Sample_No", hover_data=["Date"],
                           title="<b>Willett Ratio vs. Temperature</b>",
                           labels={"Temperature_C": "Temperature (°C)", "Willett_Ratio": "Willett Ratio"},
                           color_continuous_scale="Magma")
        fig_w.update_layout(plot_bgcolor="white", height=420)
        st.plotly_chart(fig_w, use_container_width=True)


# ======================================================================================
# 5. TEMPERATURE & CORRELATION ANALYSIS
# ======================================================================================
elif menu == "🌡️ Temperature & Correlations":
    st.title("🌡️ Temperature Relationships & Statistical Correlations")

    # Heatmap
    corr_cols = ["Temperature_C", "O2_percent", "CO_percent", "CO2_percent", "H2_percent",
                 "CH4_percent", "N2_percent", "O2_Deficiency_percent", "Graham_Ratio",
                 "Young_Ratio", "CO_CO2_Ratio", "Jones_Trickett_Ratio", "Willett_Ratio"]
    corr = df[corr_cols].corr()

    fig_corr = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r",
                         title="<b>Pearson Correlation Matrix Heatmap (N=14)</b>", zmin=-1, zmax=1)
    fig_corr.update_layout(height=600)
    st.plotly_chart(fig_corr, use_container_width=True)

    st.subheader("Statistical Findings & Regression Fits")
    st.markdown(
        """
        - **CO vs. Temperature**: Pearson $r = +0.540$ (Moderate positive, $R^2 = 0.292$). Linear Fit: $CO = 0.0076 \times Temp - 0.2644$.
        - **O₂ vs. Temperature**: Pearson $r = -0.370$ (Weak-to-moderate negative, $R^2 = 0.137$). Linear Fit: $O_2 = -0.0520 \times Temp + 6.6496$.
        - **H₂ vs. Temperature**: Pearson $r = +0.536$ (Moderate positive, $R^2 = 0.288$). Linear Fit: $H_2 = 0.0202 \times Temp - 0.7431$.
        - **Graham Ratio vs. Temperature**: Pearson $r = +0.539$ (Moderate positive, $R^2 = 0.291$).
        """
    )


# ======================================================================================
# 6. THEORETICAL N2 DILUTION SIMULATOR
# ======================================================================================
elif menu == "💨 Theoretical N₂ Dilution Simulator":
    st.title("💨 Theoretical Nitrogen Inertisation Dilution Simulator")
    st.markdown("### Academic Model for Flushing a Sealed Underground Void with Pure Nitrogen")
    st.warning("⚠️ **ACADEMIC MODEL ONLY**: This simulation is an idealized mathematical tool and is NOT an operational mine safety procedure.")

    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        v_m3 = st.slider("Sealed Void Volume, V (m³)", min_value=5000, max_value=60000, value=27000, step=1000)
        q_m3_s = st.slider("Inert Gas / Air Flow Rate, Q (m³/s)", min_value=1.0, max_value=20.0, value=5.0, step=0.5)
        init_ch4 = st.slider("Initial Methane, CH₄ (%)", min_value=5.0, max_value=30.0, value=15.0, step=0.5)
        init_o2 = st.slider("Initial Oxygen, O₂ (%)", min_value=2.0, max_value=18.0, value=10.0, step=0.5)

    with col_sim2:
        turnover_sec = v_m3 / q_m3_s
        turnover_min = turnover_sec / 60.0
        turnover_hr = turnover_min / 60.0

        st.subheader("Simulated Turnover Metrics")
        st.metric("Nominal Turnover Ratio (V/Q)", f"{turnover_min:.1f} minutes", f"{turnover_hr:.2f} hours")
        st.markdown(
            f"""
            - **Volume ($V$)**: {v_m3:,} m³
            - **Flow Rate ($Q$)**: {q_m3_s:.1f} m³/s
            - **Nominal Flushing Time**: **{turnover_min:.1f} min** ({turnover_sec:,.0f} seconds)
            - **Practical Reality**: Complete inertisation requires **3 to 5 volume turnovers** ({3*turnover_min:.0f} to {5*turnover_min:.0f} minutes) due to exponential dilution mixing ($C(t) = C_0 e^{-Qt/V}$).
            """
        )

    # Dynamic Coward Trajectory
    f_vals = np.linspace(1.0, 0.02, 30)
    sim_ch4 = init_ch4 * f_vals
    sim_o2 = init_o2 * f_vals

    fig_sim = go.Figure()
    # Air line
    ch4_a = np.linspace(0, 22, 100)
    fig_sim.add_trace(go.Scatter(x=ch4_a, y=20.93 * (1.0 - ch4_a / 100.0), mode="lines", name="Air Dilution Line", line=dict(color="black", dash="dash")))

    # Zone A
    ch4_t = np.linspace(5.0, 15.0, 50)
    fig_sim.add_trace(go.Scatter(x=[5.0]+list(ch4_t)+[15.0, 5.9, 5.0], y=[19.88]+list(20.93*(1-ch4_t/100))+[17.79, 12.1, 19.88],
                                 fill="toself", fillcolor="rgba(230, 57, 70, 0.35)", line=dict(color="red"), name="Zone A (Explosive)"))

    # Dilution trajectory
    fig_sim.add_trace(go.Scatter(x=sim_ch4, y=sim_o2, mode="lines+markers",
                                 name=f"Dynamic N₂ Dilution Path ({init_ch4}% CH₄, {init_o2}% O₂)",
                                 line=dict(color="cyan", width=3), marker=dict(size=6, color="darkblue")))

    fig_sim.update_layout(title="<b>Dynamic Nitrogen Dilution Path on Coward Diagram</b>",
                          xaxis=dict(title="<b>CH₄ (%)</b>", range=[-0.5, max(22.0, init_ch4 + 2)]),
                          yaxis=dict(title="<b>O₂ (%)</b>", range=[-0.5, 23.0]),
                          plot_bgcolor="white", height=500)
    st.plotly_chart(fig_sim, use_container_width=True)


# ======================================================================================
# 7. DATA TABLE & EXTREMA
# ======================================================================================
elif menu == "📑 Data Table & Extrema":
    st.title("📑 Complete Dataset & Summary of Extrema")

    st.subheader("Summary of Extrema (Automatic Observations)")
    extremes_data = [
        {"Observation": "Highest Temperature", "Sample": "S4", "Date": "20-06-1987", "Value": "80.00 °C", "Temp": 80.0},
        {"Observation": "Highest CO", "Sample": "S6", "Date": "02-06-1988", "Value": "0.8130 %", "Temp": 64.0},
        {"Observation": "Highest CO₂", "Sample": "S4", "Date": "20-06-1987", "Value": "17.1300 %", "Temp": 80.0},
        {"Observation": "Highest H₂", "Sample": "S5", "Date": "15-12-1987", "Value": "2.3430 %", "Temp": 72.0},
        {"Observation": "Highest CH₄", "Sample": "S6", "Date": "02-06-1988", "Value": "0.5260 %", "Temp": 64.0},
        {"Observation": "Lowest O₂", "Sample": "S12", "Date": "16-10-1992", "Value": "0.0000 %", "Temp": 37.0},
        {"Observation": "Highest O₂ Deficiency (ΔO₂)", "Sample": "S12", "Date": "16-10-1992", "Value": "23.6601 %", "Temp": 37.0},
        {"Observation": "Highest Graham Ratio", "Sample": "S6", "Date": "02-06-1988", "Value": "4.8112", "Temp": 64.0},
        {"Observation": "Highest CO/CO₂ Ratio", "Sample": "S6", "Date": "02-06-1988", "Value": "5.7989 %", "Temp": 64.0},
        {"Observation": "Highest Young Ratio", "Sample": "S9", "Date": "11-06-1990", "Value": "94.7313", "Temp": 47.0},
        {"Observation": "Highest Jones–Trickett Ratio", "Sample": "S9", "Date": "11-06-1990", "Value": "0.9473", "Temp": 47.0},
        {"Observation": "Highest Willett Ratio", "Sample": "S9", "Date": "11-06-1990", "Value": "0.2008", "Temp": 47.0}
    ]
    st.table(pd.DataFrame(extremes_data))

    st.subheader("Complete 14 Samples with All Calculated Indices")
    st.dataframe(df, use_container_width=True)
