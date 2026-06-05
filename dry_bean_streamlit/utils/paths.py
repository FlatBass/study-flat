# D:/study-flat/dl2/dry_bean_streamlit/utils/paths.py

from pathlib import Path

ARTIFACT_DIR = Path("artifacts")
MODEL_DIR = ARTIFACT_DIR / "models"
WEIGHT_DIR = ARTIFACT_DIR / "weights"
REPORT_DIR = ARTIFACT_DIR / "reports"
LOG_PATH = ARTIFACT_DIR / "experiment_log.csv"

for path in [ARTIFACT_DIR, MODEL_DIR, WEIGHT_DIR, REPORT_DIR]:
    path.mkdir(parents=True, exist_ok=True)