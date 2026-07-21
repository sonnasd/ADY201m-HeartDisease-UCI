from io import StringIO

import pandas as pd

REQUIRED_FEATURES = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
]

FEATURE_RANGES = {
    "age": (1.0, 120.0),
    "sex": (0.0, 1.0),
    "cp": (1.0, 4.0),
    "trestbps": (50.0, 300.0),
    "chol": (0.0, 700.0),
    "fbs": (0.0, 1.0),
    "restecg": (0.0, 2.0),
    "thalach": (40.0, 250.0),
    "exang": (0.0, 1.0),
    "oldpeak": (0.0, 10.0),
    "slope": (1.0, 3.0),
    "ca": (0.0, 3.0),
    "thal": (3.0, 7.0),
}

RESULT_COLUMNS = [
    "prediction_target_binary",
    "probability_target_1",
    "risk_label",
    "row_status",
    "error_message",
]


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def build_template_csv() -> bytes:
    template = pd.DataFrame([
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
        }
    ])
    return to_csv_bytes(template)


def read_patient_csv(uploaded_file) -> pd.DataFrame:
    text = uploaded_file.getvalue().decode("utf-8-sig")
    return pd.read_csv(StringIO(text))


def validate_patient_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    missing_columns = [col for col in REQUIRED_FEATURES if col not in df.columns]
    if missing_columns:
        raise ValueError("Missing required columns: " + ", ".join(missing_columns))
    if df.empty:
        raise ValueError("Input CSV is empty.")

    result = df.copy()
    features = pd.DataFrame(index=result.index)
    row_errors = {idx: [] for idx in result.index}
    row_has_missing = pd.Series(False, index=result.index)

    for col in REQUIRED_FEATURES:
        raw = result[col]
        missing_mask = raw.isna() | raw.astype(str).str.strip().eq("")
        numeric = pd.to_numeric(raw, errors="coerce")
        low, high = FEATURE_RANGES[col]
        bad_type = numeric.isna() & ~missing_mask
        bad_range = numeric.notna() & ((numeric < low) | (numeric > high))

        features[col] = numeric
        row_has_missing = row_has_missing | missing_mask
        for idx in result.index[bad_type]:
            row_errors[idx].append(f"{col} is not numeric")
        for idx in result.index[bad_range]:
            row_errors[idx].append(f"{col} outside range {low:g}-{high:g}")

    for col in RESULT_COLUMNS:
        result[col] = pd.NA
    result["error_message"] = ["; ".join(row_errors[idx]) for idx in result.index]
    result["row_status"] = "predicted"
    result.loc[row_has_missing, "row_status"] = "predicted_with_missing"
    result.loc[result["error_message"].ne(""), "row_status"] = "invalid"
    return result, features[REQUIRED_FEATURES]


def predict_patient_file(model, df: pd.DataFrame) -> pd.DataFrame:
    result, features = validate_patient_rows(df)
    valid_mask = result["row_status"].ne("invalid")
    if not valid_mask.any():
        return result

    predictions = model.predict(features.loc[valid_mask])
    probabilities = model.predict_proba(features.loc[valid_mask])[:, 1]
    result.loc[valid_mask, "prediction_target_binary"] = predictions.astype(int)
    result.loc[valid_mask, "probability_target_1"] = probabilities.round(4)
    result.loc[valid_mask, "risk_label"] = [
        "Predicted disease pattern" if int(pred) == 1 else "No predicted disease pattern"
        for pred in predictions
    ]
    return result
