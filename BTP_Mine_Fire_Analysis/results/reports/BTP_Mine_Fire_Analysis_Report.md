# BTP PROJECT REPORT
## Fire Gases and Their Interpretation in Underground Coal Mines

**Department of Mining Engineering**  
**Indian Institute of Technology Kharagpur**  

---

## Chapter 1 — Introduction

Underground coal mine fires represent one of the most perilous hazards in the mining industry, threatening miner safety, causing massive sterilization of valuable energy reserves, and emitting hazardous, toxic, and flammable gases. Spontaneous combustion of coal, arising from the exothermic reaction of coal with atmospheric oxygen, is the primary source of underground heating and fires in bord-and-pillar workings and goaf areas.

Accurate detection, diagnostic interpretation, and continuous atmospheric monitoring are imperative for early warning, seal-integrity verification, and safe inertisation decision-making. This Bachelor/Master of Technology project presents a rigorous, reproducible, Python-based analytical framework applied to real, published mine-fire gas data from **Lodna Colliery, Jharia Coalfield** (Singh et al., 2007).

## Chapter 2 — Mine Fire Gases

The principal atmospheric components analyzed during mine fire occurrences include:

- **Oxygen ($O_2$)**: Essential for human respiration (normal 20.93% vol). In mine fires, $O_2$ is consumed by coal oxidation. However, residual $O_2$ measured behind stoppings is governed by seal leakage, barometric breathing, and fresh-air dilution.
- **Carbon Monoxide ($CO$)**: The primary diagnostic indicator of low-temperature coal oxidation and incomplete combustion. Toxic at very low concentrations (>50 ppm). As demonstrated in this study, $CO$ does not increase monotonically with temperature.
- **Carbon Dioxide ($CO_2$)**: Major product of complete oxidation and combustion. It can also originate from carbonate-acid reactions in mine water and coal seam strata emission.
- **Hydrogen ($H_2$)**: Highly flammable gas generated primarily during advanced heating and active flaming (>250–300°C) or water-gas shift reaction ($C + H_2O \rightarrow CO + H_2$).
- **Methane ($CH_4$)**: Natural coal-seam firedamp gas. Highly combustible with an explosive range between ~5.0% and 15.0% in air. Governs atmospheric explosibility on the Coward diagram.
- **Nitrogen ($N_2$)**: Chemically inert carrier gas (79.04% in dry air). Changes in $N_2$ proportion provide the basis for calculating oxygen deficiency and evaluating nitrogen inertisation flushing.

## Chapter 3 — Fire-Gas Indices

To minimize errors caused by pure dilution or changes in ventilation quantity, mining engineers utilize standardized fire-gas ratios. The formulas implemented in this system are:

1. **Oxygen Deficiency ($\Delta O_2$)**:
   $$\Delta O_2 = \left(\frac{20.93}{79.04}\right) N_2 - O_2 \approx 0.2648 N_2 - O_2$$
   *Limitation*: Numerical ratio instability occurs when $\Delta O_2 < 0.3\%$.

2. **Graham's Ratio ($G$)**:
   $$G = 100 \times \frac{CO}{\Delta O_2}$$
   *Indicative Guide*: $\le 0.4$ (Normal/background); $0.4-0.5$ (Check condition); $0.5-1.0$ (Heating indication); $1.0-2.0$ (Serious heating); $2.0-7.0$ (Active fire); $\ge 7.0$ (Blazing fire).

3. **Young's Ratio ($Y$)**:
   $$Y = 100 \times \frac{CO_2}{\Delta O_2}$$
   *Limitations*: Non-combustion sources of $CO_2$ (strata gas, acid water-carbonate reactions) may inflate this ratio.

4. **$CO / CO_2$ Ratio**:
   $$\frac{CO}{CO_2} = 100 \times \frac{CO}{CO_2}$$
   *Limitations*: Readily affected by water dissolution of $CO_2$ and strata gas.

5. **Jones–Trickett Ratio ($JT$)**:
   $$JT = \frac{CO_2 + 0.75 \, CO - 0.25 \, H_2}{\Delta O_2}$$
   *Indicative Fuel Ranges*: $0.4-0.5$ (Methane combustion); $0.5-1.0$ (Coal, oil, belt); $0.9-1.6$ (Timber).

6. **Willett's Ratio ($W$)**:
   $$W = \frac{CO_2}{\text{Excess } N_2 + CO_2 + \text{Combustibles}}$$
   $$\text{Excess } N_2 = N_2 - 3.8 \, O_2$$
   $$\text{Combustibles} = CO + H_2 + CH_4$$

