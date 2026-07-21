USE HeartDiseaseClinicalDB;
GO

-- Data Quality Check 1: Kiểm tra row count của 7 bảng quan hệ.
-- Kỳ vọng: mỗi bảng có 920 dòng sau khi import CSV.
SELECT 'patients' AS table_name, COUNT(*) AS total_rows FROM dbo.patients
UNION ALL SELECT 'encounters', COUNT(*) FROM dbo.encounters
UNION ALL SELECT 'symptoms', COUNT(*) FROM dbo.symptoms
UNION ALL SELECT 'risk_history', COUNT(*) FROM dbo.risk_history
UNION ALL SELECT 'resting_tests', COUNT(*) FROM dbo.resting_tests
UNION ALL SELECT 'exercise_ecg_tests', COUNT(*) FROM dbo.exercise_ecg_tests
UNION ALL SELECT 'diagnoses', COUNT(*) FROM dbo.diagnoses;

-- Data Quality Check 2: Kiểm tra missing values ở các cột chính.
SELECT 'risk_history.fbs' AS column_name, COUNT(*) AS missing_count FROM dbo.risk_history WHERE fbs IS NULL
UNION ALL SELECT 'resting_tests.trestbps', COUNT(*) FROM dbo.resting_tests WHERE trestbps IS NULL
UNION ALL SELECT 'resting_tests.chol', COUNT(*) FROM dbo.resting_tests WHERE chol IS NULL
UNION ALL SELECT 'exercise_ecg_tests.thalach', COUNT(*) FROM dbo.exercise_ecg_tests WHERE thalach IS NULL
UNION ALL SELECT 'exercise_ecg_tests.oldpeak', COUNT(*) FROM dbo.exercise_ecg_tests WHERE oldpeak IS NULL
UNION ALL SELECT 'diagnoses.ca', COUNT(*) FROM dbo.diagnoses WHERE ca IS NULL
UNION ALL SELECT 'diagnoses.thal', COUNT(*) FROM dbo.diagnoses WHERE thal IS NULL;

-- Data Quality Check 3: Kiểm tra duplicate theo patient_id.
SELECT patient_id, COUNT(*) AS duplicate_count
FROM dbo.patients
GROUP BY patient_id
HAVING COUNT(*) > 1;

-- Data Quality Check 4: Kiểm tra duplicate theo encounter_id.
SELECT encounter_id, COUNT(*) AS duplicate_count
FROM dbo.encounters
GROUP BY encounter_id
HAVING COUNT(*) > 1;
GO
