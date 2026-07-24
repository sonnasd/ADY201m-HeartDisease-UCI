"""
03_preprocessing_cleaning.py
-----------------------------
Script điều phối (orchestrator) giai đoạn Preprocessing & Cleaning.

Luồng xử lý:
  Python (01_data_profile.py)      --> flat CSV
  Python (02_load_flat_data.py)    --> dbo.raw_flat_data (staging table)
  SQL   (04_split_relational_data.sql) --> 7 bảng quan hệ
  SQL   (05_data_quality_reports.sql)  --> báo cáo chất lượng dữ liệu
  SQL   (07_create_ml_view.sql)        --> view với data sạch + features
  Python (script này)          --> query các SQL reports, lưu CSV cho Dashboard
                               --> query view ML, lưu ml_ready_heart_disease.csv

Lưu ý:
  - Tất cả logic xử lý dữ liệu (tách bảng, làm sạch, feature engineering,
    tính báo cáo) đều nằm hoàn toàn trong SQL.
  - Python ở đây chỉ gọi SQL và lưu kết quả.
"""
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

BASE_DIR     = Path(__file__).resolve().parents[1]
SQL_DIR      = BASE_DIR / "sql"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR   = BASE_DIR / "reports" / "outputs"

server             = os.getenv("DB_SERVER", "localhost")
database           = os.getenv("DB_NAME", "HeartDiseaseClinicalDB")
driver             = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server").replace(" ", "+")
trusted_connection = os.getenv("DB_TRUSTED_CONNECTION", "yes")

connection_url = (
    f"mssql+pyodbc://@{server}/{database}"
    f"?driver={driver}&trusted_connection={trusted_connection}&TrustServerCertificate=yes"
)
engine = create_engine(connection_url)


def run_sql_file(conn, sql_path: Path) -> None:
    """Chạy một file SQL, bỏ qua các câu lệnh GO (T-SQL batch separator)."""
    sql = sql_path.read_text(encoding="utf-8")
    # Tách theo GO để thực thi từng batch một
    batches = [b.strip() for b in sql.split("\nGO") if b.strip()]
    for batch in batches:
        if batch:
            conn.execute(text(batch))
    print(f"  Executed: {sql_path.name}")


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


# ────────────────────────────────────────────────────────────
# CÁC CÂU QUERY SQL CHO TỪNG BÁO CÁO (trích từ 05_data_quality_reports.sql)
# ────────────────────────────────────────────────────────────

