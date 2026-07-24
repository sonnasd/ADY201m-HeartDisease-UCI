from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RELATIONAL_DIR = PROCESSED_DIR / "relational"
REPORT_DIR = BASE_DIR / "reports" / "outputs"
FIGURE_DIR = BASE_DIR / "reports" / "figures"
MODEL_DIR = BASE_DIR / "models"

@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RELATIONAL_DIR = PROCESSED_DIR / "relational"
REPORT_DIR = BASE_DIR / "reports" / "outputs"
FIGURE_DIR = BASE_DIR / "reports" / "figures"
MODEL_DIR = BASE_DIR / "models"

@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

@st.cache_data
def load_all_data() -> dict:
    return {
        "ml": load_csv(PROCESSED_DIR / "ml_ready_heart_disease.csv"),
        "flat": load_csv(PROCESSED_DIR / "uci_heart_disease_parsed_flat.csv"),
        "missing_report": load_csv(REPORT_DIR / "missing_values_report.csv"),
        "duplicate_report": load_csv(REPORT_DIR / "duplicate_report.csv"),
        "outlier_report": load_csv(REPORT_DIR / "outlier_report.csv"),
        "default_report": load_csv(REPORT_DIR / "default_value_check_report.csv"),
        "target_report": load_csv(REPORT_DIR / "target_distribution_report.csv"),
        
        "source_counts": load_csv(REPORT_DIR / "analysis_source_counts.csv"),
        "target_dist": load_csv(REPORT_DIR / "analysis_target_dist.csv"),
        "cp_target": load_csv(REPORT_DIR / "analysis_cp_target.csv"),
        "avg_metrics": load_csv(REPORT_DIR / "analysis_avg_metrics.csv"),
        "oldpeak_rank": load_csv(REPORT_DIR / "analysis_oldpeak_rank.csv"),
        "source_target_rate_vs_overall": load_csv(REPORT_DIR / "analysis_source_vs_overall.csv"),
        "chol_outliers": load_csv(REPORT_DIR / "analysis_chol_outliers.csv"),

        "metrics": _format_metrics(load_csv(REPORT_DIR / "model_metrics.csv")),
        "python_cp_target": load_csv(REPORT_DIR / "python_crosstab_cp_target.csv"),
        "python_age_group_summary": load_csv(REPORT_DIR / "python_age_group_summary.csv"),
        "python_correlation_target": load_csv(REPORT_DIR / "python_correlation_target.csv"),
        "selected_correlation_features": load_csv(REPORT_DIR / "selected_correlation_features.csv"),
    }

def _format_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Convert metric columns from decimal (0.83) to percentage string (83.50%) for display."""
    pct_cols = [c for c in ["accuracy", "precision", "recall", "f1_score"] if c in df.columns]
    df = df.copy()
    for col in pct_cols:
        df[col] = df[col].apply(lambda v: f"{v * 100:.2f}%" if pd.notna(v) else v)
    return df


@st.cache_resource
def load_model():
    best_path = MODEL_DIR / "best_model.joblib"
    if not best_path.exists():
        raise FileNotFoundError("Run python src\\05_machine_learning.py to create models\\best_model.joblib")
    return joblib.load(best_path)

def get_figure_path(name: str) -> Path:
    return FIGURE_DIR / name
