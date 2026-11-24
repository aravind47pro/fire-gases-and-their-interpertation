"""
Excel Exporter Module for BTP Mine Fire Gas Analysis
Generates the comprehensive 10-sheet Excel workbook 'BTP_Final_Gas_Analysis.xlsx'.
Includes formatted tables, headers, and reference documentation.
"""

import os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from typing import Dict, Any, Optional

def export_to_excel(filepath: str,
                    raw_df: pd.DataFrame,
                    calc_df: pd.DataFrame,
                    temp_df: pd.DataFrame,
                    corr_df: pd.DataFrame,
                    coward_class_df: pd.DataFrame,
                    summary_df: pd.DataFrame,
                    extremes_df: pd.DataFrame,
                    qa_dict: Dict[str, Any]) -> None:
    """
    Export all BTP calculations, indices, models, and reference documentation
    into an elegant, formatted 10-sheet Excel workbook.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Sheet 1: Raw Data
        raw_df.to_excel(writer, sheet_name='Raw Data', index=False)

        # Sheet 2: Gas Calculations
        calc_cols = ["Sample_No", "Date", "Gas_Sum_percent", "Diff_from_100_percent",
                     "Validation_Status", "O2_Deficiency_percent", "O2_Deficiency_Flag"]
        calc_df[calc_cols].to_excel(writer, sheet_name='Gas Calculations', index=False)

        # Sheet 3: Fire Indices
        indices_cols = ["Sample_No", "Date", "Temperature_C", "O2_Deficiency_percent",
                        "Graham_Ratio", "Graham_Flag", "Graham_Interpretation",
                        "Young_Ratio", "Young_Flag", "CO_CO2_Ratio", "CO_CO2_Flag",
                        "Jones_Trickett_Ratio", "Jones_Trickett_Flag", "Jones_Trickett_Fuel",
                        "Willett_Ratio", "Willett_Flag", "CH_Ratio_Note"]
        calc_df[indices_cols].to_excel(writer, sheet_name='Fire Indices', index=False)

        # Sheet 4: Temperature Analysis
        temp_df.to_excel(writer, sheet_name='Temperature Analysis', index=False)

        # Sheet 5: Correlations
        corr_df.to_excel(writer, sheet_name='Correlations')

        # Sheet 6: Coward Data
        coward_data = calc_df[["Sample_No", "Date", "CH4_percent", "O2_percent", "Temperature_C"]].copy()
        coward_data.to_excel(writer, sheet_name='Coward Data', index=False)

        # Sheet 7: Coward Zone Classification
        coward_class_df.to_excel(writer, sheet_name='Coward Zone Classification', index=False)

        # Sheet 8: Summary
        # Combine extremes and summary stats
        extremes_df.to_excel(writer, sheet_name='Summary', index=False, startrow=0)
        summary_df.to_excel(writer, sheet_name='Summary', index=False, startrow=len(extremes_df) + 3)

        # Sheet 9: Formula Guide
        formula_data = pd.DataFrame([
            {"Parameter": "Oxygen Deficiency (ΔO2)", "Formula": "ΔO2 = (20.93 / 79.04) * N2 - O2 ≈ 0.265 * N2 - O2",
             "Indicative Application / Rule": "Measures O2 consumed by coal oxidation.", "Limitations": "Unreliable when ΔO2 < 0.3%."},
            {"Parameter": "Graham Ratio", "Formula": "Graham = 100 * CO / ΔO2",
             "Indicative Application / Rule": "<0.4: Normal; 0.5: Check; 1.0: Heating; 2.0: Serious heating; >=3.0: Active fire.",
             "Limitations": "Becomes unstable if ΔO2 < 0.3%. Indicative only."},
            {"Parameter": "Young Ratio", "Formula": "Young = 100 * CO2 / ΔO2",
             "Indicative Application / Rule": "Evaluates combustion maturity.",
             "Limitations": "CO2 can arise from acid-carbonate reactions, strata gas, or water dissolution."},
            {"Parameter": "CO / CO2 Ratio", "Formula": "CO/CO2 = 100 * CO / CO2",
             "Indicative Application / Rule": "Combustion efficiency / incomplete combustion indicator.",
             "Limitations": "CO2 dissolution in wet workings artificially inflates ratio."},
            {"Parameter": "Jones-Trickett Ratio", "Formula": "JT = (CO2 + 0.75 * CO - 0.25 * H2) / ΔO2",
             "Indicative Application / Rule": "0.4-0.5: Methane; 0.5-1.0: Coal/oil/belt; 0.9-1.6: Timber.",
             "Limitations": "Ambiguous when multiple fuel types or water-gas shift are present."},
            {"Parameter": "Willett Ratio", "Formula": "CO2 / (Excess N2 + CO2 + Combustibles); Excess N2 = N2 - 3.8 * O2",
             "Indicative Application / Rule": "Trend indicator for sealed fire status.",
             "Limitations": "Sensitive to dilution and combustible gas definition (CO+H2+CH4)."},
            {"Parameter": "C / H Ratio", "Formula": "REFERENCE REQUIRED (Definition varies across mining literature)",
             "Indicative Application / Rule": "Combustion stoichiometry indicator.",
             "Limitations": "Not standardized in Singh et al. (2007); requires supervisor definition."}
        ])
        formula_data.to_excel(writer, sheet_name='Formula Guide', index=False)

        # Sheet 10: Sources & References
        references_data = pd.DataFrame([
            {"Reference_ID": "Singh et al. (2007)",
             "Full_Citation": "Singh, A.K., Singh, R.V.K., Singh, M.P., Kumar, H., Sural, N. (2007). Mine fire gas indices and their application to Indian underground coal mine fires. International Journal of Coal Geology, 69(3), 192-204. DOI: 10.1016/j.coal.2006.04.004.",
             "Application": "Source of 14 Lodna Colliery real mine-fire samples (1985-1993)."},
            {"Reference_ID": "Coward & Jones (1952)",
             "Full_Citation": "Coward, H.F., Jones, G.W. (1952). Limits of Flammability of Gases and Vapors. U.S. Bureau of Mines Bulletin 503, 155 pp.",
             "Application": "Foundational Coward diagram explosibility limits and Nose point coordinates."},
            {"Reference_ID": "Zabetakis (1965)",
             "Full_Citation": "Zabetakis, M.G. (1965). Flammability Characteristics of Combustible Gases and Vapors. U.S. Bureau of Mines Bulletin 627, 121 pp.",
             "Application": "Flammability envelopes and nitrogen inertisation dilution limits."},
            {"Reference_ID": "Banerjee (1985)",
             "Full_Citation": "Banerjee, S.C. (1985). Prevention and Combating Mine Fires. Oxford & IBH Publishing Co., New Delhi, 280 pp.",
             "Application": "Indian coal mining fire ratios, Graham index benchmarks, and gas interpretation."},
            {"Reference_ID": "Ray et al. (2004)",
             "Full_Citation": "Ray, S.K., Khan, A.M., Singh, R.V.K., Singh, A.K. (2004). Mine fire gas analysis for assessing spontaneous heating. Journal of Mines, Metals & Fuels, 52(9), 235-241.",
             "Application": "Spontaneous heating index validation in Indian underground coal mines."}
        ])
        references_data.to_excel(writer, sheet_name='Sources & References', index=False)

    # Format workbook headers and column widths
    wb = openpyxl.load_workbook(filepath)
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    thin_border = Border(left=Side(style='thin', color='D9D9D9'),
                         right=Side(style='thin', color='D9D9D9'),
                         top=Side(style='thin', color='D9D9D9'),
                         bottom=Side(style='thin', color='D9D9D9'))

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        ws.views.sheetView[0].showGridLines = True

        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)

            # Style header row
            first_cell = col[0]
            if first_cell.value is not None:
                first_cell.fill = header_fill
                first_cell.font = header_font
                first_cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            for cell in col:
                cell.border = thin_border
                val_str = str(cell.value or '')
                max_len = max(max_len, len(val_str))

            ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 50)

    wb.save(filepath)
