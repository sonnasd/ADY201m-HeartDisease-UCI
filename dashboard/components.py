from pathlib import Path

import pandas as pd
import streamlit as st

try:
    from dashboard.prediction_batch import build_template_csv, predict_patient_file, read_patient_csv, to_csv_bytes
except ModuleNotFoundError:
    from prediction_batch import build_template_csv, predict_patient_file, read_patient_csv, to_csv_bytes


def V(text: str) -> str:
    return text.encode("ascii").decode("unicode_escape")


def show_kpis(data: dict) -> None:
    ml_df = data["ml"]
    missing_cells = int(ml_df.isna().sum().sum())
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total records", f"{len(ml_df):,}")
    col2.metric("Relational tables", "7")
    col3.metric("Missing cells", f"{missing_cells:,}")
    col4.metric("Target = 1", f"{int((ml_df['target_binary'] == 1).sum()):,}")
    st.caption("Note: dataset currently has 920 records, suitable for academics and pipeline demo, but small compared to large-scale datasets.")


def show_image(path: Path, caption: str) -> None:
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.warning("Missing image: " + path.name)


def show_dataframe(title: str, df: pd.DataFrame, height: int = 320) -> None:
    st.subheader(title)
    st.dataframe(df, use_container_width=True, height=height)


def render_prediction_form(model) -> None:
    st.subheader("Prediction with Logistic Regression")
    st.caption("Academic demo. Do not use for medical diagnosis.")
    mode = st.radio("Prediction mode", ["Import CSV batch", "Manual input for 1 patient"], horizontal=True)
    if mode.startswith("Import"):
        render_batch_prediction_upload(model)
        return

    with st.form("prediction_form"):
        patient_id = st.text_input("patient_id", value="DEMO_SINGLE_001")
        c1, c2, c3 = st.columns(3)
        age = c1.number_input("age", min_value=1.0, max_value=120.0, value=55.0)
        sex = c2.selectbox("sex", [0.0, 1.0], index=1)
        cp = c3.selectbox("cp", [1.0, 2.0, 3.0, 4.0], index=1)

        c1, c2, c3 = st.columns(3)
        trestbps = c1.number_input("trestbps", min_value=50.0, max_value=300.0, value=130.0)
        chol = c2.number_input("chol", min_value=0.0, max_value=700.0, value=240.0)
        fbs = c3.selectbox("fbs", [0.0, 1.0], index=0)

        c1, c2, c3 = st.columns(3)
        restecg = c1.selectbox("restecg", [0.0, 1.0, 2.0], index=0)
        thalach = c2.number_input("thalach", min_value=40.0, max_value=250.0, value=150.0)
        exang = c3.selectbox("exang", [0.0, 1.0], index=0)

        c1, c2, c3, c4 = st.columns(4)
        oldpeak = c1.number_input("oldpeak", min_value=0.0, max_value=10.0, value=1.0)
        slope = c2.selectbox("slope", [1.0, 2.0, 3.0], index=1)
        ca = c3.selectbox("ca", [0.0, 1.0, 2.0, 3.0], index=0)
        thal = c4.selectbox("thal", [3.0, 6.0, 7.0], index=0)
        submitted = st.form_submit_button("Predict")

    if submitted:
        sample = pd.DataFrame([{name: value for name, value in {
            "age": age, "sex": sex, "cp": cp, "trestbps": trestbps, "chol": chol,
            "fbs": fbs, "restecg": restecg, "thalach": thalach, "exang": exang,
            "oldpeak": oldpeak, "slope": slope, "ca": ca, "thal": thal,
        }.items()}])
        prediction = int(model.predict(sample)[0])
        probability = float(model.predict_proba(sample)[0][1])
        st.write(f"patient_id = {patient_id}")
        st.success(f"target_binary = {prediction}")
        st.metric("Probability of target = 1", f"{probability:.2%}")
        st.caption("Meaning: record has a pattern similar to the presence of heart disease group in the UCI dataset.")

def render_batch_prediction_upload(model) -> None:
    st.caption("Upload patient CSV file for row-by-row prediction. Results are for educational purposes only, do not use for medical diagnosis.")
    st.download_button(
        "Download CSV template",
        data=build_template_csv(),
        file_name="patient_prediction_template.csv",
        mime="text/csv",
    )

    with st.form("batch_prediction_form"):
        uploaded_file = st.file_uploader("Import patient CSV", type=["csv"])
        submitted = st.form_submit_button("Predict batch")

    if not submitted:
        return
    if uploaded_file is None:
        st.error("Please import a patient CSV first.")
        return

    try:
        patient_df = read_patient_csv(uploaded_file)
        result_df = predict_patient_file(model, patient_df)
    except UnicodeDecodeError:
        st.error("CSV must be saved as UTF-8 or UTF-8-SIG.")
        return
    except ValueError as exc:
        st.error(str(exc))
        return

    st.success("Prediction complete. Download the result file below.")
    show_dataframe("Prediction results preview", result_df.head(100), height=360)
    st.download_button(
        "Download prediction_results.csv",
        data=to_csv_bytes(result_df),
        file_name="prediction_results.csv",
        mime="text/csv",
    )
