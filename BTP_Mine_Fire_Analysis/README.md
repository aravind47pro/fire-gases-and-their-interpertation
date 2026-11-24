# BTP Project: Fire Gases and Their Interpretation in Underground Coal Mines

**Department of Mining Engineering**  
**Indian Institute of Technology Kharagpur**  
**Topic:** *Fire Gases and Their Interpretation in Underground Coal Mines*  
**Primary Dataset:** 14 Real Mine-Fire Samples from Lodna Colliery, Jharia Coalfield, India  
**Reference:** Singh et al. (2007), *Mine fire gas indices and their application to Indian underground coal mine fires*, International Journal of Coal Geology, 69(3), 192–204. DOI: [10.1016/j.coal.2006.04.004](https://doi.org/10.1016/j.coal.2006.04.004).

---

## 1. Project Overview

This repository provides a reproducible, research-grade Python analysis system developed for BTech/MTech Mining Engineering BTP analysis, supervisor discussions, viva preparation, and final report generation.

The software performs:
1. **Gas Composition Validation**: Checks that each gas sample sum equals 100% within acceptable analytical tolerance (±1.0%) without altering raw field measurements.
2. **Oxygen Deficiency Calculation**: Literature-based formula $\Delta O_2 = (20.93/79.04) \times N_2 - O_2 \approx 0.2648 \times N_2 - O_2$.
3. **Fire-Gas Ratios**:
   - **Graham Ratio**: $100 \times CO / \Delta O_2$ (with indicative heating/fire stages; flags low $\Delta O_2 < 0.3\%$).
   - **Young Ratio**: $100 \times CO_2 / \Delta O_2$ (with documentation of strata and carbonate limitations).
   - **$CO/CO_2$ Ratio**: $100 \times CO / CO_2$ (oxidation stage & water solubility effects).
   - **Jones–Trickett Ratio**: $(CO_2 + 0.75 \times CO - 0.25 \times H_2) / \Delta O_2$ (evaluates coal vs timber vs methane fuels).
   - **Willett Ratio**: $CO_2 / (\text{Excess } N_2 + CO_2 + \text{Combustibles})$, where $\text{Excess } N_2 = N_2 - 3.8 \times O_2$.
   - **$C/H$ Ratio**: Marked as **REFERENCE REQUIRED** because definitions vary across literature and no formula was fabricated.
4. **Temperature Relationship & Regression Analysis**: Investigates linear fits, Pearson correlations, $R^2$, and rigorously addresses the 4 key BTP research questions.
5. **Statistical & Correlation Heatmap**: Pearson correlation matrix, descriptive statistics, and extrema identification.
6. **Coward Diagram Representation**:
   - Plots all 14 Lodna samples on the $CH_4$ vs $O_2$ explosibility diagram.
   - Plots verified Coward Zones A, B, C, D, and E based on USBM Bulletin 503 (Coward & Jones, 1952) / USBM Bulletin 627 (Zabetakis, 1965).
   - Classifies every sample into its respective explosibility zone.
7. **Theoretical Nitrogen Dilution Simulation**: Academic simulation of pure $N_2$ injection for a sealed 27,000 m³ void at 5 m³/s, showing trajectory toward origin $(0, 0)$ and explaining why 90 minutes is purely a nominal turnover ratio ($V/Q$) rather than a field safety duration.
8. **Automated Report & 10-Sheet Excel Workbook**: Automatically exports Word (.docx), Markdown (.md), CSVs, and Excel.

---

## 2. Directory Structure

```text
BTP_Mine_Fire_Analysis/
├── data/
│   ├── lodna_mine_fire_data.csv       <- 14 Real published Lodna Colliery samples (Singh et al., 2007)
│   └── normal_air_reference.csv       <- Standard dry air baseline (Volume % vs Mass %)
├── src/
│   ├── __init__.py
│   ├── data_loader.py                 <- Data loading and path validation
│   ├── validation.py                  <- Gas sum validation (100% tolerance check)
│   ├── gas_indices.py                 <- Oxygen deficiency and fire ratio formulas
│   ├── temperature_analysis.py        <- Regressions and answers to 4 research questions
│   ├── correlation_analysis.py        <- Correlation matrix and descriptive statistics
│   ├── coward_diagram.py              <- Coward diagram rendering and zone classification
│   ├── dilution_model.py              <- Theoretical N2 inertisation model
│   ├── plotting.py                    <- Generates all 15 publication figures (300 DPI)
│   ├── excel_exporter.py              <- Formatted 10-sheet Excel workbook export
│   ├── report_generator.py            <- Generates DOCX and MD 9-chapter reports
│   └── main.py                        <- Modular execution pipeline
├── coward/
│   ├── coward_boundaries.csv          <- Published USBM Bulletin 503 boundary coordinates
│   ├── coward_boundaries_template.csv <- Blank configurable template for supervisor coordinates
│   └── README_coward_boundaries.md    <- Coward boundary documentation
├── results/
│   ├── figures/                       <- 15 High-resolution figures (300 DPI PNG)
│   ├── tables/                        <- 6 Processed CSV tables
│   ├── reports/                       <- BTP Report (.docx and .md)
│   └── BTP_Final_Gas_Analysis.xlsx    <- 10-Sheet comprehensive Excel workbook
├── requirements.txt                   <- Python package dependencies
├── README.md                          <- Project documentation
└── BTP_complete_analysis.py           <- Single-file complete analysis runner
```

---

## 3. Simple Step-by-Step Instructions

You do not need to be an expert programmer to run this project. Follow these 5 steps:

### Step 1: Install Python
Ensure Python 3.9+ (or newer) is installed on your computer.

### Step 2: Open Terminal / PowerShell in the Project Directory
Open PowerShell or Command Prompt, and navigate to the project directory:
```powershell
cd c:\Users\Aravind\OneDrive\Desktop\Fire_gas_interpretation\BTP_Mine_Fire_Analysis
```

### Step 3: Install Required Packages
Run:
```powershell
pip install pandas numpy matplotlib seaborn openpyxl scipy python-docx
```

### Step 4: Run the Complete Analysis
Execute:
```powershell
python BTP_complete_analysis.py
```
*(Or `python src/main.py`)*

### Step 5: View All Generated Outputs
Open the `results/` folder:
- **`results/figures/`**: Contains all 15 figures (high-resolution PNG at 300 DPI)
- **`results/tables/`**: Contains all processed CSV tables
- **`results/BTP_Final_Gas_Analysis.xlsx`**: Formatted 10-sheet Excel workbook
- **`results/reports/`**: Full 9-chapter Word report (`.docx`) and Markdown report (`.md`)

---

## 4. Description of Generated Output Files

### High-Resolution Figures (`results/figures/`)
| Figure Name | Description |
|:---|:---|
| `01_CO_vs_Temperature.png` | Scatter plot & linear fit: CO concentration vs Temperature |
| `02_CO2_vs_Temperature.png` | Scatter plot & linear fit: $CO_2$ concentration vs Temperature |
| `03_O2_vs_Temperature.png` | Scatter plot & linear fit: Residual $O_2$ vs Temperature |
| `04_H2_vs_Temperature.png` | Scatter plot & linear fit: Hydrogen $H_2$ vs Temperature |
| `05_CH4_vs_Temperature.png` | Scatter plot & linear fit: Methane $CH_4$ vs Temperature |
| `06_Temperature_Trend.png` | Chronological multi-panel time-series (1985–1993) of Temp, $\Delta O_2$, CO, $H_2$, Graham, and Young ratios |
| `07_Graham_vs_Temperature.png` | Scatter plot & linear fit: Graham Ratio vs Temperature |
| `08_Young_vs_Temperature.png` | Scatter plot & linear fit: Young Ratio vs Temperature |
| `09_CO_CO2_vs_Temperature.png` | Scatter plot & linear fit: $CO/CO_2$ Ratio vs Temperature |
| `10_Jones_Trickett_vs_Temperature.png` | Scatter plot & linear fit: Jones–Trickett Ratio vs Temperature |
| `11_Willett_vs_Temperature.png` | Scatter plot & linear fit: Willett Ratio vs Temperature |
| `12_Correlation_Matrix.png` | Pearson correlation heatmap across all gases, temperature, and indices |
| `13_Multi_Gas_Comparison.png` | Normalized (0 to 1) comparison of all gases across the 14 samples |
| `14_Coward_Diagram.png` | Coward Diagram showing Zones A, B, C, D, E and plotting all 14 Lodna samples with sample labels |
| `15_Coward_Diagram_With_Dilution.png` | Coward Diagram overlaying the theoretical pure $N_2$ dilution trajectory |

### 10-Sheet Excel Workbook (`results/BTP_Final_Gas_Analysis.xlsx`)
1. **Raw Data**: The original 14 Lodna Colliery samples.
2. **Gas Calculations**: Gas sum totals, deviation from 100%, validation status, and oxygen deficiency.
3. **Fire Indices**: Graham, Young, $CO/CO_2$, Jones–Trickett, Willett ratios, and status flags.
4. **Temperature Analysis**: Regression statistics ($r$, $R^2$, slope, intercept, $p$-value, equation).
5. **Correlations**: Full Pearson correlation matrix.
6. **Coward Data**: $CH_4$ %, $O_2$ %, and Temperature for all samples.
7. **Coward Zone Classification**: Sample-by-sample zone assignment (Zone D) and safety interpretation.
8. **Summary**: Summary of extrema (highest CO, highest temp, etc.) and descriptive statistics.
9. **Formula Guide**: Complete mathematical definitions, application benchmarks, and limitations.
10. **Sources & References**: Complete literature citations.

---

## 5. Answers to the 4 Core Research Questions

### Q1: Does CO increase when temperature increases?
- **Finding**: Statistical Pearson correlation is moderately positive ($r = 0.540$), but the relationship is **strictly non-monotonic**.
- **Evidence**: The highest temperature sample (**80°C on 20-06-1987**) recorded a low CO concentration of **0.022%** (Graham ratio = 0.11), whereas the maximum CO (**0.813% on 02-06-1988**) occurred at **64°C**.
- **Explanation**: In sealed underground mine workings, CO production is constrained by oxygen availability, coal surface reactivity, and dilution. High temperature alone does not guarantee high CO.

### Q2: Does O₂ decrease as temperature increases?
- **Finding**: Pearson correlation shows a negative association ($r = -0.370$).
- **Evidence**: Accelerated oxidation at higher temperatures consumes oxygen. However, residual $O_2$ behind seals is heavily governed by seal leakage, barometric breathing, and air ingress. Sample 12 recorded 0.00% $O_2$ at 37°C.

### Q3: Does H₂ increase with temperature?
- **Finding**: Pearson correlation is positive ($r = 0.536$).
- **Evidence**: Hydrogen is generated during high-temperature heating (>250°C at the coal face) and the water-gas shift reaction. The peak $H_2$ (**2.343% on 15-12-1987**) occurred at **72°C**. Samples below 55°C showed 0.000% $H_2$.

### Q4: Does Graham ratio increase with temperature?
- **Finding**: Pearson correlation is positive ($r = 0.539$).
- **Evidence**: Graham ratio reflects the rate of CO formation relative to oxygen consumed. While it generally rises with thermal intensity, it is non-monotonic and serves as an oxidation indicator rather than a direct thermometer.

---

## 6. Coward Diagram & Dilution Caveats

### Real Data Finding
All 14 Lodna Colliery samples lie in **Zone D (Non-explosive / Cannot form explosive mixtures with air alone)**. This occurs because residual oxygen was low ($O_2 \le 8.18\% < 12.1\%$ Nose limit) and methane accumulation was negligible ($CH_4 \le 0.526\% \ll 5.0\%$ LEL).

### Theoretical Academic Model vs. Mine Safety
- The $N_2$ dilution model ($V = 27,000 \text{ m}^3$, $Q = 5 \text{ m}^3/\text{s}$, initial $15\% \text{ } CH_4, 10\% \text{ } O_2$) yields a nominal mathematical turnover time $V/Q = 90.0 \text{ minutes}$.
- **CRITICAL**: This 90-minute figure is purely an idealized macroscopic turnover ratio (plug flow). It is **NOT** an operational mine safety recommendation. Real mine inertisation requires 3 to 5+ volume turnovers due to dead zones, methane desorption, gas stratification, and stopping leakage.

---

## 7. Which Parts Are Published vs. Configurable vs. Theoretical?

- **Real Published Data**: The 14 Lodna samples from Singh et al. (2007).
- **Verified Boundaries**: The Coward Diagram boundaries in `coward/coward_boundaries.csv` are based on USBM Bulletin 503 (Coward & Jones, 1952). If your supervisor specifies an alternate set of boundaries, enter them into `coward/coward_boundaries_template.csv`.
- **Reference Required**: The $C/H$ ratio is marked **REFERENCE REQUIRED** because definitions in the literature differ widely.
- **Theoretical Simulation**: The 27,000 m³ $N_2$ dilution trajectory is an academic model only.

---

## 8. Final BTP Conclusion

Mine-fire gases exhibit complex, non-monotonic relationships with temperature and atmospheric conditions. CO, $H_2$, and fire-gas indices show positive associations with temperature in the analyzed dataset, but peak gas concentrations occur at intermediate temperatures where oxygen supply is adequate. Residual oxygen behavior is governed by oxidation kinetics, ventilation leakage, and dilution. Therefore, **temperature alone is insufficient for diagnosing underground mine fires**. An integrated multi-parameter diagnosis combining $O_2$, $CO$, $CO_2$, $H_2$, $CH_4$, oxygen deficiency, Graham ratio, Jones–Trickett ratio, and Coward diagram position provides the only defensible and reliable assessment.