QUERY_MISSING_VALUES = """
SELECT table_name, column_name, missing_count, missing_pct
FROM (
    SELECT 'patients'     AS table_name, 'age'             AS column_name, SUM(CASE WHEN age IS NULL THEN 1 ELSE 0 END) AS missing_count, ROUND(100.0 * SUM(CASE WHEN age IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS missing_pct FROM dbo.patients
    UNION ALL SELECT 'patients',     'sex',            SUM(CASE WHEN sex IS NULL THEN 1 ELSE 0 END), ROUND(100.0 * SUM(CASE WHEN sex IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) FROM dbo.patients
    UNION ALL SELECT 'symptoms',     'cp',             SUM(CASE WHEN cp IS NULL THEN 1 ELSE 0 END), ROUND(100.0 * SUM(CASE WHEN cp IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) FROM dbo.symptoms
    UNION ALL SELECT 'risk_history', 'fbs',            SUM(CASE WHEN fbs IS NULL THEN 1 ELSE 0 END), ROUND(100.0 * SUM(CASE WHEN fbs IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) FROM dbo.risk_history
    UNION ALL SELECT 'resting_tests','trestbps',       SUM(CASE WHEN trestbps IS NULL THEN 1 ELSE 0 END), ROUND(100.0 * SUM(CASE WHEN trestbps IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) FROM dbo.resting_tests
    UNION ALL SELECT 'resting_tests','chol',           SUM(CASE WHEN chol IS NULL THEN 1 ELSE 0 END), ROUND(100.0 * SUM(CASE WHEN chol IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) FROM dbo.resting_tests
    UNION ALL SELECT 'resting_tests','restecg',        SUM(CASE WHEN restecg IS NULL THEN 1 ELSE 0 END), ROUND(100.0 * SUM(CASE WHEN restecg IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) FROM dbo.resting_tests
    UNION ALL SELECT 'exercise_ecg_tests','thalach',   SUM(CASE WHEN thalach IS NULL THEN 1 ELSE 0 END), ROUND(100.0 * SUM(CASE WHEN thalach IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) FROM dbo.exercise_ecg_tests
    UNION ALL SELECT 'exercise_ecg_tests','exang',     SUM(CASE WHEN exang IS NULL THEN 1 ELSE 0 END), ROUND(100.0 * SUM(CASE WHEN exang IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) FROM dbo.exercise_ecg_tests
    UNION ALL SELECT 'exercise_ecg_tests','oldpeak',   SUM(CASE WHEN oldpeak IS NULL THEN 1 ELSE 0 END), ROUND(100.0 * SUM(CASE WHEN oldpeak IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) FROM dbo.exercise_ecg_tests
    UNION ALL SELECT 'exercise_ecg_tests','slope',     SUM(CASE WHEN slope IS NULL THEN 1 ELSE 0 END), ROUND(100.0 * SUM(CASE WHEN slope IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) FROM dbo.exercise_ecg_tests
    UNION ALL SELECT 'diagnoses',    'ca',             SUM(CASE WHEN ca IS NULL THEN 1 ELSE 0 END), ROUND(100.0 * SUM(CASE WHEN ca IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) FROM dbo.diagnoses
    UNION ALL SELECT 'diagnoses',    'thal',           SUM(CASE WHEN thal IS NULL THEN 1 ELSE 0 END), ROUND(100.0 * SUM(CASE WHEN thal IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) FROM dbo.diagnoses
    UNION ALL SELECT 'diagnoses',    'num',            SUM(CASE WHEN num IS NULL THEN 1 ELSE 0 END), ROUND(100.0 * SUM(CASE WHEN num IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) FROM dbo.diagnoses
    UNION ALL SELECT 'diagnoses',    'target_binary',  SUM(CASE WHEN target_binary IS NULL THEN 1 ELSE 0 END), ROUND(100.0 * SUM(CASE WHEN target_binary IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) FROM dbo.diagnoses
) AS q
"""

QUERY_DUPLICATE = """
SELECT table_name,
       ISNULL(full_duplicate_rows, 0) AS full_duplicate_rows,
       ISNULL(duplicate_rows_excluding_id, 0) AS duplicate_rows_excluding_id
FROM (
    SELECT 'patients' AS table_name, SUM(cnt-1) AS full_duplicate_rows, SUM(cnt-1) AS duplicate_rows_excluding_id
    FROM (SELECT COUNT(*) AS cnt FROM dbo.patients GROUP BY age, sex, source_database, source_row_number HAVING COUNT(*) > 1) t
    UNION ALL
    SELECT 'symptoms', SUM(cnt-1), SUM(cnt-1)
    FROM (SELECT COUNT(*) AS cnt FROM dbo.symptoms GROUP BY encounter_id, cp HAVING COUNT(*) > 1) t
    UNION ALL
    SELECT 'risk_history', SUM(cnt-1), SUM(cnt-1)
    FROM (SELECT COUNT(*) AS cnt FROM dbo.risk_history GROUP BY encounter_id, fbs HAVING COUNT(*) > 1) t
    UNION ALL
    SELECT 'resting_tests', SUM(cnt-1), SUM(cnt-1)
    FROM (SELECT COUNT(*) AS cnt FROM dbo.resting_tests GROUP BY encounter_id, trestbps, chol, restecg HAVING COUNT(*) > 1) t
    UNION ALL
    SELECT 'exercise_ecg_tests', SUM(cnt-1), SUM(cnt-1)
    FROM (SELECT COUNT(*) AS cnt FROM dbo.exercise_ecg_tests GROUP BY encounter_id, thalach, exang, oldpeak, slope HAVING COUNT(*) > 1) t
    UNION ALL
    SELECT 'diagnoses', SUM(cnt-1), SUM(cnt-1)
    FROM (SELECT COUNT(*) AS cnt FROM dbo.diagnoses GROUP BY encounter_id, ca, thal, num, target_binary HAVING COUNT(*) > 1) t
) AS q
"""

