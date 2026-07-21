from pathlib import Path
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "processed" / "relational"

server = os.getenv("DB_SERVER", "localhost")
database = os.getenv("DB_NAME", "HeartDiseaseClinicalDB")
driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server").replace(" ", "+")
trusted_connection = os.getenv("DB_TRUSTED_CONNECTION", "yes")

connection_url = (
    f"mssql+pyodbc://@{server}/{database}"
    f"?driver={driver}&trusted_connection={trusted_connection}&TrustServerCertificate=yes"
)

engine = create_engine(connection_url)

IMPORT_ORDER = [
    ("patients", "patients.csv"),
    ("encounters", "encounters.csv"),
    ("symptoms", "symptoms.csv"),
    ("risk_history", "risk_history.csv"),
    ("resting_tests", "resting_tests.csv"),
    ("exercise_ecg_tests", "exercise_ecg_tests.csv"),
    ("diagnoses", "diagnoses.csv"),
]

TRUNCATE_ORDER = [name for name, _ in reversed(IMPORT_ORDER)]

def main():
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Relational data folder not found: {DATA_DIR}")

    with engine.begin() as conn:
        for table_name in TRUNCATE_ORDER:
            conn.exec_driver_sql(f"DELETE FROM dbo.{table_name};")

    for table_name, file_name in IMPORT_ORDER:
        csv_path = DATA_DIR / file_name
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing CSV for import: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"Importing {file_name} -> dbo.{table_name}: {df.shape}")
        df.to_sql(
            name=table_name,
            con=engine,
            schema="dbo",
            if_exists="append",
            index=False,
            chunksize=500
        )
    print("Import completed.")

if __name__ == "__main__":
    main()
