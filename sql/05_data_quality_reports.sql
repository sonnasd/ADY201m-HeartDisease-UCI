USE HeartDiseaseClinicalDB;
GO

-- ============================================================
-- 05_data_quality_reports.sql
-- Mục đích: Tính toán các báo cáo chất lượng dữ liệu bằng SQL
--           thuần túy từ 7 bảng quan hệ và bảng staging.
-- Kết quả được Python (02_preprocessing_cleaning.py) query và
-- lưu ra CSV để Dashboard đọc.
-- ============================================================


-- ============================================================
-- REPORT 1: Missing Values Report
-- Đếm NULL trong mỗi cột của từng bảng quan hệ.
-- Output columns: table_name, column_name, missing_count, missing_pct
-- ============================================================
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
UNION ALL SELECT 'diagnoses',    'target_binary',  SUM(CASE WHEN target_binary IS NULL THEN 1 ELSE 0 END), ROUND(100.0 * SUM(CASE WHEN target_binary IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) FROM dbo.diagnoses;
GO


-- ============================================================
-- REPORT 2: Duplicate Report
-- Kiểm tra duplicate dựa trên cột data (loại trừ cột ID).
-- Output columns: table_name, full_duplicate_rows, duplicate_rows_excluding_id
-- ============================================================
SELECT
    'patients' AS table_name,
    SUM(cnt - 1) AS full_duplicate_rows,
    SUM(data_cnt - 1) AS duplicate_rows_excluding_id
FROM (
    SELECT COUNT(*) AS cnt, COUNT(*) AS data_cnt
    FROM dbo.patients
    GROUP BY age, sex, source_database, source_row_number
    HAVING COUNT(*) > 1
) t
UNION ALL
SELECT
    'symptoms',
    SUM(cnt - 1),
    SUM(data_cnt - 1)
FROM (
    SELECT COUNT(*) AS cnt, COUNT(*) AS data_cnt
    FROM dbo.symptoms
    GROUP BY encounter_id, cp
    HAVING COUNT(*) > 1
) t
UNION ALL
SELECT
    'risk_history',
    SUM(cnt - 1),
    SUM(data_cnt - 1)
FROM (
    SELECT COUNT(*) AS cnt, COUNT(*) AS data_cnt
    FROM dbo.risk_history
    GROUP BY encounter_id, fbs
    HAVING COUNT(*) > 1
) t
UNION ALL
SELECT
    'resting_tests',
    SUM(cnt - 1),
    SUM(data_cnt - 1)
FROM (
    SELECT COUNT(*) AS cnt, COUNT(*) AS data_cnt
    FROM dbo.resting_tests
    GROUP BY encounter_id, trestbps, chol, restecg
    HAVING COUNT(*) > 1
) t
UNION ALL
SELECT
    'exercise_ecg_tests',
    SUM(cnt - 1),
    SUM(data_cnt - 1)
FROM (
    SELECT COUNT(*) AS cnt, COUNT(*) AS data_cnt
    FROM dbo.exercise_ecg_tests
    GROUP BY encounter_id, thalach, exang, oldpeak, slope
    HAVING COUNT(*) > 1
) t
UNION ALL
SELECT
    'diagnoses',
    SUM(cnt - 1),
    SUM(data_cnt - 1)
FROM (
    SELECT COUNT(*) AS cnt, COUNT(*) AS data_cnt
    FROM dbo.diagnoses
    GROUP BY encounter_id, ca, thal, num, target_binary
    HAVING COUNT(*) > 1
) t;
GO


-- ============================================================
-- REPORT 3: Outlier Report (IQR + Rule-based)
-- Tính Q1, Q3, IQR bằng PERCENTILE_CONT (Window Function).
-- Output columns: column_name, rule_based_min, rule_based_max,
--                 rule_outliers_count, iqr_lower_bound,
--                 iqr_upper_bound, iqr_outliers_count
-- ============================================================
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
        chol_q1,     chol_q3,     (chol_q3 - chol_q1)         AS chol_iqr,
        thalach_q1,  thalach_q3,  (thalach_q3 - thalach_q1)   AS thalach_iqr,
        oldpeak_q1,  oldpeak_q3,  (oldpeak_q3 - oldpeak_q1)   AS oldpeak_iqr
    FROM percentiles
),
counts AS (
    SELECT
        SUM(CASE WHEN trestbps < 80  OR trestbps > 220  THEN 1 ELSE 0 END) AS trestbps_rule_out,
        SUM(CASE WHEN chol     < 80  OR chol     > 600  THEN 1 ELSE 0 END) AS chol_rule_out,
        SUM(CASE WHEN thalach  < 50  OR thalach  > 230  THEN 1 ELSE 0 END) AS thalach_rule_out,
        SUM(CASE WHEN oldpeak  < 0   OR oldpeak  > 10   THEN 1 ELSE 0 END) AS oldpeak_rule_out
    FROM dbo.raw_flat_data
    WHERE trestbps IS NOT NULL OR chol IS NOT NULL OR thalach IS NOT NULL OR oldpeak IS NOT NULL
),
iqr_counts AS (
    SELECT
        b.trestbps_q1 - 1.5 * b.trestbps_iqr AS trestbps_low,
        b.trestbps_q3 + 1.5 * b.trestbps_iqr AS trestbps_high,
        b.chol_q1     - 1.5 * b.chol_iqr     AS chol_low,
        b.chol_q3     + 1.5 * b.chol_iqr     AS chol_high,
        b.thalach_q1  - 1.5 * b.thalach_iqr  AS thalach_low,
        b.thalach_q3  + 1.5 * b.thalach_iqr  AS thalach_high,
        b.oldpeak_q1  - 1.5 * b.oldpeak_iqr  AS oldpeak_low,
        b.oldpeak_q3  + 1.5 * b.oldpeak_iqr  AS oldpeak_high,
        SUM(CASE WHEN r.trestbps < (b.trestbps_q1 - 1.5*b.trestbps_iqr) OR r.trestbps > (b.trestbps_q3 + 1.5*b.trestbps_iqr) THEN 1 ELSE 0 END) AS trestbps_iqr_out,
        SUM(CASE WHEN r.chol     < (b.chol_q1     - 1.5*b.chol_iqr)     OR r.chol     > (b.chol_q3     + 1.5*b.chol_iqr)     THEN 1 ELSE 0 END) AS chol_iqr_out,
        SUM(CASE WHEN r.thalach  < (b.thalach_q1  - 1.5*b.thalach_iqr)  OR r.thalach  > (b.thalach_q3  + 1.5*b.thalach_iqr)  THEN 1 ELSE 0 END) AS thalach_iqr_out,
        SUM(CASE WHEN r.oldpeak  < (b.oldpeak_q1  - 1.5*b.oldpeak_iqr)  OR r.oldpeak  > (b.oldpeak_q3  + 1.5*b.oldpeak_iqr)  THEN 1 ELSE 0 END) AS oldpeak_iqr_out
    FROM dbo.raw_flat_data r
    CROSS JOIN bounds b
    GROUP BY b.trestbps_q1, b.trestbps_q3, b.trestbps_iqr,
             b.chol_q1, b.chol_q3, b.chol_iqr,
             b.thalach_q1, b.thalach_q3, b.thalach_iqr,
             b.oldpeak_q1, b.oldpeak_q3, b.oldpeak_iqr
)
SELECT
    'trestbps' AS column_name, 80 AS rule_based_min, 220 AS rule_based_max,
    c.trestbps_rule_out AS rule_outliers_count,
    ROUND(i.trestbps_low, 2) AS iqr_lower_bound, ROUND(i.trestbps_high, 2) AS iqr_upper_bound,
    i.trestbps_iqr_out AS iqr_outliers_count
