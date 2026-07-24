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
    col1.metric(V("T\\u1ed5ng record"), f"{len(ml_df):,}")
    col2.metric(V("S\\u1ed1 b\\u1ea3ng quan h\\u1ec7"), "7")
    col3.metric("Missing cells", f"{missing_cells:,}")
    col4.metric("Target = 1", f"{int((ml_df['target_binary'] == 1).sum()):,}")
    st.caption(V("L\\u01b0u \\u00fd: dataset hi\\u1ec7n c\\u00f3 920 record, ph\\u00f9 h\\u1ee3p cho h\\u1ecdc thu\\u1eadt v\\u00e0 demo pipeline nh\\u01b0ng v\\u1eabn nh\\u1ecf so v\\u1edbi nh\\u00f3m d\\u1eef li\\u1ec7u quy m\\u00f4 l\\u1edbn."))


def show_image(path: Path, caption: str) -> None:
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.warning(V("Thi\\u1ebfu h\\u00ecnh: ") + path.name)


def show_dataframe(title: str, df: pd.DataFrame, height: int = 320) -> None:
    st.subheader(title)
    st.dataframe(df, use_container_width=True, height=height)


def render_prediction_form(model) -> None:
    st.subheader(V("D\\u1ef1 \\u0111o\\u00e1n th\\u1eed v\\u1edbi Logistic Regression"))
    st.caption(V("Demo h\\u1ecdc thu\\u1eadt. Kh\\u00f4ng d\\u00f9ng \\u0111\\u1ec3 ch\\u1ea9n \\u0111o\\u00e1n y t\\u1ebf."))
    mode = st.radio("Prediction mode", [V("Import danh s\\u00e1ch CSV"), V("Nh\\u1eadp tay 1 b\\u1ec7nh nh\\u00e2n")], horizontal=True)
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
        submitted = st.form_submit_button(V("D\\u1ef1 \\u0111o\\u00e1n"))

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
        st.metric(V("X\\u00e1c su\\u1ea5t thu\\u1ed9c nh\\u00f3m target = 1"), f"{probability:.2%}")
        st.caption(V("\\u00dd ngh\\u0129a: record c\\u00f3 pattern g\\u1ea7n nh\\u00f3m c\\u00f3 presence of heart disease trong dataset UCI."))

def render_batch_prediction_upload(model) -> None:
    st.caption(V("Upload file CSV b\\u1ec7nh nh\\u00e2n \\u0111\\u1ec3 d\\u1ef1 \\u0111o\\u00e1n t\\u1eebng d\\u00f2ng. K\\u1ebft qu\\u1ea3 ch\\u1ec9 ph\\u1ee5c v\\u1ee5 h\\u1ecdc thu\\u1eadt, kh\\u00f4ng d\\u00f9ng \\u0111\\u1ec3 ch\\u1ea9n \\u0111o\\u00e1n y t\\u1ebf."))
    st.download_button(
        "Download CSV template",
        data=build_template_csv(),
        file_name="patient_prediction_template.csv",
        mime="text/csv",
    )

    with st.form("batch_prediction_form"):
        uploaded_file = st.file_uploader("Import patient CSV", type=["csv"])
        submitted = st.form_submit_button(V("D\\u1ef1 \\u0111o\\u00e1n danh s\\u00e1ch"))

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

    st.success(V("D\\u1ef1 \\u0111o\\u00e1n xong. T\\u1ea3i file k\\u1ebft qu\\u1ea3 b\\u00ean d\\u01b0\\u1edbi."))
    show_dataframe("Prediction results preview", result_df.head(100), height=360)
    st.download_button(
        "Download prediction_results.csv",
        data=to_csv_bytes(result_df),
        file_name="prediction_results.csv",
        mime="text/csv",
    )
