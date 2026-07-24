# ADY201m Heart Disease UCI Project

Dự án phân tích UCI Heart Disease Dataset bằng Python scripts, SQL Server và Streamlit dashboard. Pipeline gồm: data profile, preprocessing/cleaning, relational database, data quality, EDA, machine learning và dashboard.

## 1. Setup

Không cần nộp hoặc dùng `.venv`. Cài package trực tiếp bằng Python đang dùng trên máy:

```powershell
pip install -r requirements.txt
```

## 2. Chạy pipeline Python scripts

Chạy từng phần theo thứ tự, tương ứng với cấu trúc notebook cũ:

```powershell
python src\01_data_profile.py
python src\02_load_flat_data.py
python src\03_preprocessing_cleaning.py
python src\04_eda.py
python src\05_machine_learning.py
python src\06_validate_outputs.py
```

Hoặc chạy toàn bộ pipeline:

```powershell
python processdata.py
```

Output chính:

<<<<<<< HEAD
- `data/processed/uci_heart_disease_parsed_flat.csv`: dữ liệu phẳng đã parse.
- `data/processed/relational/*.csv`: 7 bảng quan hệ.
- `data/processed/ml_ready_heart_disease.csv`: dataset cho ML.
- `reports/outputs/*.csv`: báo cáo missing, duplicate, outlier, metrics.
- `reports/figures/*.png`: 17 biểu đồ PNG cho báo cáo và dashboard.
- `models/*.joblib`: model đã train, gồm `best_model.joblib` cho dashboard.
=======
- This project is an academic demo.
- The dataset is small and contains high missing rates in some columns.
- The dashboard prediction is not a medical diagnosis tool.

>>>>>>> 0f29d34c5e910262f27550daff7272c05b65128b

## 3. SQL Server

Database mặc định: `HeartDiseaseClinicalDB`.

Chạy trong SSMS:

1. `sql/01_create_database.sql`
2. `sql/02_create_tables.sql`
3. Nạp flat CSV vào staging table bằng Python:

```powershell
python src\02_load_flat_data.py
```

4. Chạy tiếp:
   - `sql/04_split_relational_data.sql`
   - `sql/05_data_quality_reports.sql`
   - `sql/06_analysis_queries.sql`
   - `sql/07_create_ml_view.sql`

Nếu dùng `sql/Dataset.sql`, bật SQLCMD Mode trong SSMS vì file dùng `:r` để gọi các script con.

## 4. Dashboard

Streamlit chạy từ file `.py`, không dùng notebook:

```powershell
streamlit run dashboard\streamlit_app.py
```

Dashboard đọc dữ liệu từ `data/processed`, `reports/outputs`, `reports/figures` và `models`.

## 5. Screenshot cần chèn vào báo cáo

SQL/SSMS:

- Query 1: row count theo `source_database`.
- Query 2: phân bố `target_binary`.
- Query 3: chest pain type theo target.
- Query 4: chỉ số trung bình theo target.
- Query 5: top outliers theo cholesterol.
- Query 6: window function xếp hạng `oldpeak` trong từng nhóm target.
- Query 7: CTE/subquery so sánh tỷ lệ target=1 theo source với tỷ lệ chung.

Dashboard Streamlit:

- Overview.
- Data Quality.
- EDA: `correlation_heatmap.png`, `selected_correlation_heatmap.png`, `age_thalach_scatter.png`, `age_group_target_rate.png`.
- SQL Results: bảng Query 1-7 tương đương.
- ML Demo: `model_metrics.csv`, `classification_report.txt`, `confusion_matrix.png`, `model_comparison_f1.png`.
- Prediction Form.

Validation:

```powershell
python src\06_validate_outputs.py
```

## 6. Citation

Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). Heart Disease [Dataset]. UCI Machine Learning Repository. DOI: `10.24432/C52P4X`.

Kết quả chỉ phục vụ mục đích học tập trong môn ADY201m, không thay thế chẩn đoán hoặc tư vấn y tế.
