import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "reports" / "outputs"
FIGURE_DIR = BASE_DIR / "reports" / "figures"
MODEL_DIR = BASE_DIR / "models"
BASE_FEATURES = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
NUMERIC_FEATURES = {"age", "trestbps", "chol", "thalach", "oldpeak"}
CATEGORICAL_FEATURES = {"sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"}


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def make_one_hot_encoder():
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def build_preprocessor(features: list[str]) -> ColumnTransformer:
    transformers = []
    numeric_cols = [col for col in features if col in NUMERIC_FEATURES]
    categorical_cols = [col for col in features if col in CATEGORICAL_FEATURES]
    if numeric_cols:
        transformers.append(("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric_cols))
    if categorical_cols:
        transformers.append(("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", make_one_hot_encoder())]), categorical_cols))
    return ColumnTransformer(transformers=transformers)


def load_selected_features() -> list[str]:
    path = REPORT_DIR / "selected_correlation_features.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run python src/03_eda.py first.")
    df = pd.read_csv(path)
    forbidden = {"num", "target_binary", "patient_id", "encounter_id"}
    features = [feature for feature in df["feature"].dropna().astype(str).tolist() if feature not in forbidden]
    if not features:
        raise AssertionError("EDA-filtered feature set is empty.")
    return features


def train_and_evaluate() -> pd.DataFrame:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PROCESSED_DIR / "ml_ready_heart_disease.csv").dropna(subset=["target_binary"])
    y = df["target_binary"].astype(int)
    feature_sets = {
        "full_features": BASE_FEATURES,
        "eda_filtered_features": load_selected_features(),
    }
    model_factories = {
        "Logistic Regression": lambda: LogisticRegression(random_state=42, max_iter=1000),
        "Decision Tree": lambda: DecisionTreeClassifier(random_state=42, max_depth=5),
        "Random Forest": lambda: RandomForestClassifier(random_state=42, n_estimators=100, max_depth=6),
    }
    rows = []
    reports = []
    best = None
    for feature_set, features in feature_sets.items():
        X_train, X_test, y_train, y_test = train_test_split(df[features], y, test_size=0.2, random_state=42, stratify=y)
        reports.append(f"=== Feature Set: {feature_set} ===\nFeatures: {features}\n")
        for model_name, make_estimator in model_factories.items():
            pipeline = Pipeline([("preprocessor", build_preprocessor(features)), ("classifier", make_estimator())])
            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            row = {
                "feature_set": feature_set,
                "model_name": model_name,
                "accuracy": round(accuracy_score(y_test, y_pred), 4),
                "precision": round(precision_score(y_test, y_pred), 4),
                "recall": round(recall_score(y_test, y_pred), 4),
                "f1_score": round(f1_score(y_test, y_pred), 4),
            }
            rows.append(row)
            reports.append(f"--- {model_name} ---\n{classification_report(y_test, y_pred)}")
            candidate = (row["f1_score"], row["recall"], feature_set, model_name, confusion_matrix(y_test, y_pred), pipeline)
            if best is None or candidate[:2] > best[:2]:
                best = candidate

    metrics_df = pd.DataFrame(rows)
    write_csv(metrics_df, REPORT_DIR / "model_metrics.csv")
    (REPORT_DIR / "classification_report.txt").write_text("\n".join(reports), encoding="utf-8")
    # Streamlit loads only this deployment artifact. Other models are reproducible from metrics/code.
    joblib.dump(best[5], MODEL_DIR / "best_model.joblib")

    plot_df = metrics_df.copy()
    plot_df["f1_score"] = plot_df["f1_score"] * 100

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    sns.barplot(data=plot_df, x="model_name", y="f1_score", hue="feature_set", ax=ax)
    ax.set_title("F1-score Comparison by Model and Feature Set")
    ax.set_xlabel("Model")
    ax.set_ylabel("F1-score (%)")
    ax.set_ylim(0, 100)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f%%", padding=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "model_comparison_f1.png", dpi=300)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.8, 5.2))
    ConfusionMatrixDisplay(best[4], display_labels=["0", "1"]).plot(cmap="Blues", ax=ax, colorbar=False)
    ax.set_title(f"Confusion Matrix - {best[3]} ({best[2]})")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "confusion_matrix.png", dpi=300)
    plt.close(fig)

    pct_cols = ["accuracy", "precision", "recall", "f1_score"]
    display_df = metrics_df.copy()
    for col in pct_cols:
        display_df[col] = display_df[col].apply(lambda v: f"{v * 100:.2f}%")
    print(display_df.to_string(index=False))
    print(f"Best model for dashboard: {best[3]} | feature_set={best[2]}")
    return metrics_df


if __name__ == "__main__":
    train_and_evaluate()
