from pathlib import Path
import sys

import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RELATIONAL_DIR = PROCESSED_DIR / "relational"
REPORT_DIR = BASE_DIR / "reports" / "outputs"
FIGURE_DIR = BASE_DIR / "reports" / "figures"
MODEL_DIR = BASE_DIR / "models"
SQL_DIR = BASE_DIR / "sql"
DOCS_DIR = BASE_DIR / "docs"
DASHBOARD_DIR = BASE_DIR / "dashboard"
RELATIONAL_TABLES = ["patients", "encounters", "symptoms", "risk_history", "resting_tests", "exercise_ecg_tests", "diagnoses"]
ENGINEERED_COLUMNS = {
    "age_group",
    "cholesterol_category",
    "st_abnormal_flag",
    "chol_missing_flag",
    "trestbps_missing_flag",
    "thalach_missing_flag",
    "oldpeak_missing_flag",
}
EXPECTED_ROWS = 920
EXPECTED_TARGET_COUNTS = {0: 411, 1: 509}
EXPECTED_CORR_THRESHOLD = 0.10
BATCH_RESULT_COLUMNS = {
    "prediction_target_binary",
    "probability_target_1",
    "risk_label",
    "row_status",
    "error_message",
}


MOJIBAKE_PATTERNS = [
    "\u00c3",
    "\u00c4",
    "\u00c6",
    "\u00e1\u00ba",
    "\u00e1\u00bb",
    "D\u00e1",
    "M\u00c3",
    "Kh\u00c3",
    "T\u00c3",
]


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"Missing required file: {path}")


