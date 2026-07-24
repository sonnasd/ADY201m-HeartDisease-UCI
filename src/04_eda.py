import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "reports" / "outputs"
FIGURE_DIR = BASE_DIR / "reports" / "figures"
AGE_GROUP_ORDER = ["<40", "40-49", "50-59", "60+"]
CORR_THRESHOLD = 0.10


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def save_current(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / name, dpi=300)
    plt.close(fig)


def plot_correlation_heatmap(ax, corr_matrix: pd.DataFrame, title: str) -> None:
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        vmin=-1,
        vmax=1,
        linewidths=0.8,
        linecolor="white",
        square=True,
        annot_kws={"size": 9, "weight": "bold"},
        cbar_kws={"label": "Correlation", "shrink": 0.8},
        ax=ax,
    )
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=45)
    ax.tick_params(axis="y", rotation=0)


def write_analysis_outputs(ml_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cp_target = pd.crosstab(ml_df["cp"], ml_df["target_binary"], margins=True).reset_index()
    write_csv(cp_target, REPORT_DIR / "python_crosstab_cp_target.csv")

    age_summary = (
        ml_df.assign(age_group=pd.Categorical(ml_df["age_group"], categories=AGE_GROUP_ORDER, ordered=True))
        .groupby("age_group", observed=False)
        .agg(
            total_records=("target_binary", "size"),
            positive_records=("target_binary", "sum"),
            target_positive_rate=("target_binary", "mean"),
            avg_thalach=("thalach", "mean"),
            avg_oldpeak=("oldpeak", "mean"),
        )
        .reset_index()
    )
    age_summary["target_positive_rate"] = (age_summary["target_positive_rate"] * 100).round(2)
    age_summary["avg_thalach"] = age_summary["avg_thalach"].round(2)
    age_summary["avg_oldpeak"] = age_summary["avg_oldpeak"].round(2)
    write_csv(age_summary, REPORT_DIR / "python_age_group_summary.csv")

    numeric_cols = [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
        "exang", "oldpeak", "slope", "ca", "thal", "target_binary",
    ]
    corr = (
        ml_df[numeric_cols]
        .corr(numeric_only=True)["target_binary"]
        .drop(labels=["target_binary"])
        .sort_values(key=lambda s: s.abs(), ascending=False)
        .reset_index()
        .rename(columns={"index": "feature", "target_binary": "correlation_with_target"})
    )
    corr["correlation_with_target"] = corr["correlation_with_target"].round(4)
    write_csv(corr, REPORT_DIR / "python_correlation_target.csv")

    selected = corr.loc[corr["correlation_with_target"].abs() >= CORR_THRESHOLD].copy()
    selected = selected.loc[~selected["feature"].isin(["num", "target_binary"])]
    write_csv(selected, REPORT_DIR / "selected_correlation_features.csv")
    return age_summary, corr, selected


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    ml_df = pd.read_csv(PROCESSED_DIR / "ml_ready_heart_disease.csv")
    flat_df = pd.read_csv(PROCESSED_DIR / "uci_heart_disease_parsed_flat.csv")
    age_summary, _, selected = write_analysis_outputs(ml_df)

    fig, ax = plt.subplots(figsize=(6, 4.5))
    counts = ml_df["target_binary"].value_counts().sort_index()
    ax.bar(["0", "1"], counts.values, color=["#3B82F6", "#F59E0B"])
    ax.set_title("Phân bố target_binary")
    ax.set_xlabel("target_binary")
    ax.set_ylabel("Số record")
    for i, value in enumerate(counts.values):
        ax.text(i, value, str(value), ha="center", va="bottom")
    save_current(fig, "target_distribution.png")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    source_counts = flat_df["source_database"].value_counts().sort_values(ascending=False)
    sns.barplot(x=source_counts.index, y=source_counts.values, color="#1E40AF", ax=ax)
    ax.set_title("Số record theo source_database")
    ax.set_xlabel("Source database")
    ax.set_ylabel("Số record")
    ax.tick_params(axis="x", rotation=20)
    for i, value in enumerate(source_counts.values):
        ax.text(i, value, str(value), ha="center", va="bottom")
    save_current(fig, "patient_count_by_source.png")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    source_rate = (
        flat_df.groupby("source_database")["target_binary"]
        .mean()
        .mul(100)
        .sort_values(ascending=False)
        .reset_index(name="heart_disease_rate")
    )
    sns.barplot(data=source_rate, x="source_database", y="heart_disease_rate", color="#DC2626", ax=ax)
    ax.set_title("Tỷ lệ bệnh tim theo source_database")
    ax.set_xlabel("Source database")
    ax.set_ylabel("Tỷ lệ target=1 (%)")
    ax.set_ylim(0, max(100, float(source_rate["heart_disease_rate"].max()) + 5))
    ax.tick_params(axis="x", rotation=20)
    for i, row in source_rate.iterrows():
        ax.text(i, row["heart_disease_rate"], f"{row['heart_disease_rate']:.1f}%", ha="center", va="bottom")
    save_current(fig, "heart_disease_rate_by_region.png")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.histplot(data=ml_df, x="age", hue="target_binary", bins=20, multiple="stack", ax=ax)
    ax.set_title("Phân bố tuổi theo target")
    ax.set_xlabel("Tuổi")
    ax.set_ylabel("Số record")
    save_current(fig, "age_distribution.png")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    cp_counts = ml_df.groupby(["cp", "target_binary"]).size().reset_index(name="count")
    sns.barplot(data=cp_counts, x="cp", y="count", hue="target_binary", ax=ax)
    ax.set_title("Chest pain type theo target")
    ax.set_xlabel("cp")
    ax.set_ylabel("Số record")
    save_current(fig, "cp_target.png")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    cp_disease_counts = (
        ml_df.loc[ml_df["target_binary"] == 1, "cp"]
        .value_counts()
        .reset_index(name="count")
        .rename(columns={"cp": "cp"})
        .assign(cp=lambda x: x["cp"].astype(int))
        .sort_values("cp")
        .reset_index(drop=True)
    )
    bars = ax.bar(cp_disease_counts["cp"].astype(str), cp_disease_counts["count"], color="#EF4444")
    ax.set_title("Phân bố loại đau ngực ở nhóm bệnh nhân bệnh tim")
    ax.set_xlabel("Chest Pain Type (cp)")
    ax.set_ylabel("Số record")
    for bar, value in zip(bars, cp_disease_counts["count"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(value), ha="center", va="bottom")
    save_current(fig, "cp_heart_disease.png")

    for y_col, title, name in [
        ("chol", "Cholesterol theo target", "chol_by_target.png"),
        ("oldpeak", "Oldpeak theo target", "oldpeak_by_target.png"),
    ]:
        fig, ax = plt.subplots(figsize=(7, 4.5))
        sns.boxplot(data=ml_df, x="target_binary", y=y_col, ax=ax)
        ax.set_title(title)
        ax.set_xlabel("target_binary")
        ax.set_ylabel(y_col)
        save_current(fig, name)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.scatterplot(data=ml_df.dropna(subset=["age", "thalach", "target_binary"]), x="age", y="thalach", hue="target_binary", alpha=0.72, ax=ax)
    ax.set_title("Tuổi và nhịp tim tối đa theo target")
    ax.set_xlabel("Tuổi")
    ax.set_ylabel("thalach - nhịp tim tối đa")
    ax.legend(title="target_binary")
    save_current(fig, "age_thalach_scatter.png")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.lineplot(data=age_summary, x="age_group", y="target_positive_rate", marker="o", color="#1E40AF", ax=ax)
    ax.set_title("Tỷ lệ target=1 theo nhóm tuổi")
    ax.set_xlabel("Nhóm tuổi")
    ax.set_ylabel("Tỷ lệ target=1 (%)")
    ax.set_ylim(0, max(100, float(age_summary["target_positive_rate"].max()) + 5))
    for _, row in age_summary.iterrows():
        ax.text(row["age_group"], row["target_positive_rate"], f"{row['target_positive_rate']:.1f}%", ha="center", va="bottom")
    save_current(fig, "age_group_target_rate.png")

    numeric_cols = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target_binary"]
    corr_matrix = ml_df[numeric_cols].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(10, 8))
    plot_correlation_heatmap(ax, corr_matrix, "Correlation heatmap")
    save_current(fig, "correlation_heatmap.png")

    selected_features = selected["feature"].tolist() + ["target_binary"]
    fig, ax = plt.subplots(figsize=(10, 9))
    plot_correlation_heatmap(ax, corr_matrix.loc[selected_features, selected_features], f"Selected Correlation Heatmap (|corr| >= {CORR_THRESHOLD:.2f})")
    save_current(fig, "selected_correlation_heatmap.png")

    fig, ax = plt.subplots(figsize=(10, 4.5))
    sns.heatmap(ml_df.isna(), cbar=False, yticklabels=False, cmap="Blues", ax=ax)
    ax.set_title("Missing value heatmap")
    save_current(fig, "missing_value_heatmap.png")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.boxplot(data=ml_df[["trestbps", "chol", "thalach", "oldpeak"]], ax=ax)
    ax.set_title("Boxplot các biến kiểm tra outlier")
    ax.set_xlabel("Biến")
    ax.set_ylabel("Giá trị")
    save_current(fig, "outliers_boxplot.png")

    print(f"Saved figures to {FIGURE_DIR}")
    print(f"Saved Python analysis outputs to {REPORT_DIR}")


if __name__ == "__main__":
    main()