7. **$C/H$ Ratio**:
   *Status*: **REFERENCE REQUIRED**. Definitions in mining literature vary substantially (e.g., Mitchell stoichiometric vs elemental). In strict adherence to academic rigor, no arbitrary formula was fabricated.

## Chapter 4 — Dataset and Methodology

### 4.1 Real Mine Fire Dataset
The project analyzes 14 real mine-fire samples collected behind sealed stoppings at **Lodna Colliery, Jharia Coalfield** (Singh et al., 2007, *Int. J. Coal Geol.*, 69(3), 192–204). The sampling period spans September 1985 to October 1993.

### 4.2 Methodology Flowchart
```
Published Gas Data (Lodna Colliery, N=14)
           │
           ▼
Gas Composition Validation (Sum vs. 100% Tolerance)
           │
           ▼
Oxygen Deficiency Calculation (ΔO2 = 0.2648*N2 - O2)
           │
           ▼
Fire-Gas Indices Computation (Graham, Young, CO/CO2, JT, Willett)
           │
           ▼
Temperature Relationship & Regression Analysis
           │
           ▼
Statistical & Pearson Correlation Matrix Computation
           │
           ▼
Coward Diagram Plotting & Zone Classification (Zones A to E)
           │
           ▼
Theoretical N2 Dilution Modeling (Academic Academic Simulation)
           │
           ▼
Multi-Indicator Synthesis & BTP Conclusion
```

## Chapter 5 — Results

### 5.1 Data Validation Summary

- Total Samples Analyzed: **14**
- Mean Gas Sum: **100.00%** (Range: 99.99% to 100.01%)
- Maximum Absolute Deviation: **0.01%**
- Validation Status: **All 14 samples within acceptable analytical/rounding tolerance (±1.0%)**.


### 5.2 Summary of Extrema

| Observation_Category | Sample_No | Date | Value | Temperature_C |
| --- | --- | --- | --- | --- |
| Highest Temperature | 4 | 20-06-1987 | 80.0000 °C | 80.0 |
| Highest CO | 6 | 02-06-1988 | 0.8130 % | 64.0 |
| Highest CO2 | 4 | 20-06-1987 | 17.1300 % | 80.0 |
| Highest H2 | 5 | 15-12-1987 | 2.3430 % | 72.0 |
| Highest CH4 | 6 | 02-06-1988 | 0.5260 % | 64.0 |
| Lowest O2 | 12 | 16-10-1992 | 0.0000 % | 37.0 |
| Highest O2 Deficiency | 12 | 16-10-1992 | 23.6601 % | 37.0 |
| Highest Graham Ratio | 6 | 02-06-1988 | 4.8112 | 64.0 |
| Highest CO/CO2 Ratio | 6 | 02-06-1988 | 5.7989 % | 64.0 |
| Highest Young Ratio | 9 | 11-06-1990 | 94.7313 | 47.0 |
| Highest Jones-Trickett Ratio | 9 | 11-06-1990 | 0.9473 | 47.0 |
| Highest Willett Ratio | 9 | 11-06-1990 | 0.2008 | 47.0 |



## Chapter 6 — Temperature and Gas Relationships

A central inquiry in mining engineering research is whether temperature alone governs gas concentrations. The calculated statistical results directly resolve the 4 core BTP research questions:


### Does CO increase when temperature increases?

- **Pearson r**: 0.385 (R² = 0.148)

- **Scientific Finding**: Moderate positive correlation (r = 0.385), but the relationship is NON-MONOTONIC. The highest temperature (80°C on 20-06-1987) recorded a low CO of 0.022%, whereas the maximum CO (0.813% on 02-06-1988) occurred at a lower temperature of 64°C. This proves that CO concentration in a sealed mine fire is not dictated by temperature alone; it is strongly governed by oxygen supply, oxidation stage, and dilution.


### Does O2 decrease as temperature increases?

- **Pearson r**: -0.132 (R² = 0.017)

- **Scientific Finding**: Weak/Moderate negative correlation (r = -0.132, slope = -0.0169). Generally, higher temperatures accelerate oxidation kinetics and consume oxygen, leading to lower residual O2. However, residual O2 also depends heavily on seal tightness, atmospheric pressure fluctuations, barometric breathing, and air ingress. For instance, sample 12 recorded 0.00% O2 at 37°C, showing that low oxygen can also persist in an inactive or oxygen-depleted sealed zone.


