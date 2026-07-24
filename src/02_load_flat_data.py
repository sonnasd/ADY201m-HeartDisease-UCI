"""
load_flat_data.py
-----------------
Nhiệm vụ duy nhất của script này là đọc file CSV flat được tạo bởi
01_data_profile.py và nạp nó vào bảng staging dbo.raw_flat_data trên
SQL Server. Toàn bộ quá trình làm sạch, tách bảng và feature engineering
đều được thực hiện bởi SQL (04_split_relational_data.sql và 07_create_ml_view.sql).
"""
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
FLAT_CSV = BASE_DIR / "data" / "processed" / "uci_heart_disease_parsed_flat.csv"

server             = os.getenv("DB_SERVER", "localhost")
database           = os.getenv("DB_NAME", "HeartDiseaseClinicalDB")
driver             = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server").replace(" ", "+")
trusted_connection = os.getenv("DB_TRUSTED_CONNECTION", "yes")

connection_url = (
    f"mssql+pyodbc://@{server}/{database}"
    f"?driver={driver}&trusted_connection={trusted_connection}&TrustServerCertificate=yes"
)
engine = create_engine(connection_url)


def main() -> None:
    if not FLAT_CSV.exists():
        raise FileNotFoundError(
            f"Flat CSV not found: {FLAT_CSV}\n"
            "Please run '01_data_profile.py' first."
        )

    print(f"Reading flat data from: {FLAT_CSV}")
    df = pd.read_csv(FLAT_CSV)
    print(f"  => {len(df)} rows, {len(df.columns)} columns")

    # Xóa dữ liệu cũ trong bảng staging trước khi nạp lại
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM dbo.raw_flat_data;"))
        print("Cleared old data in dbo.raw_flat_data.")

    print("Loading data into dbo.raw_flat_data...")
    df.to_sql(
        name="raw_flat_data",
        con=engine,
        schema="dbo",
        if_exists="append",
        index=False,
        chunksize=500,
    )
    print(f"Done! Loaded {len(df)} rows into dbo.raw_flat_data.")


if __name__ == "__main__":
    main()
