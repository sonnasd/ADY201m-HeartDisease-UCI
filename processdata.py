import runpy
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
SCRIPT_ORDER = [
    PROJECT_ROOT / "src" / "01_data_profile.py",
    PROJECT_ROOT / "src" / "02_preprocessing_cleaning.py",
    PROJECT_ROOT / "src" / "03_eda.py",
    PROJECT_ROOT / "src" / "04_machine_learning.py",
    PROJECT_ROOT / "src" / "05_validate_outputs.py",
]


def main() -> None:
    for script_path in SCRIPT_ORDER:
        print(f"\n=== Running {script_path.relative_to(PROJECT_ROOT)} ===")
        runpy.run_path(str(script_path), run_name="__main__")
    print("\nPipeline completed.")


if __name__ == "__main__":
    main()
