# Data Dictionary - Heart Disease UCI Relational Dataset

## 1. Bảng `patients`

| Cột | Kiểu gợi ý SQL Server | Mô tả |
|---|---|---|
| `patient_id` | `NVARCHAR(20)` | Mã bệnh nhân ẩn danh, khóa chính. |
| `age` | `FLOAT` | Tuổi bệnh nhân tại thời điểm ghi nhận. |
| `sex` | `FLOAT` | Giới tính mã hóa từ bộ dữ liệu UCI (`1` = nam, `0` = nữ). |
| `source_database` | `NVARCHAR(50)` | Nguồn bản ghi: `cleveland`, `hungarian`, `switzerland`, `va_long_beach`. |
| `source_row_number` | `INT` | Số thứ tự dòng trong file nguồn. |

## 2. Bảng `encounters`

| Cột | Kiểu gợi ý SQL Server | Mô tả |
|---|---|---|
| `encounter_id` | `NVARCHAR(20)` | Mã lượt ghi nhận/khám, khóa chính. |
| `patient_id` | `NVARCHAR(20)` | Khóa ngoại liên kết sang `patients`. |
| `source_database` | `NVARCHAR(50)` | Nguồn dữ liệu của lượt ghi nhận. |
| `source_row_number` | `INT` | Vị trí record trong file processed nguồn. |

## 3. Bảng `symptoms`

| Cột | Kiểu gợi ý SQL Server | Mô tả |
|---|---|---|
| `symptom_id` | `NVARCHAR(20)` | Mã bản ghi triệu chứng, khóa chính. |
| `encounter_id` | `NVARCHAR(20)` | Khóa ngoại sang `encounters`. |
| `cp` | `FLOAT` | Chest pain type: mã loại đau ngực. |

## 4. Bảng `risk_history`

| Cột | Kiểu gợi ý SQL Server | Mô tả |
|---|---|---|
| `risk_id` | `NVARCHAR(20)` | Mã bản ghi yếu tố nguy cơ, khóa chính. |
| `encounter_id` | `NVARCHAR(20)` | Khóa ngoại sang `encounters`. |
| `fbs` | `FLOAT` | Fasting blood sugar vượt ngưỡng (`1`/`0` theo mã hóa UCI). |

## 5. Bảng `resting_tests`

| Cột | Kiểu gợi ý SQL Server | Mô tả |
|---|---|---|
| `resting_test_id` | `NVARCHAR(20)` | Mã bản ghi xét nghiệm/chỉ số nghỉ, khóa chính. |
| `encounter_id` | `NVARCHAR(20)` | Khóa ngoại sang `encounters`. |
| `trestbps` | `FLOAT` | Huyết áp tâm thu lúc nghỉ. |
| `chol` | `FLOAT` | Total cholesterol. Giá trị `0` thường được xem là thiếu/không hợp lệ trong EDA. |
| `restecg` | `FLOAT` | Resting ECG result code. |

## 6. Bảng `exercise_ecg_tests`

| Cột | Kiểu gợi ý SQL Server | Mô tả |
|---|---|---|
| `exercise_test_id` | `NVARCHAR(20)` | Mã bài test gắng sức/ECG, khóa chính. |
| `encounter_id` | `NVARCHAR(20)` | Khóa ngoại sang `encounters`. |
| `thalach` | `FLOAT` | Nhịp tim tối đa đạt được. |
| `exang` | `FLOAT` | Có/không đau thắt ngực do gắng sức (`1`/`0`). |
| `oldpeak` | `FLOAT` | ST depression induced by exercise relative to rest. |
| `slope` | `FLOAT` | Slope of the peak exercise ST segment. |

## 7. Bảng `diagnoses`

| Cột | Kiểu gợi ý SQL Server | Mô tả |
|---|---|---|
| `diagnosis_id` | `NVARCHAR(20)` | Mã nhãn chẩn đoán, khóa chính. |
| `encounter_id` | `NVARCHAR(20)` | Khóa ngoại sang `encounters`. |
| `ca` | `FLOAT` | Number of major vessels colored by fluoroscopy. |
| `thal` | `FLOAT` | Thalassemia/stress-related encoded result. |
| `num` | `FLOAT` | Nhãn gốc UCI từ `0` đến `4`. |
| `target_binary` | `FLOAT` | Nhãn nhị phân: `0` nếu `num = 0`, `1` nếu `num > 0`. |

## 8. Cột feature engineering trong `ml_ready_heart_disease.csv`

| Cột | Mô tả |
|---|---|
| `age_group` | Nhóm tuổi: `<40`, `40-49`, `50-59`, `60+`. |
| `cholesterol_category` | Phân loại cholesterol: `low_or_unknown`, `normal`, `borderline_high`, `high`. |
| `st_abnormal_flag` | Cờ bất thường ST/ECG: `1` nếu `oldpeak > 1.0` hoặc `slope` thuộc `{2, 3}`. |
| `chol_missing_flag` | `1` nếu `chol` thiếu, ngược lại `0`. |
| `trestbps_missing_flag` | `1` nếu `trestbps` thiếu. |
| `thalach_missing_flag` | `1` nếu `thalach` thiếu. |
| `oldpeak_missing_flag` | `1` nếu `oldpeak` thiếu. |
