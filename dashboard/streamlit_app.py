from pathlib import Path

import streamlit as st

try:
    from dashboard.components import render_prediction_form, show_dataframe, show_image, show_kpis
    from dashboard.data_loader import build_sql_result_frames, get_figure_path, load_all_data, load_model
except ModuleNotFoundError:
    from components import render_prediction_form, show_dataframe, show_image, show_kpis
    from data_loader import build_sql_result_frames, get_figure_path, load_all_data, load_model


def V(text: str) -> str:
    return text.encode("ascii").decode("unicode_escape")


st.set_page_config(page_title="ADY Heart Disease Dashboard", layout="wide")

st.title("ADY Heart Disease Dashboard")
st.caption(V("T\\u1ed5ng h\\u1ee3p data quality, EDA, SQL analysis, ML v\\u00e0 demo d\\u1ef1 \\u0111o\\u00e1n. Ch\\u1ec9 ph\\u1ee5c v\\u1ee5 h\\u1ecdc t\\u1eadp."))

data = load_all_data()
sql_results = build_sql_result_frames(data)
model = load_model()

tabs = st.tabs(["Overview", "Data Quality", "EDA", "SQL Results", "ML Demo", "Prediction Form"])

with tabs[0]:
    show_kpis(data)
    c1, c2 = st.columns([1.1, 1])
    with c1:
        show_dataframe("Raw shape report", data["shape_report"], height=220)
        show_dataframe("Target distribution report", data["target_report"], height=240)
    with c2:
        show_image(get_figure_path("target_distribution.png"), "Target distribution")
        show_image(get_figure_path("patient_count_by_source.png"), "Patient count by source")

with tabs[1]:
    show_dataframe("Missing values report", data["missing_report"])
    show_dataframe("Duplicate report", data["duplicate_report"], height=180)
    c1, c2 = st.columns(2)
    with c1:
        show_dataframe("Outlier report", data["outlier_report"], height=220)
    with c2:
        show_dataframe("Default value report", data["default_report"], height=220)
    show_image(get_figure_path("missing_value_heatmap.png"), "Missing value heatmap")
    show_image(get_figure_path("outliers_boxplot.png"), "Outlier boxplot")

with tabs[2]:
    c1, c2 = st.columns(2)
    with c1:
        show_image(get_figure_path("age_distribution.png"), "Age distribution")
        show_image(get_figure_path("chol_by_target.png"), "Cholesterol by target")
        show_image(get_figure_path("age_group_target_rate.png"), "Target rate by age group")
        show_image(get_figure_path("correlation_heatmap.png"), "Correlation heatmap")
    with c2:
        show_image(get_figure_path("cp_target.png"), "Chest pain vs target")
        show_image(get_figure_path("oldpeak_by_target.png"), "Oldpeak by target")
        show_image(get_figure_path("age_thalach_scatter.png"), "Age vs thalach scatter")
        show_image(get_figure_path("selected_correlation_heatmap.png"), "Selected correlation heatmap")
    c1, c2 = st.columns(2)
    with c1:
        show_dataframe("Python crosstab cp x target", data["python_cp_target"], height=260)
        show_dataframe("Selected correlation features", data["selected_correlation_features"], height=260)
    with c2:
        show_dataframe("Python age group summary", data["python_age_group_summary"], height=260)
        show_dataframe("Correlation with target", data["python_correlation_target"], height=260)
    st.caption("Selected correlation features exclude num and target_binary to avoid leakage.")

with tabs[3]:
    st.info(V("Tab n\\u00e0y hi\\u1ec3n th\\u1ecb k\\u1ebft qu\\u1ea3 t\\u01b0\\u01a1ng \\u0111\\u01b0\\u01a1ng c\\u00e1c query SQL \\u0111\\u1ec3 \\u0111\\u1ed1i chi\\u1ebfu report. Screenshot SQL Server v\\u1eabn c\\u1ea7n ch\\u1ee5p tr\\u1ef1c ti\\u1ebfp khi ch\\u1ea1y SSMS."))
    show_dataframe("Source database counts", sql_results["source_counts"], height=220)
    show_dataframe("Target distribution", sql_results["target_dist"], height=220)
    show_dataframe("Chest pain by target", sql_results["cp_target"], height=280)
    show_dataframe("Average metrics by target", sql_results["avg_metrics"], height=220)
    show_dataframe("Oldpeak rank", sql_results["oldpeak_rank"], height=320)
    show_dataframe("Source target rate vs overall", sql_results["source_target_rate_vs_overall"], height=220)

with tabs[4]:
    st.caption(V("Random Forest hi\\u1ec7n l\\u00e0 m\\u00f4 h\\u00ecnh t\\u1ed1t nh\\u1ea5t theo F1-score v\\u00e0 Recall tr\\u00ean t\\u1eadp ki\\u1ec3m tra. K\\u1ebft qu\\u1ea3 ch\\u1ec9 ph\\u1ee5c v\\u1ee5 h\\u1ecdc thu\\u1eadt."))
    show_dataframe("Model metrics", data["metrics"], height=200)
    c1, c2 = st.columns(2)
    with c1:
        show_image(get_figure_path("model_comparison_f1.png"), "Model comparison by F1-score")
    with c2:
        show_image(get_figure_path("confusion_matrix.png"), "Confusion matrix - best model")
    report_path = Path(__file__).resolve().parents[1] / "reports" / "outputs" / "classification_report.txt"
    if report_path.exists():
        st.subheader("Classification report")
        st.code(report_path.read_text(encoding="utf-8"), language="text")

with tabs[5]:
    render_prediction_form(model)
