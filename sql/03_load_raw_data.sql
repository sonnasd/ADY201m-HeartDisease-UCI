USE HeartDiseaseClinicalDB;
GO

-- ============================================================
-- 03_import_data.sql
-- Hướng dẫn import dữ liệu vào hệ thống.
-- ============================================================
-- Quy trình import dữ liệu (SQL-first pipeline):
--
--   Bước 1: python src/01_data_profile.py
--           → Đọc 4 file .data từ UCI, tạo flat CSV
--             (data/processed/uci_heart_disease_parsed_flat.csv)
--
--   Bước 2: python src/load_flat_data.py
--           → Nạp flat CSV vào bảng staging dbo.raw_flat_data
--
--   Bước 3: python src/02_preprocessing_cleaning.py
--           → Gọi SQL 03_split_relational_data.sql để tách 7 bảng
--           → Query báo cáo chất lượng dữ liệu từ SQL, lưu CSV
--           → Query vw_ml_heart_disease_features, lưu ml_ready_heart_disease.csv
--
-- Kiểm tra row count sau khi import:
SELECT 'raw_flat_data'       AS table_name, COUNT(*) AS total_rows FROM dbo.raw_flat_data
UNION ALL SELECT 'patients',           COUNT(*) FROM dbo.patients
UNION ALL SELECT 'encounters',         COUNT(*) FROM dbo.encounters
UNION ALL SELECT 'symptoms',           COUNT(*) FROM dbo.symptoms
UNION ALL SELECT 'risk_history',       COUNT(*) FROM dbo.risk_history
UNION ALL SELECT 'resting_tests',      COUNT(*) FROM dbo.resting_tests
UNION ALL SELECT 'exercise_ecg_tests', COUNT(*) FROM dbo.exercise_ecg_tests
UNION ALL SELECT 'diagnoses',          COUNT(*) FROM dbo.diagnoses;
GO
