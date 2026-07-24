# ADY201m Heart Disease UCI Project

This project analyzes the UCI Heart Disease Dataset using Python scripts, SQL Server, and a Streamlit dashboard. The pipeline includes: data profiling, preprocessing/cleaning, relational database design, data quality assurance, exploratory data analysis (EDA), machine learning, and dashboard deployment.

## 1. Setup

There is no need to submit or use a `.venv`. Install the required packages directly using your current Python environment:

```powershell
pip install -r requirements.txt
```

## 2. Running the Python Scripts Pipeline

You can run each script sequentially in the following order, corresponding to the previous notebook structure:

```powershell
python src\01_data_profile.py
python src\02_load_flat_data.py
python src\03_preprocessing_cleaning.py
python src\04_eda.py
python src\05_machine_learning.py
python src\06_validate_outputs.py
```

Alternatively, you can execute the entire pipeline with a single command:

```powershell
python processdata.py
```

Main outputs generated:

- `data/processed/uci_heart_disease_parsed_flat.csv`: The parsed flat dataset.
- `data/processed/relational/*.csv`: The 7 normalized relational tables.
- `data/processed/ml_ready_heart_disease.csv`: The final dataset ready for machine learning.
- `reports/outputs/*.csv`: Data quality reports detailing missing values, duplicates, outliers, and metrics.
- `reports/figures/*.png`: 17 PNG charts used in the report and dashboard.
- `models/*.joblib`: Trained models, including `best_model.joblib` used by the dashboard.

## 3. SQL Server

Default database name: `HeartDiseaseClinicalDB`.

To execute in SQL Server Management Studio (SSMS):

1. Run `sql/01_create_database.sql`
2. Run `sql/02_create_tables.sql`
3. Load the flat CSV into the staging table using Python:

```powershell
python src\02_load_flat_data.py
```

4. Continue running the remaining SQL scripts:
   - `sql/04_split_relational_data.sql`
   - `sql/05_data_quality_reports.sql`
   - `sql/06_analysis_queries.sql`
   - `sql/07_create_ml_view.sql`

If you are using the `sql/Dataset.sql` script to run everything, make sure to enable **SQLCMD Mode** in SSMS, as the file uses the `:r` command to call sub-scripts.

## 4. Dashboard

The Streamlit dashboard is run directly from the `.py` script (not a notebook):

```powershell
streamlit run dashboard\streamlit_app.py
```

The dashboard reads its data from the `data/processed`, `reports/outputs`, `reports/figures`, and `models` directories.

## 5. Required Screenshots for the Report

**SQL/SSMS:**

- Query 1: Row count grouped by `source_database`.
- Query 2: Distribution of `target_binary`.
- Query 3: Chest pain type grouped by target.
- Query 4: Average clinical metrics grouped by target.
- Query 5: Top outliers ordered by cholesterol.
- Query 6: Window function ranking `oldpeak` within each target group.
- Query 7: CTE/subquery comparing the target=1 rate by source against the overall rate.

**Streamlit Dashboard:**

- Overview tab.
- Data Quality tab.
- EDA tab: `correlation_heatmap.png`, `selected_correlation_heatmap.png`, `age_thalach_scatter.png`, `age_group_target_rate.png`.
- SQL Results tab: Tables corresponding to Queries 1-7.
- ML Demo tab: `model_metrics.csv`, `classification_report.txt`, `confusion_matrix.png`, `model_comparison_f1.png`.
- Prediction Form tab.

**Validation Script:**

```powershell
python src\06_validate_outputs.py
```

## 6. Citation

Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). Heart Disease [Dataset]. UCI Machine Learning Repository. DOI: `10.24432/C52P4X`.

*Disclaimer: The results of this project are for educational purposes only as part of the ADY201m course and are not intended to replace professional medical diagnosis or advice.*