### Does H2 increase with temperature?

- **Pearson r**: 0.523 (R² = 0.274)

- **Scientific Finding**: Moderate positive correlation (r = 0.523). Hydrogen generation typically requires elevated coal temperatures (> 200-250°C at the coal face) and water-gas reaction. In the field measurements, the peak H2 (2.343% on 15-12-1987) occurred at 72°C. Samples below 55°C generally showed 0.000% H2, confirming that detectable hydrogen is associated with higher thermal activity, though field temperatures measured behind stoppings reflect dissipated air temperature rather than peak internal hotspot temperatures.


### Does Graham ratio increase with temperature?

- **Pearson r**: 0.400 (R² = 0.160)

- **Scientific Finding**: Moderate positive correlation (r = 0.400). Graham ratio generally rises with increasing temperature because elevated thermal oxidation generates more CO relative to oxygen consumed. However, this relationship is non-linear and non-monotonic due to oxygen starvation and ventilation dynamics. Thus, Graham ratio serves as an indicative index of oxidation intensity rather than a direct thermometer.


### Key Principle: Non-Monotonic Behavior
The dataset explicitly demonstrates that **higher temperature does not automatically yield higher CO or Graham ratio**. The highest temperature recorded (80°C on 20-06-1987) exhibited a low CO concentration of 0.022% (Graham ratio = 0.11), whereas the peak CO of 0.813% (Graham ratio = 4.81, indicating active fire) occurred at a lower temperature of 64°C. This non-monotonicity arises because gas emissions are controlled by oxygen availability, seal leakage, coal surface reactivity, and dilution, rather than temperature alone.

## Chapter 7 — Coward Diagram Analysis

### 7.1 Coward Diagram Classification
Using classical explosibility limits from USBM Bulletin 503 (Coward & Jones, 1952), the 14 Lodna samples were classified:


| Sample_No | Date | CH4_percent | O2_percent | Temperature_C | Coward_Zone | Safety_Interpretation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 27-09-1985 | 0.351 | 5.18 | 73.0 | Zone D | Not capable of forming explosive mixtures (Inert / Deficient in both fuel and oxygen) |
| 2 | 14-05-1986 | 0.0 | 1.64 | 55.0 | Zone D | Not capable of forming explosive mixtures (Inert / Deficient in both fuel and oxygen) |
| 3 | 08-10-1986 | 0.0 | 2.13 | 30.0 | Zone D | Not capable of forming explosive mixtures (Inert / Deficient in both fuel and oxygen) |
| 4 | 20-06-1987 | 0.0 | 1.55 | 80.0 | Zone D | Not capable of forming explosive mixtures (Inert / Deficient in both fuel and oxygen) |
| 5 | 15-12-1987 | 0.0 | 4.75 | 72.0 | Zone D | Not capable of forming explosive mixtures (Inert / Deficient in both fuel and oxygen) |
| 6 | 02-06-1988 | 0.526 | 4.22 | 64.0 | Zone D | Not capable of forming explosive mixtures (Inert / Deficient in both fuel and oxygen) |
| 7 | 27-12-1988 | 0.0 | 3.33 | 67.0 | Zone D | Not capable of forming explosive mixtures (Inert / Deficient in both fuel and oxygen) |
| 8 | 22-06-1989 | 0.095 | 3.93 | 63.0 | Zone D | Not capable of forming explosive mixtures (Inert / Deficient in both fuel and oxygen) |
| 9 | 11-06-1990 | 0.0 | 4.88 | 47.0 | Zone D | Not capable of forming explosive mixtures (Inert / Deficient in both fuel and oxygen) |
| 10 | 11-11-1990 | 0.0 | 4.29 | 54.0 | Zone D | Not capable of forming explosive mixtures (Inert / Deficient in both fuel and oxygen) |
| 11 | 07-12-1991 | 0.0 | 3.0 | 31.0 | Zone D | Not capable of forming explosive mixtures (Inert / Deficient in both fuel and oxygen) |
| 12 | 16-10-1992 | 0.0 | 0.0 | 37.0 | Zone D | Not capable of forming explosive mixtures (Inert / Deficient in both fuel and oxygen) |
| 13 | 22-04-1993 | 0.0 | 7.51 | 34.0 | Zone D | Not capable of forming explosive mixtures (Inert / Deficient in both fuel and oxygen) |
| 14 | 18-10-1993 | 0.0 | 8.18 | 33.0 | Zone D | Not capable of forming explosive mixtures (Inert / Deficient in both fuel and oxygen) |