def assert_no_mojibake(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    found = [pattern for pattern in MOJIBAKE_PATTERNS if pattern in text]
    if found:
        raise AssertionError(f"Detected mojibake in {path}: {found}")


def iter_text_files() -> list[Path]:
    roots = [BASE_DIR, DOCS_DIR, SQL_DIR, DASHBOARD_DIR, BASE_DIR / "src"]
    files = [BASE_DIR / "README.md", BASE_DIR / "requirements.txt", BASE_DIR / ".gitignore"]
    for root in roots:
        if root.exists():
            for pattern in ["*.py", "*.md", "*.sql", "*.txt", "*.example"]:
                files.extend(root.glob(pattern))
    return sorted(set(path for path in files if path.exists() and ".venv" not in path.parts))


def main() -> None:
    required_files = [
        PROCESSED_DIR / "uci_heart_disease_parsed_flat.csv",
        PROCESSED_DIR / "ml_ready_heart_disease.csv",
        REPORT_DIR / "missing_values_report.csv",
        REPORT_DIR / "duplicate_report.csv",
        REPORT_DIR / "outlier_report.csv",
        REPORT_DIR / "default_value_check_report.csv",
        REPORT_DIR / "target_distribution_report.csv",
        REPORT_DIR / "model_metrics.csv",
        REPORT_DIR / "classification_report.txt",
        REPORT_DIR / "python_crosstab_cp_target.csv",
        REPORT_DIR / "python_age_group_summary.csv",
        REPORT_DIR / "python_correlation_target.csv",
        REPORT_DIR / "selected_correlation_features.csv",
        SQL_DIR / "Dataset.sql",
        SQL_DIR / "01_create_database.sql",
        SQL_DIR / "02_create_tables.sql",
        SQL_DIR / "03_load_raw_data.sql",
        SQL_DIR / "04_split_relational_data.sql",
        SQL_DIR / "05_data_quality_reports.sql",
        SQL_DIR / "06_analysis_queries.sql",
        SQL_DIR / "07_create_ml_view.sql",
        BASE_DIR / "requirements.txt",
        BASE_DIR / ".gitignore",
    ]
    for path in required_files:
        assert_exists(path)
        if path.suffix == ".sql" and path.stat().st_size == 0:
            raise AssertionError(f"SQL file is empty: {path}")

    flat_df = pd.read_csv(PROCESSED_DIR / "uci_heart_disease_parsed_flat.csv")
    ml_df = pd.read_csv(PROCESSED_DIR / "ml_ready_heart_disease.csv")
    metrics_df = pd.read_csv(REPORT_DIR / "model_metrics.csv")
    selected_df = pd.read_csv(REPORT_DIR / "selected_correlation_features.csv")

    assert len(flat_df) == EXPECTED_ROWS, f"Expected {EXPECTED_ROWS} parsed rows, got {len(flat_df)}"
    assert len(ml_df) == EXPECTED_ROWS, f"Expected {EXPECTED_ROWS} ML-ready rows, got {len(ml_df)}"

    counts = {int(k): int(v) for k, v in ml_df["target_binary"].value_counts().to_dict().items()}
    assert counts == EXPECTED_TARGET_COUNTS, counts

    missing_cols = ENGINEERED_COLUMNS - set(ml_df.columns)
    assert not missing_cols, f"Missing engineered columns: {sorted(missing_cols)}"

    assert set(metrics_df["model_name"]) == {"Logistic Regression", "Decision Tree", "Random Forest"}, metrics_df
    assert set(metrics_df["feature_set"]) == {"full_features", "eda_filtered_features"}, metrics_df
    assert {"feature_set", "accuracy", "precision", "recall", "f1_score"}.issubset(metrics_df.columns), metrics_df.columns.tolist()

    assert {"feature", "correlation_with_target"}.issubset(selected_df.columns), selected_df.columns.tolist()
    assert not selected_df.empty, "selected_correlation_features.csv is empty"
    assert "num" not in selected_df["feature"].tolist(), selected_df
    assert "target_binary" not in selected_df["feature"].tolist(), selected_df
    min_selected_corr = selected_df["correlation_with_target"].abs().min()
    assert min_selected_corr >= EXPECTED_CORR_THRESHOLD, selected_df

    for name in [
        "target_distribution.png",
        "patient_count_by_source.png",
        "age_distribution.png",
        "cp_target.png",
        "chol_by_target.png",
        "oldpeak_by_target.png",
        "age_thalach_scatter.png",
        "age_group_target_rate.png",
        "correlation_heatmap.png",
        "selected_correlation_heatmap.png",
        "missing_value_heatmap.png",
        "outliers_boxplot.png",
        "model_comparison_f1.png",
        "confusion_matrix.png",
    ]:
        assert_exists(FIGURE_DIR / name)

    assert_exists(MODEL_DIR / "best_model.joblib")

    from dashboard.prediction_batch import predict_patient_file

    model = joblib.load(MODEL_DIR / "best_model.joblib")
    sample_patients = pd.DataFrame([
        {
            "patient_id": "P001",
            "name": "Nguyen Van A",
            "age": 55,
            "sex": 1,
            "cp": 2,
            "trestbps": 130,
            "chol": 240,
            "fbs": 0,
            "restecg": 0,
            "thalach": 150,
            "exang": 0,
            "oldpeak": 1.0,
            "slope": 2,
            "ca": 0,
            "thal": 3,
        },
        {
            "patient_id": "P002",
            "name": "Tran Thi B",
            "age": 61,
            "sex": 0,
            "cp": 4,
            "trestbps": 145,
            "chol": 260,
            "fbs": 1,
            "restecg": 1,
            "thalach": None,
            "exang": 1,
            "oldpeak": 2.2,
            "slope": 2,
            "ca": 1,
            "thal": 7,
        },
    ])
    batch_result = predict_patient_file(model, sample_patients)
    assert BATCH_RESULT_COLUMNS.issubset(batch_result.columns), batch_result.columns.tolist()
    assert set(batch_result["row_status"]) == {"predicted", "predicted_with_missing"}, batch_result
    assert batch_result["error_message"].fillna("").eq("").all(), batch_result
    assert batch_result["prediction_target_binary"].notna().all(), batch_result

    for path in iter_text_files():
        assert_no_mojibake(path)

    for removed_name in ["notebooks", ".venv"]:
        if (BASE_DIR / removed_name).exists():
            raise AssertionError(f"Removed folder still exists: {BASE_DIR / removed_name}")

    print("Validation passed.")


if __name__ == "__main__":
    main()