QUERY_OUTLIER = """
WITH percentiles AS (
    SELECT
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY trestbps) OVER () AS trestbps_q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY trestbps) OVER () AS trestbps_q3,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY chol)     OVER () AS chol_q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY chol)     OVER () AS chol_q3,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY thalach)  OVER () AS thalach_q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY thalach)  OVER () AS thalach_q3,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY oldpeak)  OVER () AS oldpeak_q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY oldpeak)  OVER () AS oldpeak_q3
    FROM dbo.raw_flat_data
),
bounds AS (
    SELECT DISTINCT
        trestbps_q1, trestbps_q3, (trestbps_q3 - trestbps_q1) AS trestbps_iqr,
        chol_q1, chol_q3, (chol_q3 - chol_q1) AS chol_iqr,
        thalach_q1, thalach_q3, (thalach_q3 - thalach_q1) AS thalach_iqr,
        oldpeak_q1, oldpeak_q3, (oldpeak_q3 - oldpeak_q1) AS oldpeak_iqr
    FROM percentiles
),
counts AS (
    SELECT
        SUM(CASE WHEN trestbps < 80  OR trestbps > 220  THEN 1 ELSE 0 END) AS trestbps_rule_out,
        SUM(CASE WHEN chol     < 80  OR chol     > 600  THEN 1 ELSE 0 END) AS chol_rule_out,
        SUM(CASE WHEN thalach  < 50  OR thalach  > 230  THEN 1 ELSE 0 END) AS thalach_rule_out,
        SUM(CASE WHEN oldpeak  < 0   OR oldpeak  > 10   THEN 1 ELSE 0 END) AS oldpeak_rule_out
    FROM dbo.raw_flat_data
),
iqr_counts AS (
    SELECT
        ROUND(b.trestbps_q1 - 1.5*b.trestbps_iqr, 2) AS trestbps_low,
        ROUND(b.trestbps_q3 + 1.5*b.trestbps_iqr, 2) AS trestbps_high,
        ROUND(b.chol_q1     - 1.5*b.chol_iqr,     2) AS chol_low,
        ROUND(b.chol_q3     + 1.5*b.chol_iqr,     2) AS chol_high,
        ROUND(b.thalach_q1  - 1.5*b.thalach_iqr,  2) AS thalach_low,
        ROUND(b.thalach_q3  + 1.5*b.thalach_iqr,  2) AS thalach_high,
        ROUND(b.oldpeak_q1  - 1.5*b.oldpeak_iqr,  2) AS oldpeak_low,
        ROUND(b.oldpeak_q3  + 1.5*b.oldpeak_iqr,  2) AS oldpeak_high,
        SUM(CASE WHEN r.trestbps < (b.trestbps_q1-1.5*b.trestbps_iqr) OR r.trestbps > (b.trestbps_q3+1.5*b.trestbps_iqr) THEN 1 ELSE 0 END) AS trestbps_iqr_out,
        SUM(CASE WHEN r.chol     < (b.chol_q1-1.5*b.chol_iqr)         OR r.chol     > (b.chol_q3+1.5*b.chol_iqr)         THEN 1 ELSE 0 END) AS chol_iqr_out,
        SUM(CASE WHEN r.thalach  < (b.thalach_q1-1.5*b.thalach_iqr)   OR r.thalach  > (b.thalach_q3+1.5*b.thalach_iqr)   THEN 1 ELSE 0 END) AS thalach_iqr_out,
        SUM(CASE WHEN r.oldpeak  < (b.oldpeak_q1-1.5*b.oldpeak_iqr)   OR r.oldpeak  > (b.oldpeak_q3+1.5*b.oldpeak_iqr)   THEN 1 ELSE 0 END) AS oldpeak_iqr_out
    FROM dbo.raw_flat_data r CROSS JOIN bounds b
    GROUP BY b.trestbps_q1, b.trestbps_q3, b.trestbps_iqr,
             b.chol_q1, b.chol_q3, b.chol_iqr,
             b.thalach_q1, b.thalach_q3, b.thalach_iqr,
             b.oldpeak_q1, b.oldpeak_q3, b.oldpeak_iqr
)
SELECT 'trestbps' AS column_name, 80 AS rule_based_min, 220 AS rule_based_max,
       c.trestbps_rule_out AS rule_outliers_count,
       i.trestbps_low AS iqr_lower_bound, i.trestbps_high AS iqr_upper_bound,
       i.trestbps_iqr_out AS iqr_outliers_count
FROM counts c, iqr_counts i
UNION ALL
SELECT 'chol', 80, 600, c.chol_rule_out, i.chol_low, i.chol_high, i.chol_iqr_out
FROM counts c, iqr_counts i
UNION ALL
SELECT 'thalach', 50, 230, c.thalach_rule_out, i.thalach_low, i.thalach_high, i.thalach_iqr_out
FROM counts c, iqr_counts i
UNION ALL
SELECT 'oldpeak', 0, 10, c.oldpeak_rule_out, i.oldpeak_low, i.oldpeak_high, i.oldpeak_iqr_out
FROM counts c, iqr_counts i
"""