**Key Finding**: Every Lodna mine fire sample resides firmly inside **Zone D (Non-explosive / Cannot form explosive mixtures with air alone)**. This is attributable to the low residual oxygen ($O_2 \le 8.18\% < 12.1\%$ Nose limit) and minimal methane accumulation ($CH_4 \le 0.526\% \ll 5.0\%$ LEL).

### 7.2 Theoretical Nitrogen Dilution Trajectory
In the hypothetical academic scenario ($V = 27,000.0 \text{ m}^3$, $Q = 5.0 \text{ m}^3/\text{s}$):
- Initial sealed atmosphere: $15.0\% \, CH_4$, $10.0\% \, O_2$.
- Dilution path: Pure $N_2$ injection linearly decreases both $CH_4$ and $O_2$ toward the origin $(0, 0)$ without crossing the explosive Zone A.
- Nominal turnover ratio: $V/Q = 90.0 \text{ minutes}$ (1.50 hours).
- **Scientific Warning**: CRITICAL: 90 minutes is purely a nominal mathematical turnover ratio (V/Q). It must NEVER be treated as an operational mine-sealing or inertisation duration. Actual field flushing requires continuous gas chromatography monitoring, pressure balancing, and professional mine rescue assessment.

## Chapter 8 — Discussion

### 8.1 Multi-Indicator Synthesis
Relying on a single fire gas or a single ratio creates severe risks of misdiagnosis:
1. Low $CO$ at 80°C could be misread as an extinguished fire, whereas it was actually caused by oxygen starvation ($O_2 = 1.55\%$).
2. Young's ratio remained elevated (>70) throughout the observation period, reflecting both oxidation products and strata/water interactions.
3. Jones–Trickett values clustered between 0.6 and 1.0, accurately pointing toward coal heating rather than methane combustion.

### 8.2 Scientific Limitations
1. **Sample Size**: The dataset is restricted to 14 published samples; statistical correlations must not be extrapolated uncritically.
2. **Correlation vs. Causation**: Statistical association does not imply direct physical causation.
3. **Heterogeneous Underground Conditions**: Stratification, dead zones, and barometric breathing create spatial gas gradients.
4. **Theoretical Model**: The $N_2$ dilution model assumes ideal plug-flow; real mine inertisation requires exponential volume turnovers.

## Chapter 9 — Conclusions

Based on the empirical analysis of the Lodna Colliery dataset:

1. Mine-fire gases exhibit complex, non-monotonic relationships with temperature. While $CO$, $H_2$, and Graham's ratio exhibit moderate positive correlations with temperature overall, peak gas emissions and fire severity occur at intermediate temperatures where oxygen availability is sufficient.
2. Oxygen concentration generally decreases with temperature, but field concentrations are dominated by seal tightness and barometric leakage.
3. **Temperature alone is fundamentally insufficient for interpreting mine-fire conditions.**
4. All 14 Lodna samples occupied Zone D on the Coward Diagram, proving that the sealed atmosphere was non-explosive.
5. A multi-parameter diagnostic approach combining $O_2$, $CO$, $CO_2$, $H_2$, $CH_4$, oxygen deficiency, Graham's ratio, Jones–Trickett ratio, and Coward diagram trajectory provides the only robust methodology for underground coal mine fire assessment.


## References

1. **Singh, A.K., Singh, R.V.K., Singh, M.P., Kumar, H., Sural, N. (2007).** Mine fire gas indices and their application to Indian underground coal mine fires. *International Journal of Coal Geology*, 69(3), 192–204. DOI: 10.1016/j.coal.2006.04.004.
2. **Coward, H.F., Jones, G.W. (1952).** *Limits of Flammability of Gases and Vapors.* U.S. Bureau of Mines Bulletin 503, 155 pp.
3. **Zabetakis, M.G. (1965).** *Flammability Characteristics of Combustible Gases and Vapors.* U.S. Bureau of Mines Bulletin 627, 121 pp.
4. **Banerjee, S.C. (1985).** *Prevention and Combating Mine Fires.* Oxford & IBH Publishing Co., New Delhi, 280 pp.
5. **Ray, S.K., Khan, A.M., Singh, R.V.K., Singh, A.K. (2004).** Mine fire gas analysis for assessing spontaneous heating. *Journal of Mines, Metals & Fuels*, 52(9), 235–241.
