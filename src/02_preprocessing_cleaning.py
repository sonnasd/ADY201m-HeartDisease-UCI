from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RELATIONAL_DIR = PROCESSED_DIR / "relational"
REPORT_DIR = BASE_DIR / "reports" / "outputs"


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def split_relational_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    symptoms = df[["encounter_id", "cp"]].copy()
    symptoms.insert(0, "symptom_id", [f"S{i:05d}" for i in range(1, len(symptoms) + 1)])

    risk_history = df[["encounter_id", "fbs"]].copy()
    risk_history.insert(0, "risk_id", [f"R{i:05d}" for i in range(1, len(risk_history) + 1)])

    resting_tests = df[["encounter_id", "trestbps", "chol", "restecg"]].copy()
    resting_tests.insert(0, "resting_test_id", [f"RT{i:05d}" for i in range(1, len(resting_tests) + 1)])

    exercise_ecg_tests = df[["encounter_id", "thalach", "exang", "oldpeak", "slope"]].copy()
    exercise_ecg_tests.insert(0, "exercise_test_id", [f"EX{i:05d}" for i in range(1, len(exercise_ecg_tests) + 1)])

    diagnoses = df[["encounter_id", "ca", "thal", "num", "target_binary"]].copy()
    diagnoses.insert(0, "diagnosis_id", [f"D{i:05d}" for i in range(1, len(diagnoses) + 1)])

    return {
        "patients": df[["patient_id", "age", "sex", "source_database", "source_row_number"]].copy(),
        "encounters": df[["encounter_id", "patient_id", "source_database", "source_row_number"]].copy(),
        "symptoms": symptoms,
        "risk_history": risk_history,
        "resting_tests": resting_tests,
        "exercise_ecg_tests": exercise_ecg_tests,
        "diagnoses": diagnoses,
    }


def save_relational_tables(tables: dict[str, pd.DataFrame]) -> None:
    for table_name, df in tables.items():
        output_path = RELATIONAL_DIR / f"{table_name}.csv"
        write_csv(df, output_path)
        print(f"Saved {table_name}: {output_path} | shape={df.shape}")


def add_ml_features(ml_df: pd.DataFrame) -> pd.DataFrame:
    ml_df = ml_df.copy()

    def get_age_group(age):
        if pd.isna(age):
            return np.nan
        if age < 40:
            return "<40"
        if age < 50:
            return "40-49"
        if age < 60:
            return "50-59"
        return "60+"

    def get_chol_category(chol):
        if pd.isna(chol) or chol == 0:
            return "low_or_unknown"
        if chol < 200:
            return "normal"
        if chol < 240:
            return "borderline_high"
        return "high"

    ml_df["age_group"] = ml_df["age"].apply(get_age_group)
    ml_df["cholesterol_category"] = ml_df["chol"].apply(get_chol_category)
    ml_df["st_abnormal_flag"] = np.where((ml_df["oldpeak"] > 1.0) | (ml_df["slope"].isin([2, 3])), 1, 0)
    ml_df.loc[ml_df["oldpeak"].isna() & ml_df["slope"].isna(), "st_abnormal_flag"] = np.nan

    for col in ["chol", "trestbps", "thalach", "oldpeak"]:
        ml_df[f"{col}_missing_flag"] = np.where(ml_df[col].isna(), 1, 0)
    return ml_df


def build_ml_ready_dataset(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    ml_df = (
        tables["encounters"]
        .merge(tables["patients"], on=["patient_id", "source_database", "source_row_number"], how="left")
        .merge(tables["symptoms"], on="encounter_id", how="left")
        .merge(tables["risk_history"], on="encounter_id", how="left")
        .merge(tables["resting_tests"], on="encounter_id", how="left")
        .merge(tables["exercise_ecg_tests"], on="encounter_id", how="left")
        .merge(tables["diagnoses"], on="encounter_id", how="left")
    )
    return add_ml_features(ml_df)


def create_missing_values_report(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for table_name, df in tables.items():
        for col in df.columns:
            missing_count = int(df[col].isna().sum())
            rows.append({
                "table_name": table_name,
                "column_name": col,
                "missing_count": missing_count,
                "missing_pct": round(missing_count / len(df) * 100, 2) if len(df) else 0,
            })
    report = pd.DataFrame(rows)
    write_csv(report, REPORT_DIR / "missing_values_report.csv")
    return report


def create_duplicate_report(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for table_name, df in tables.items():
        id_cols = [c for c in df.columns if c.endswith("_id") or c in {"patient_id", "encounter_id"}]
        data_cols = [c for c in df.columns if c not in id_cols]
        rows.append({
            "table_name": table_name,
            "full_duplicate_rows": int(df.duplicated().sum()),
            "duplicate_rows_excluding_id": int(df.duplicated(subset=data_cols).sum()) if data_cols else 0,
        })
    report = pd.DataFrame(rows)
    write_csv(report, REPORT_DIR / "duplicate_report.csv")
    return report


def create_outlier_report(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col, (low, high) in {
        "trestbps": (80, 220),
        "chol": (80, 600),
        "thalach": (50, 230),
        "oldpeak": (0, 10),
    }.items():
        col_data = pd.to_numeric(df[col], errors="coerce").dropna()
        if col_data.empty:
            continue
        q1 = col_data.quantile(0.25)
        q3 = col_data.quantile(0.75)
        iqr = q3 - q1
        iqr_low = q1 - 1.5 * iqr
        iqr_high = q3 + 1.5 * iqr
        rows.append({
            "column_name": col,
            "rule_based_min": low,
            "rule_based_max": high,
            "rule_outliers_count": int(((col_data < low) | (col_data > high)).sum()),
            "iqr_lower_bound": round(iqr_low, 2),
            "iqr_upper_bound": round(iqr_high, 2),
            "iqr_outliers_count": int(((col_data < iqr_low) | (col_data > iqr_high)).sum()),
        })
    report = pd.DataFrame(rows)
    write_csv(report, REPORT_DIR / "outlier_report.csv")
    return report


def create_default_value_check_report(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col, val in {"trestbps": 120, "chol": 0, "oldpeak": 0}.items():
        col_data = pd.to_numeric(df[col], errors="coerce")
        count = int((col_data == val).sum())
        rows.append({
            "column_name": col,
            "default_value": val,
            "occurrence_count": count,
            "percentage": round(count / len(col_data) * 100, 2) if len(col_data) else 0,
        })
    report = pd.DataFrame(rows)
    write_csv(report, REPORT_DIR / "default_value_check_report.csv")
    return report


def create_target_distribution_report(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in ["num", "target_binary"]:
        total = len(df)
        for val, count in df[col].value_counts(dropna=False).items():
            rows.append({
                "target_variable": col,
                "value": str(val),
                "count": int(count),
                "percentage": round(count / total * 100, 2),
            })
    report = pd.DataFrame(rows)
    write_csv(report, REPORT_DIR / "target_distribution_report.csv")
    return report


def main() -> pd.DataFrame:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    RELATIONAL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    flat_df = pd.read_csv(PROCESSED_DIR / "uci_heart_disease_parsed_flat.csv")
    tables = split_relational_tables(flat_df)
    save_relational_tables(tables)
    create_missing_values_report(tables)
    create_duplicate_report(tables)
    create_outlier_report(flat_df)
    create_default_value_check_report(flat_df)
    create_target_distribution_report(flat_df)
    ml_df = build_ml_ready_dataset(tables)
    write_csv(ml_df, PROCESSED_DIR / "ml_ready_heart_disease.csv")
    print(f"Saved ML-ready dataset: {len(ml_df)} rows")
    return ml_df


if __name__ == "__main__":
    main()
