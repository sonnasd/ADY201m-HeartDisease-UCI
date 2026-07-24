USE HeartDiseaseClinicalDB;
GO

-- 07_create_ml_view.sql: Create ML-Ready View
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
    NULLIF(rt.chol, 0) AS chol,
    rt.restecg,
    ex.thalach,
    ex.exang,
    ex.oldpeak,
    ex.slope,
    d.ca,
    d.thal,
    d.num,
    d.target_binary,
    CASE 
        WHEN p.age IS NULL THEN NULL
        WHEN p.age < 40 THEN '<40'
        WHEN p.age < 50 THEN '40-49'
        WHEN p.age < 60 THEN '50-59'
        ELSE '60+' 
    END AS age_group,
    CASE
        WHEN NULLIF(rt.chol, 0) IS NULL THEN 'low_or_unknown'
        WHEN NULLIF(rt.chol, 0) < 200 THEN 'normal'
        WHEN NULLIF(rt.chol, 0) < 240 THEN 'borderline_high'
        ELSE 'high'
    END AS cholesterol_category,
    CASE 
        WHEN ex.oldpeak IS NULL AND ex.slope IS NULL THEN NULL
        WHEN ex.oldpeak > 1.0 OR ex.slope IN (2, 3) THEN 1
        ELSE 0
    END AS st_abnormal_flag,
    CASE WHEN NULLIF(rt.chol, 0) IS NULL THEN 1 ELSE 0 END AS chol_missing_flag,
    CASE WHEN rt.trestbps IS NULL THEN 1 ELSE 0 END AS trestbps_missing_flag,
    CASE WHEN ex.thalach IS NULL THEN 1 ELSE 0 END AS thalach_missing_flag,
    CASE WHEN ex.oldpeak IS NULL THEN 1 ELSE 0 END AS oldpeak_missing_flag
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
