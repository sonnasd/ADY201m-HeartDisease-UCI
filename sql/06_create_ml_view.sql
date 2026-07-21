USE HeartDiseaseClinicalDB;
GO

-- SQL View: Tạo ML-ready view từ 7 bảng quan hệ.
-- Lưu ý: num và target_binary được giữ trong view để đối chiếu nhãn,
-- nhưng num không được dùng làm input feature khi train model để tránh data leakage.
CREATE OR ALTER VIEW dbo.vw_ml_heart_disease_features AS
SELECT
    e.encounter_id,
    e.patient_id,
    e.source_database,
    e.source_row_number,
    p.age,
    p.sex,
    s.cp,
    rh.fbs,
    rt.trestbps,
    rt.chol,
    rt.restecg,
    ex.thalach,
    ex.exang,
    ex.oldpeak,
    ex.slope,
    d.ca,
    d.thal,
    d.num,
    d.target_binary
FROM dbo.encounters AS e
JOIN dbo.patients AS p ON e.patient_id = p.patient_id
LEFT JOIN dbo.symptoms AS s ON e.encounter_id = s.encounter_id
LEFT JOIN dbo.risk_history AS rh ON e.encounter_id = rh.encounter_id
LEFT JOIN dbo.resting_tests AS rt ON e.encounter_id = rt.encounter_id
LEFT JOIN dbo.exercise_ecg_tests AS ex ON e.encounter_id = ex.encounter_id
LEFT JOIN dbo.diagnoses AS d ON e.encounter_id = d.encounter_id;
GO

SELECT TOP 20 * FROM dbo.vw_ml_heart_disease_features;
GO
