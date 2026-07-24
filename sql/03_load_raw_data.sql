USE HeartDiseaseClinicalDB;
GO

-- 03_load_raw_data.sql: Verify Data Import
SELECT 'raw_flat_data'       AS table_name, COUNT(*) AS total_rows FROM dbo.raw_flat_data
UNION ALL SELECT 'patients',           COUNT(*) FROM dbo.patients
UNION ALL SELECT 'encounters',         COUNT(*) FROM dbo.encounters
UNION ALL SELECT 'symptoms',           COUNT(*) FROM dbo.symptoms
UNION ALL SELECT 'risk_history',       COUNT(*) FROM dbo.risk_history
UNION ALL SELECT 'resting_tests',      COUNT(*) FROM dbo.resting_tests
UNION ALL SELECT 'exercise_ecg_tests', COUNT(*) FROM dbo.exercise_ecg_tests
UNION ALL SELECT 'diagnoses',          COUNT(*) FROM dbo.diagnoses;
GO
