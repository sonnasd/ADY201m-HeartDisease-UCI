USE HeartDiseaseClinicalDB;
GO

IF OBJECT_ID(N'dbo.diagnoses', N'U') IS NOT NULL DROP TABLE dbo.diagnoses;
IF OBJECT_ID(N'dbo.exercise_ecg_tests', N'U') IS NOT NULL DROP TABLE dbo.exercise_ecg_tests;
IF OBJECT_ID(N'dbo.resting_tests', N'U') IS NOT NULL DROP TABLE dbo.resting_tests;
IF OBJECT_ID(N'dbo.risk_history', N'U') IS NOT NULL DROP TABLE dbo.risk_history;
IF OBJECT_ID(N'dbo.symptoms', N'U') IS NOT NULL DROP TABLE dbo.symptoms;
IF OBJECT_ID(N'dbo.encounters', N'U') IS NOT NULL DROP TABLE dbo.encounters;
IF OBJECT_ID(N'dbo.patients', N'U') IS NOT NULL DROP TABLE dbo.patients;
IF OBJECT_ID(N'dbo.raw_flat_data', N'U') IS NOT NULL DROP TABLE dbo.raw_flat_data;
GO

-- Bảng staging: nhận dữ liệu flat CSV từ Python (01_data_profile.py output).
-- Toàn bộ việc tách bảng quan hệ, làm sạch và feature engineering đều được thực hiện bởi SQL từ bảng này.
CREATE TABLE dbo.raw_flat_data (
    global_record_number INT NOT NULL,
    patient_id           NVARCHAR(20) NOT NULL,
    encounter_id         NVARCHAR(20) NOT NULL,
    age                  FLOAT NULL,
    sex                  FLOAT NULL,
    cp                   FLOAT NULL,
    trestbps             FLOAT NULL,
    chol                 FLOAT NULL,
    fbs                  FLOAT NULL,
    restecg              FLOAT NULL,
    thalach              FLOAT NULL,
    exang                FLOAT NULL,
    oldpeak              FLOAT NULL,
    slope                FLOAT NULL,
    ca                   FLOAT NULL,
    thal                 FLOAT NULL,
    num                  FLOAT NULL,
    target_binary        FLOAT NULL,
    source_database      NVARCHAR(50) NOT NULL,
    source_row_number    INT NOT NULL,
    CONSTRAINT PK_raw_flat_data PRIMARY KEY (global_record_number)
);
GO


CREATE TABLE dbo.patients (
    patient_id NVARCHAR(20) NOT NULL PRIMARY KEY,
    age FLOAT NULL,
    sex FLOAT NULL,
    source_database NVARCHAR(50) NOT NULL,
    source_row_number INT NOT NULL
);

CREATE TABLE dbo.encounters (
    encounter_id NVARCHAR(20) NOT NULL PRIMARY KEY,
    patient_id NVARCHAR(20) NOT NULL,
    source_database NVARCHAR(50) NOT NULL,
    source_row_number INT NOT NULL,
    CONSTRAINT FK_encounters_patients FOREIGN KEY (patient_id) REFERENCES dbo.patients(patient_id)
);

CREATE TABLE dbo.symptoms (
    symptom_id NVARCHAR(20) NOT NULL PRIMARY KEY,
    encounter_id NVARCHAR(20) NOT NULL,
    cp FLOAT NULL,
    CONSTRAINT FK_symptoms_encounters FOREIGN KEY (encounter_id) REFERENCES dbo.encounters(encounter_id)
);

CREATE TABLE dbo.risk_history (
    risk_id NVARCHAR(20) NOT NULL PRIMARY KEY,
    encounter_id NVARCHAR(20) NOT NULL,
    fbs FLOAT NULL,
    CONSTRAINT FK_risk_history_encounters FOREIGN KEY (encounter_id) REFERENCES dbo.encounters(encounter_id)
);

CREATE TABLE dbo.resting_tests (
    resting_test_id NVARCHAR(20) NOT NULL PRIMARY KEY,
    encounter_id NVARCHAR(20) NOT NULL,
    trestbps FLOAT NULL,
    chol FLOAT NULL,
    restecg FLOAT NULL,
    CONSTRAINT FK_resting_tests_encounters FOREIGN KEY (encounter_id) REFERENCES dbo.encounters(encounter_id)
);

CREATE TABLE dbo.exercise_ecg_tests (
    exercise_test_id NVARCHAR(20) NOT NULL PRIMARY KEY,
    encounter_id NVARCHAR(20) NOT NULL,
    thalach FLOAT NULL,
    exang FLOAT NULL,
    oldpeak FLOAT NULL,
    slope FLOAT NULL,
    CONSTRAINT FK_exercise_ecg_tests_encounters FOREIGN KEY (encounter_id) REFERENCES dbo.encounters(encounter_id)
);

CREATE TABLE dbo.diagnoses (
    diagnosis_id NVARCHAR(20) NOT NULL PRIMARY KEY,
    encounter_id NVARCHAR(20) NOT NULL,
    ca FLOAT NULL,
    thal FLOAT NULL,
    num FLOAT NULL,
    target_binary FLOAT NULL,
    CONSTRAINT FK_diagnoses_encounters FOREIGN KEY (encounter_id) REFERENCES dbo.encounters(encounter_id)
);
GO
