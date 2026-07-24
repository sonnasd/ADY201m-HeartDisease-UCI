USE HeartDiseaseClinicalDB;
GO

-- Query 1: Số record theo source_database.
SELECT
    source_database,
    COUNT(*) AS total_records
FROM dbo.encounters
GROUP BY source_database
ORDER BY source_database;

-- Query 2: Phân bố target_binary.
SELECT
    target_binary,
    COUNT(*) AS total_records,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM dbo.diagnoses
GROUP BY target_binary
ORDER BY target_binary;

-- Query 3: Chest pain type theo target.
SELECT
    s.cp,
    d.target_binary,
    COUNT(*) AS total_records
FROM dbo.symptoms AS s
JOIN dbo.diagnoses AS d ON s.encounter_id = d.encounter_id
GROUP BY s.cp, d.target_binary
ORDER BY s.cp, d.target_binary;

-- Query 4: Chỉ số trung bình theo target.
SELECT
    d.target_binary,
    AVG(CAST(r.trestbps AS FLOAT)) AS avg_resting_bp,
    AVG(CAST(r.chol AS FLOAT)) AS avg_cholesterol,
    AVG(CAST(e.thalach AS FLOAT)) AS avg_max_heart_rate,
    AVG(CAST(e.oldpeak AS FLOAT)) AS avg_oldpeak
FROM dbo.diagnoses AS d
JOIN dbo.resting_tests AS r ON d.encounter_id = r.encounter_id
JOIN dbo.exercise_ecg_tests AS e ON d.encounter_id = e.encounter_id
GROUP BY d.target_binary
ORDER BY d.target_binary;

-- Query 5: Top outliers theo cholesterol.
-- chol = 0 có thể là giá trị default/missing được mã hóa; chol > 400 là mức cao cần review.
SELECT TOP 20
    r.encounter_id,
    r.chol,
    d.target_binary,
    e.oldpeak,
    e.thalach
FROM dbo.resting_tests AS r
JOIN dbo.exercise_ecg_tests AS e ON r.encounter_id = e.encounter_id
JOIN dbo.diagnoses AS d ON r.encounter_id = d.encounter_id
WHERE r.chol = 0 OR r.chol > 400
ORDER BY r.chol DESC;

-- Query 6: Window function xếp hạng oldpeak trong từng nhóm target.
-- Chỉ hiển thị top 10 mỗi nhóm để dễ chụp screenshot và nhận xét.
WITH ranked_oldpeak AS (
    SELECT
        d.target_binary,
        e.encounter_id,
        e.oldpeak,
        RANK() OVER (PARTITION BY d.target_binary ORDER BY CAST(e.oldpeak AS FLOAT) DESC) AS oldpeak_rank
    FROM dbo.exercise_ecg_tests AS e
    JOIN dbo.diagnoses AS d ON e.encounter_id = d.encounter_id
    WHERE e.oldpeak IS NOT NULL
)
SELECT
    target_binary,
    encounter_id,
    oldpeak,
    oldpeak_rank
FROM ranked_oldpeak
WHERE oldpeak_rank <= 10
ORDER BY target_binary, oldpeak_rank;

-- Query 7: CTE/subquery so sánh tỷ lệ target=1 theo source với tỷ lệ chung.
WITH source_target AS (
    SELECT
        e.source_database,
        COUNT(*) AS total_records,
        SUM(CASE WHEN d.target_binary = 1 THEN 1 ELSE 0 END) AS positive_records
    FROM dbo.encounters AS e
    JOIN dbo.diagnoses AS d ON e.encounter_id = d.encounter_id
    GROUP BY e.source_database
), overall_rate AS (
    SELECT
        CAST(SUM(CASE WHEN target_binary = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) AS overall_positive_rate
    FROM dbo.diagnoses
)
SELECT
    s.source_database,
    s.total_records,
    s.positive_records,
    ROUND(CAST(s.positive_records AS FLOAT) * 100.0 / s.total_records, 2) AS source_positive_rate,
    ROUND(o.overall_positive_rate * 100.0, 2) AS overall_positive_rate,
    ROUND((CAST(s.positive_records AS FLOAT) / s.total_records - o.overall_positive_rate) * 100.0, 2) AS rate_gap
FROM source_target AS s
CROSS JOIN overall_rate AS o
ORDER BY rate_gap DESC;
GO
