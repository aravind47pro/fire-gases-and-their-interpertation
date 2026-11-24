"""
Main Pipeline for BTP Mine Fire Gas Analysis
Coordinates data ingestion, validation, fire-gas indices, temperature regressions,
Coward diagram generation, theoretical dilution modeling, and automated report generation.
"""

import os
import sys
import pandas as pd
from typing import Optional

# Ensure package root is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data_loader import (
    get_default_paths, load_lodna_data,
    load_normal_air_reference, load_coward_boundaries
)
from src.validation import validate_gas_composition, get_validation_summary
from src.gas_indices import calculate_all_indices
from src.temperature_analysis import (
    analyze_all_temperature_relationships, answer_research_questions
)
from src.correlation_analysis import (
    compute_correlation_matrix, compute_summary_statistics,
    generate_automatic_extremes_table
)
from src.coward_diagram import build_coward_classification_table
from src.dilution_model import simulate_n2_dilution, compute_nominal_turnover
from src.plotting import generate_all_btp_figures
from src.excel_exporter import export_to_excel
from src.report_generator import build_markdown_report, build_docx_report


def run_complete_btp_pipeline(base_dir: Optional[str] = None, verbose: bool = True) -> dict:
    """Run the entire analysis pipeline from start to finish."""
    paths = get_default_paths(base_dir)

    if verbose:
        print("=" * 80)
        print("  BTP PROJECT: FIRE GASES & THEIR INTERPRETATION IN UNDERGROUND COAL MINES")
        print("  Department of Mining Engineering, IIT Kharagpur")
        print("=" * 80)
        print(f"[*] Base Directory: {paths['base_dir']}")

    # 1. Load Data
    if verbose:
        print("\n[Step 1/8] Ingesting published mine-fire dataset...")
    df_raw = load_lodna_data(paths["lodna_csv"])
    df_air = load_normal_air_reference(paths["normal_air_csv"])
    df_bounds, is_verified, ref_note = load_coward_boundaries(paths["coward_csv"])
    if verbose:
        print(f"  -> Loaded {len(df_raw)} samples from Lodna Colliery (Singh et al., 2007).")
        print(f"  -> Coward Boundary Status: {'Verified' if is_verified else 'Pending'} ({ref_note}).")

    # 2. Validate Data
    if verbose:
        print("\n[Step 2/8] Validating gas composition sums against 100% tolerance...")
    df_validated = validate_gas_composition(df_raw, tolerance_percent=1.0)
    val_summary = get_validation_summary(df_validated)
    if verbose:
        print(f"  -> Mean Gas Sum: {val_summary['Mean_Gas_Sum']:.2f}% (Std: {val_summary['Std_Gas_Sum']:.2f}%).")
        print(f"  -> Max Deviation from 100%: {val_summary['Max_Abs_Difference']:.2f}%.")
        print(f"  -> All samples valid: {val_summary['All_Valid']}.")

    # 3. Calculate Fire-Gas Indices
    if verbose:
        print("\n[Step 3/8] Computing oxygen deficiency and standard mining fire-gas indices...")
    df_calculated = calculate_all_indices(df_validated)

    # 4. Temperature Analysis and Research Questions
    if verbose:
        print("\n[Step 4/8] Investigating temperature relationships & answering research questions...")
    df_temp_analysis = analyze_all_temperature_relationships(df_calculated)
    qa_answers = answer_research_questions(df_calculated, df_temp_analysis)

    # 5. Correlations & Summary Statistics
    if verbose:
        print("\n[Step 5/8] Computing Pearson correlation matrix and descriptive statistics...")
    corr_matrix, _ = compute_correlation_matrix(df_calculated)
    df_summary_stats = compute_summary_statistics(df_calculated)
    df_extremes = generate_automatic_extremes_table(df_calculated)

    # 6. Coward Diagram Classification & Theoretical Dilution
    if verbose:
        print("\n[Step 6/8] Performing Coward explosibility zone mapping & N2 dilution simulation...")
    df_coward_class = build_coward_classification_table(df_calculated, is_verified=is_verified)
    df_dilution = simulate_n2_dilution(initial_ch4=15.0, initial_o2=10.0, f_steps=25)
    turnover_results = compute_nominal_turnover(volume_m3=27000.0, flow_rate_m3_s=5.0)

    # 7. Generate Figures
    if verbose:
        print("\n[Step 7/8] Generating 15 publication-quality figures (300 DPI)...")
    figures_map = generate_all_btp_figures(
        df_calculated, paths["figures_dir"],
        dilution_df=df_dilution, is_verified=is_verified,
        ref_note=ref_note, dpi=300
    )
    if verbose:
        print(f"  -> Successfully saved 15 figures to: {paths['figures_dir']}")

    # 8. Export Tables, Excel, and Reports
    if verbose:
        print("\n[Step 8/8] Exporting CSV tables, 10-sheet Excel workbook, and reports...")

    os.makedirs(paths["tables_dir"], exist_ok=True)
    os.makedirs(paths["reports_dir"], exist_ok=True)

    # Export CSVs
    p_indices_csv = os.path.join(paths["tables_dir"], "calculated_gas_indices.csv")
    p_corr_csv = os.path.join(paths["tables_dir"], "correlation_matrix.csv")
    p_coward_coords_csv = os.path.join(paths["tables_dir"], "coward_sample_coordinates.csv")
    p_coward_class_csv = os.path.join(paths["tables_dir"], "coward_zone_classification.csv")
    p_summary_csv = os.path.join(paths["tables_dir"], "summary_statistics.csv")
    p_extremes_csv = os.path.join(paths["tables_dir"], "summary_extremes.csv")

    df_calculated.to_csv(p_indices_csv, index=False)
    corr_matrix.to_csv(p_corr_csv)
    df_calculated[["Sample_No", "Date", "CH4_percent", "O2_percent", "Temperature_C"]].to_csv(p_coward_coords_csv, index=False)
    df_coward_class.to_csv(p_coward_class_csv, index=False)
    df_summary_stats.to_csv(p_summary_csv, index=False)
    df_extremes.to_csv(p_extremes_csv, index=False)

    # Export Excel
    excel_path = os.path.join(paths["results_dir"], "BTP_Final_Gas_Analysis.xlsx")
    export_to_excel(
        excel_path, df_raw, df_calculated, df_temp_analysis,
        corr_matrix, df_coward_class, df_summary_stats, df_extremes, qa_answers
    )

    # Export Reports
    md_report_path = os.path.join(paths["reports_dir"], "BTP_Mine_Fire_Analysis_Report.md")
    docx_report_path = os.path.join(paths["reports_dir"], "BTP_Mine_Fire_Analysis_Report.docx")

    build_markdown_report(
        md_report_path, df_raw, df_calculated, df_temp_analysis,
        df_summary_stats, df_extremes, qa_answers, df_coward_class,
        turnover_results, val_summary
    )
    build_docx_report(
        docx_report_path, df_raw, df_calculated, df_temp_analysis,
        df_summary_stats, df_extremes, qa_answers, df_coward_class,
        turnover_results, val_summary
    )

    if verbose:
        print(f"  -> Excel Workbook: {excel_path}")
        print(f"  -> Markdown Report: {md_report_path}")
        print(f"  -> Word Document: {docx_report_path}")
        print("\n" + "=" * 80)
        print("  ANALYSIS PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 80)

    return {
        "calculated_df": df_calculated,
        "validation_summary": val_summary,
        "qa_answers": qa_answers,
        "extremes_df": df_extremes,
        "coward_classification": df_coward_class,
        "turnover_results": turnover_results,
        "figures": figures_map,
        "excel_path": excel_path,
        "report_md": md_report_path,
        "report_docx": docx_report_path
    }


if __name__ == "__main__":
    run_complete_btp_pipeline()