QUERY_DEFAULT_VALUE = """
SELECT
    'trestbps' AS column_name, 120 AS default_value,
    SUM(CASE WHEN trestbps = 120 THEN 1 ELSE 0 END) AS occurrence_count,
    ROUND(100.0 * SUM(CASE WHEN trestbps = 120 THEN 1 ELSE 0 END) / COUNT(*), 2) AS percentage
FROM dbo.raw_flat_data WHERE trestbps IS NOT NULL
UNION ALL
SELECT 'chol', 0, SUM(CASE WHEN chol = 0 THEN 1 ELSE 0 END),
    ROUND(100.0 * SUM(CASE WHEN chol = 0 THEN 1 ELSE 0 END) / COUNT(*), 2)
FROM dbo.raw_flat_data WHERE chol IS NOT NULL
UNION ALL
SELECT 'oldpeak', 0, SUM(CASE WHEN oldpeak = 0 THEN 1 ELSE 0 END),
    ROUND(100.0 * SUM(CASE WHEN oldpeak = 0 THEN 1 ELSE 0 END) / COUNT(*), 2)
FROM dbo.raw_flat_data WHERE oldpeak IS NOT NULL
"""

QUERY_TARGET_DIST = """
SELECT target_variable, value, count, percentage FROM (
    SELECT 'num' AS target_variable,
           CAST(num AS NVARCHAR(10)) AS value,
           COUNT(*) AS count,
           ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
    FROM dbo.raw_flat_data GROUP BY num
    UNION ALL
    SELECT 'target_binary',
           CAST(target_binary AS NVARCHAR(10)),
           COUNT(*),
           ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)
    FROM dbo.raw_flat_data GROUP BY target_binary
) AS q ORDER BY target_variable, value
"""

QUERY_ML_DATASET = "SELECT * FROM dbo.vw_ml_heart_disease_features"

