USE HeartDiseaseClinicalDB;
GO

-- ============================================================
-- 04_split_relational_data.sql
-- Mục đích: Tách dữ liệu từ bảng staging dbo.raw_flat_data
--           ra 7 bảng quan hệ. Script này thay thế hoàn toàn
--           việc split bảng bằng Python (Pandas).
-- Chạy sau khi: Python load_flat_data.py đã nạp raw_flat_data.
-- ============================================================

-- Xóa dữ liệu cũ (theo thứ tự FK)
DELETE FROM dbo.diagnoses;
DELETE FROM dbo.exercise_ecg_tests;
DELETE FROM dbo.resting_tests;
DELETE FROM dbo.risk_history;
DELETE FROM dbo.symptoms;
DELETE FROM dbo.encounters;
DELETE FROM dbo.patients;
GO

-- 1. Bảng patients
INSERT INTO dbo.patients (patient_id, age, sex, source_database, source_row_number)
SELECT
    patient_id,
    age,
    sex,
    source_database,
    source_row_number
FROM dbo.raw_flat_data;
GO

-- 2. Bảng encounters
INSERT INTO dbo.encounters (encounter_id, patient_id, source_database, source_row_number)
SELECT
    encounter_id,
    patient_id,
    source_database,
    source_row_number
FROM dbo.raw_flat_data;
GO

-- 3. Bảng symptoms
-- Sinh symptom_id dạng S00001 bằng ROW_NUMBER + FORMAT
INSERT INTO dbo.symptoms (symptom_id, encounter_id, cp)
SELECT
    'S' + FORMAT(ROW_NUMBER() OVER (ORDER BY global_record_number), '00000') AS symptom_id,
    encounter_id,
    cp
FROM dbo.raw_flat_data;
GO

-- 4. Bảng risk_history
INSERT INTO dbo.risk_history (risk_id, encounter_id, fbs)
SELECT
    'R' + FORMAT(ROW_NUMBER() OVER (ORDER BY global_record_number), '00000') AS risk_id,
    encounter_id,
    fbs
FROM dbo.raw_flat_data;
GO

-- 5. Bảng resting_tests
INSERT INTO dbo.resting_tests (resting_test_id, encounter_id, trestbps, chol, restecg)
SELECT
    'RT' + FORMAT(ROW_NUMBER() OVER (ORDER BY global_record_number), '00000') AS resting_test_id,
    encounter_id,
    trestbps,
    chol,
    restecg
FROM dbo.raw_flat_data;
GO

-- 6. Bảng exercise_ecg_tests
INSERT INTO dbo.exercise_ecg_tests (exercise_test_id, encounter_id, thalach, exang, oldpeak, slope)
SELECT
    'EX' + FORMAT(ROW_NUMBER() OVER (ORDER BY global_record_number), '00000') AS exercise_test_id,
    encounter_id,
    thalach,
    exang,
    oldpeak,
    slope
FROM dbo.raw_flat_data;
GO

-- 7. Bảng diagnoses
INSERT INTO dbo.diagnoses (diagnosis_id, encounter_id, ca, thal, num, target_binary)
SELECT
    'D' + FORMAT(ROW_NUMBER() OVER (ORDER BY global_record_number), '00000') AS diagnosis_id,
    encounter_id,
    ca,
    thal,
    num,
    target_binary
FROM dbo.raw_flat_data;
GO

-- Kiểm tra row count sau khi split
SELECT 'patients'           AS table_name, COUNT(*) AS total_rows FROM dbo.patients
UNION ALL SELECT 'encounters',          COUNT(*) FROM dbo.encounters
UNION ALL SELECT 'symptoms',            COUNT(*) FROM dbo.symptoms
UNION ALL SELECT 'risk_history',        COUNT(*) FROM dbo.risk_history
UNION ALL SELECT 'resting_tests',       COUNT(*) FROM dbo.resting_tests
UNION ALL SELECT 'exercise_ecg_tests',  COUNT(*) FROM dbo.exercise_ecg_tests
UNION ALL SELECT 'diagnoses',           COUNT(*) FROM dbo.diagnoses;
GO
