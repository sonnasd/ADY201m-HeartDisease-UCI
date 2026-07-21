from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw" / "uci_heart_disease"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "reports" / "outputs"

UCI_COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num",
]
SOURCE_FILES = {
    "cleveland": "processed.cleveland.data",
    "hungarian": "processed.hungarian.data",
    "switzerland": "processed.switzerland.data",
    "va_long_beach": "processed.va.data",
}


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def read_uci_file(source_name: str, file_name: str) -> pd.DataFrame:
    file_path = RAW_DIR / file_name
    if not file_path.exists():
        print(f"[WARNING] File not found: {file_path}")
        return pd.DataFrame(columns=UCI_COLUMNS)
    df = pd.read_csv(file_path, header=0, names=UCI_COLUMNS, na_values=["?", " ?"], skipinitialspace=True)
    df["source_database"] = source_name
    df["source_row_number"] = range(1, len(df) + 1)
    return df


def load_all_sources() -> pd.DataFrame:
    frames = []
    for source_name, file_name in SOURCE_FILES.items():
        df = read_uci_file(source_name, file_name)
        if not df.empty:
            frames.append(df)
            print(f"Loaded {source_name}: {df.shape[0]} rows, {df.shape[1]} columns")
    if not frames:
        raise FileNotFoundError("No UCI files were loaded. Check data/raw/uci_heart_disease/.")
    full_df = pd.concat(frames, ignore_index=True)
    print(f"Combined dataset shape: {full_df.shape}")
    return full_df


def add_generated_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["global_record_number"] = range(1, len(df) + 1)
    df["patient_id"] = df["global_record_number"].apply(lambda x: f"P{x:05d}")
    df["encounter_id"] = df["global_record_number"].apply(lambda x: f"E{x:05d}")
    df["num"] = pd.to_numeric(df["num"], errors="coerce")
    df["target_binary"] = np.where(df["num"] > 0, 1, 0)
    df.loc[df["num"].isna(), "target_binary"] = np.nan
    return df


def convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = UCI_COLUMNS + ["target_binary", "source_row_number", "global_record_number"]
    df = df.copy()
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def create_raw_table_shape_report() -> pd.DataFrame:
    rows = []
    for source_name, file_name in SOURCE_FILES.items():
        file_path = RAW_DIR / file_name
        if file_path.exists():
            df = pd.read_csv(file_path, header=0, na_values=["?", " ?"])
            rows.append({
                "source_name": source_name,
                "file_name": file_name,
                "row_count": len(df),
                "column_count": len(df.columns),
            })
    report = pd.DataFrame(rows)
    write_csv(report, REPORT_DIR / "raw_table_shape_report.csv")
    return report


def create_data_type_report(df: pd.DataFrame) -> pd.DataFrame:
    report = pd.DataFrame([
        {
            "column_name": col,
            "pandas_dtype": str(df[col].dtype),
            "non_null_count": int(df[col].notna().sum()),
            "null_count": int(df[col].isna().sum()),
        }
        for col in df.columns
    ])
    write_csv(report, REPORT_DIR / "data_type_report.csv")
    return report


def main() -> pd.DataFrame:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    df = convert_numeric_columns(add_generated_columns(load_all_sources()))
    write_csv(df, PROCESSED_DIR / "uci_heart_disease_parsed_flat.csv")
    create_raw_table_shape_report()
    create_data_type_report(df)
    print(f"Saved parsed flat dataset: {len(df)} rows")
    return df


if __name__ == "__main__":
    main()