ANALYSIS_QUERIES = {
    "analysis_source_counts.csv": """
        SELECT source_database, COUNT(*) AS total_records
        FROM dbo.encounters GROUP BY source_database ORDER BY source_database;
    """,
    "analysis_target_dist.csv": """
        SELECT target_binary, COUNT(*) AS total_records,
               ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
        FROM dbo.diagnoses GROUP BY target_binary ORDER BY target_binary;
    """,
    "analysis_cp_target.csv": """
        SELECT s.cp, d.target_binary, COUNT(*) AS total_records
        FROM dbo.symptoms AS s JOIN dbo.diagnoses AS d ON s.encounter_id = d.encounter_id
        GROUP BY s.cp, d.target_binary ORDER BY s.cp, d.target_binary;
    """,
    "analysis_avg_metrics.csv": """
        SELECT d.target_binary,
               AVG(CAST(r.trestbps AS FLOAT)) AS avg_resting_bp,
               AVG(CAST(r.chol AS FLOAT)) AS avg_cholesterol,
               AVG(CAST(e.thalach AS FLOAT)) AS avg_max_heart_rate,
               AVG(CAST(e.oldpeak AS FLOAT)) AS avg_oldpeak
        FROM dbo.diagnoses AS d
        JOIN dbo.resting_tests AS r ON d.encounter_id = r.encounter_id
        JOIN dbo.exercise_ecg_tests AS e ON d.encounter_id = e.encounter_id
        GROUP BY d.target_binary ORDER BY d.target_binary;
    """,
    "analysis_chol_outliers.csv": """
        SELECT TOP 20 r.encounter_id, r.chol, d.target_binary, e.oldpeak, e.thalach
        FROM dbo.resting_tests AS r
        JOIN dbo.exercise_ecg_tests AS e ON r.encounter_id = e.encounter_id
        JOIN dbo.diagnoses AS d ON r.encounter_id = d.encounter_id
        WHERE r.chol = 0 OR r.chol > 400 ORDER BY r.chol DESC;
    """,
    "analysis_oldpeak_rank.csv": """
        WITH ranked_oldpeak AS (
            SELECT d.target_binary, e.encounter_id, e.oldpeak,
                   RANK() OVER (PARTITION BY d.target_binary ORDER BY CAST(e.oldpeak AS FLOAT) DESC) AS oldpeak_rank
            FROM dbo.exercise_ecg_tests AS e
            JOIN dbo.diagnoses AS d ON e.encounter_id = d.encounter_id
            WHERE e.oldpeak IS NOT NULL
        )
        SELECT target_binary, encounter_id, oldpeak, oldpeak_rank
        FROM ranked_oldpeak WHERE oldpeak_rank <= 10 ORDER BY target_binary, oldpeak_rank;
    """,
    "analysis_source_vs_overall.csv": """
        WITH source_target AS (
            SELECT e.source_database, COUNT(*) AS total_records,
                   SUM(CASE WHEN d.target_binary = 1 THEN 1 ELSE 0 END) AS positive_records
            FROM dbo.encounters AS e JOIN dbo.diagnoses AS d ON e.encounter_id = d.encounter_id
            GROUP BY e.source_database
        ), overall_rate AS (
            SELECT CAST(SUM(CASE WHEN target_binary = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) AS overall_positive_rate
            FROM dbo.diagnoses
        )
        SELECT s.source_database, s.total_records, s.positive_records,
               ROUND(CAST(s.positive_records AS FLOAT) * 100.0 / s.total_records, 2) AS source_positive_rate,
               ROUND(o.overall_positive_rate * 100.0, 2) AS overall_positive_rate,
               ROUND((CAST(s.positive_records AS FLOAT) / s.total_records - o.overall_positive_rate) * 100.0, 2) AS rate_gap
        FROM source_target AS s CROSS JOIN overall_rate AS o ORDER BY rate_gap DESC;
    """
}

# ────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────

def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("=== 03_preprocessing_cleaning.py: SQL Orchestrator ===\n")

    # 1. Chạy SQL: tách dữ liệu từ staging ra 7 bảng quan hệ
    print("[1/2] Running SQL split (04_split_relational_data.sql)...")
    split_sql = SQL_DIR / "04_split_relational_data.sql"
    with engine.begin() as conn:
        run_sql_file(conn, split_sql)
    print("  => Table splitting completed.\n")

    # 2. Query các báo cáo từ SQL và lưu CSV
    print("[2/2] Querying Data Quality Reports from SQL and saving to CSV...")
    reports = {
        "missing_values_report.csv":    QUERY_MISSING_VALUES,
        "duplicate_report.csv":         QUERY_DUPLICATE,
        "outlier_report.csv":           QUERY_OUTLIER,
        "default_value_check_report.csv": QUERY_DEFAULT_VALUE,
        "target_distribution_report.csv": QUERY_TARGET_DIST,
    }
    for file_name, query in reports.items():
        df = pd.read_sql_query(query, engine)
        write_csv(df, REPORT_DIR / file_name)
        print(f"  Saved: {file_name} ({len(df)} rows)")

    print("\n[3/4] Querying Analysis Queries from SQL and saving to CSV...")
    for file_name, query in ANALYSIS_QUERIES.items():
        df = pd.read_sql_query(query, engine)
        write_csv(df, REPORT_DIR / file_name)
        print(f"  Saved: {file_name} ({len(df)} rows)")

    # 4. Query view ML và lưu CSV cho EDA/ML
    print("\n[4/4] Querying dbo.vw_ml_heart_disease_features...")
    ml_df = pd.read_sql_query(QUERY_ML_DATASET, engine)
    write_csv(ml_df, PROCESSED_DIR / "ml_ready_heart_disease.csv")
    print(f"  Saved: ml_ready_heart_disease.csv ({len(ml_df)} rows)")

    print("\n=== Done! ===")


if __name__ == "__main__":
    main()
