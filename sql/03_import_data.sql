USE HeartDiseaseClinicalDB;
GO

-- Cach import khuyen nghi: chay Python loader de xu ly CSV/NaN on dinh hon BULK INSERT.
-- Lenh: python src/load_relational_data.py
-- File nay giu checklist import cho phan SQL trong bao cao.

SELECT 'patients.csv' AS csv_file, 'dbo.patients' AS target_table
UNION ALL SELECT 'encounters.csv', 'dbo.encounters'
UNION ALL SELECT 'symptoms.csv', 'dbo.symptoms'
UNION ALL SELECT 'risk_history.csv', 'dbo.risk_history'
UNION ALL SELECT 'resting_tests.csv', 'dbo.resting_tests'
UNION ALL SELECT 'exercise_ecg_tests.csv', 'dbo.exercise_ecg_tests'
UNION ALL SELECT 'diagnoses.csv', 'dbo.diagnoses';
GO
