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
        "patients": load_csv(RELATIONAL_DIR / "patients.csv"),
        "encounters": load_csv(RELATIONAL_DIR / "encounters.csv"),
        "symptoms": load_csv(RELATIONAL_DIR / "symptoms.csv"),
        "risk_history": load_csv(RELATIONAL_DIR / "risk_history.csv"),
        "resting_tests": load_csv(RELATIONAL_DIR / "resting_tests.csv"),
        "exercise_ecg_tests": load_csv(RELATIONAL_DIR / "exercise_ecg_tests.csv"),
        "diagnoses": load_csv(RELATIONAL_DIR / "diagnoses.csv"),
        "missing_report": load_csv(REPORT_DIR / "missing_values_report.csv"),
        "duplicate_report": load_csv(REPORT_DIR / "duplicate_report.csv"),
        "outlier_report": load_csv(REPORT_DIR / "outlier_report.csv"),
        "default_report": load_csv(REPORT_DIR / "default_value_check_report.csv"),
        "shape_report": load_csv(REPORT_DIR / "raw_table_shape_report.csv"),
        "target_report": load_csv(REPORT_DIR / "target_distribution_report.csv"),
        "metrics": load_csv(REPORT_DIR / "model_metrics.csv"),
        "python_cp_target": load_csv(REPORT_DIR / "python_crosstab_cp_target.csv"),
        "python_age_group_summary": load_csv(REPORT_DIR / "python_age_group_summary.csv"),
        "python_correlation_target": load_csv(REPORT_DIR / "python_correlation_target.csv"),
        "selected_correlation_features": load_csv(REPORT_DIR / "selected_correlation_features.csv"),
    }

@st.cache_resource
def load_model():
    best_path = MODEL_DIR / "best_model.joblib"
    if not best_path.exists():
        raise FileNotFoundError("Run python src\\04_machine_learning.py to create models\\best_model.joblib")
    return joblib.load(best_path)

def get_figure_path(name: str) -> Path:
    return FIGURE_DIR / name

def build_sql_result_frames(data: dict) -> dict:
    encounters = data["encounters"]
    symptoms = data["symptoms"]
    diagnoses = data["diagnoses"]
    resting_tests = data["resting_tests"]
    exercise = data["exercise_ecg_tests"]

    source_counts = encounters.groupby("source_database").size().reset_index(name="total_records")
    target_dist = diagnoses.groupby("target_binary").size().reset_index(name="total_records")
    target_dist["percentage"] = (target_dist["total_records"] / target_dist["total_records"].sum() * 100).round(2)

    cp_target = (
        symptoms.merge(diagnoses[["encounter_id", "target_binary"]], on="encounter_id")
        .groupby(["cp", "target_binary"]).size().reset_index(name="total_records")
        .sort_values(["cp", "target_binary"])
    )

    avg_metrics = (
        diagnoses[["encounter_id", "target_binary"]]
        .merge(resting_tests[["encounter_id", "trestbps", "chol"]], on="encounter_id")
        .merge(exercise[["encounter_id", "thalach", "oldpeak"]], on="encounter_id")
        .groupby("target_binary")[["trestbps", "chol", "thalach", "oldpeak"]]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={
            "trestbps": "avg_resting_bp",
            "chol": "avg_cholesterol",
            "thalach": "avg_max_heart_rate",
            "oldpeak": "avg_oldpeak",
        })
    )

    oldpeak_rank = (
        exercise.merge(diagnoses[["encounter_id", "target_binary"]], on="encounter_id")
        .dropna(subset=["oldpeak"])
        .sort_values(["target_binary", "oldpeak"], ascending=[True, False])
    )
    oldpeak_rank["oldpeak_rank"] = oldpeak_rank.groupby("target_binary")["oldpeak"].rank(method="min", ascending=False)

    source_target = (
        encounters[["encounter_id", "source_database"]]
        .merge(diagnoses[["encounter_id", "target_binary"]], on="encounter_id")
        .groupby("source_database")
        .agg(
            total_records=("target_binary", "size"),
            positive_records=("target_binary", "sum"),
        )
        .reset_index()
    )
    overall_positive_rate = diagnoses["target_binary"].mean()
    source_target["source_positive_rate"] = (source_target["positive_records"] / source_target["total_records"] * 100).round(2)
    source_target["overall_positive_rate"] = round(overall_positive_rate * 100, 2)
    source_target["rate_gap"] = (source_target["source_positive_rate"] - source_target["overall_positive_rate"]).round(2)
    source_target = source_target.sort_values("rate_gap", ascending=False)

    return {
        "source_counts": source_counts,
        "target_dist": target_dist,
        "cp_target": cp_target,
        "avg_metrics": avg_metrics,
        "oldpeak_rank": oldpeak_rank[["target_binary", "encounter_id", "oldpeak", "oldpeak_rank"]].head(20),
        "source_target_rate_vs_overall": source_target,
    }