FROM counts c, iqr_counts i
UNION ALL
SELECT 'chol', 80, 600, c.chol_rule_out,
    ROUND(i.chol_low, 2), ROUND(i.chol_high, 2), i.chol_iqr_out
FROM counts c, iqr_counts i
UNION ALL
SELECT 'thalach', 50, 230, c.thalach_rule_out,
    ROUND(i.thalach_low, 2), ROUND(i.thalach_high, 2), i.thalach_iqr_out
FROM counts c, iqr_counts i
UNION ALL
SELECT 'oldpeak', 0, 10, c.oldpeak_rule_out,
    ROUND(i.oldpeak_low, 2), ROUND(i.oldpeak_high, 2), i.oldpeak_iqr_out
FROM counts c, iqr_counts i;
GO


-- ============================================================
-- REPORT 4: Default Value Check Report
-- Đếm giá trị mặc định đáng ngờ (chol=0, trestbps=120, oldpeak=0).
-- Output columns: column_name, default_value, occurrence_count, percentage
-- ============================================================
SELECT
    'trestbps' AS column_name,
    120        AS default_value,
    SUM(CASE WHEN trestbps = 120 THEN 1 ELSE 0 END) AS occurrence_count,
    ROUND(100.0 * SUM(CASE WHEN trestbps = 120 THEN 1 ELSE 0 END) / COUNT(*), 2) AS percentage
FROM dbo.raw_flat_data WHERE trestbps IS NOT NULL
UNION ALL
SELECT
    'chol', 0,
    SUM(CASE WHEN chol = 0 THEN 1 ELSE 0 END),
    ROUND(100.0 * SUM(CASE WHEN chol = 0 THEN 1 ELSE 0 END) / COUNT(*), 2)
FROM dbo.raw_flat_data WHERE chol IS NOT NULL
UNION ALL
SELECT
    'oldpeak', 0,
    SUM(CASE WHEN oldpeak = 0 THEN 1 ELSE 0 END),
    ROUND(100.0 * SUM(CASE WHEN oldpeak = 0 THEN 1 ELSE 0 END) / COUNT(*), 2)
FROM dbo.raw_flat_data WHERE oldpeak IS NOT NULL;
GO


-- ============================================================
-- REPORT 5: Target Distribution Report
-- Phân bố của num và target_binary.
-- Output columns: target_variable, value, count, percentage
-- ============================================================
SELECT
    'num'   AS target_variable,
    CAST(num AS NVARCHAR(10)) AS value,
    COUNT(*) AS count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM dbo.raw_flat_data
GROUP BY num
UNION ALL
SELECT
    'target_binary',
    CAST(target_binary AS NVARCHAR(10)),
    COUNT(*),
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)
FROM dbo.raw_flat_data
GROUP BY target_binary
ORDER BY target_variable, value;
GO
