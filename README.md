# ADY201m Heart Disease UCI

## Project Overview

This project analyzes the UCI Heart Disease dataset and builds an end-to-end academic data pipeline:

```text
Raw Data -> Cleaning -> Relational Database -> SQL Analysis -> EDA -> Machine Learning -> Streamlit Dashboard
```

The project is for learning and demonstration only. Prediction results must not be used for real medical diagnosis.

## Main Objectives

- Clean and prepare the UCI Heart Disease dataset.
- Build relational tables for SQL/database analysis.
- Perform data quality checks and exploratory data analysis.
- Train and compare binary classification models.
- Deploy the best model in a Streamlit dashboard.
- Support single-patient prediction and batch CSV prediction.

## Dataset

- Source: UCI Heart Disease dataset.
- Records: 920.
- Sources: 4 original data sources.
- Target variable: `target_binary`.

Target meaning:

```text
0 = no predicted heart disease pattern
1 = predicted heart disease pattern
```

## Project Structure

```text
dashboard/                  Streamlit dashboard code
data/raw/uci_heart_disease/ Raw UCI dataset files
data/processed/             Cleaned and ML-ready datasets
data/processed/relational/  Relational CSV tables
docs/                       Documentation and slide plan
models/                     Saved model artifact
reports/figures/            EDA and ML figures
reports/outputs/            CSV/TXT report outputs
sql/                        Database schema and SQL queries
src/                        Data profiling, cleaning, EDA, ML, validation scripts
processdata.py              Full pipeline runner
requirements.txt            Python dependencies
```

## Main Pipeline

Run the full project pipeline:

```powershell
python processdata.py
```

This runs:

```text
src/01_data_profile.py
src/02_preprocessing_cleaning.py
src/03_eda.py
src/04_machine_learning.py
src/05_validate_outputs.py
```

## Streamlit Dashboard

Start the dashboard:

```powershell
streamlit run dashboard/streamlit_app.py
```

Dashboard features:

- Overview KPIs.
- Data quality reports.
- EDA charts and correlation analysis.
- SQL-equivalent result tables.
- ML metrics and confusion matrix.
- Single-patient prediction.
- Batch CSV prediction and downloadable results.

## Machine Learning

Task type:

```text
Binary classification
```

Models compared:

```text
Logistic Regression
Decision Tree
Random Forest
```

Best model:

```text
Random Forest
```

Best model metrics:

```text
Accuracy  = 0.8641
Precision = 0.8598
Recall    = 0.9020
F1-score  = 0.8804
```

Deployment artifact:

```text
models/best_model.joblib
```

Other model files are not stored because they can be reproduced by running the training script. Their evaluation results are kept in `reports/outputs/model_metrics.csv` and `reports/outputs/classification_report.txt`.

## Batch Prediction Demo

Demo input file:

```text
data/demo_patient_batch.csv
```

Required CSV columns:

```text
age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal
```

Recommended optional columns:

```text
patient_id,encounter_id,name,source_database
```

Output columns added by the dashboard:

```text
prediction_target_binary
probability_target_1
risk_label
row_status
error_message
```

## SQL Components

The `sql/` folder contains:

- Database creation script.
- Table creation script.
- Data import script.
- Data quality SQL checks.
- Analysis queries using JOIN, CTE/subquery, and window function.
- ML-ready SQL view.

## Team Contribution

| Member | Main Responsibility |
|---|---|
| Nguyen Huy Son | Data cleaning, machine learning, Streamlit dashboard |
| Pham Minh Quan | Data quality, EDA, visualization, limitations |
| Pham Gia Long | Database design, SQL scripts, SQL analysis |

## Setup

Create and activate a virtual environment if needed:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run validation:

```powershell
python src/05_validate_outputs.py
```

Expected result:

```text
Validation passed.
```

## Notes

- This project is an academic demo.
- The dataset is small and contains high missing rates in some columns.
- The dashboard prediction is not a medical diagnosis tool.
- Do not upload `.venv/`, `__pycache__/`, or temporary files to GitHub.

