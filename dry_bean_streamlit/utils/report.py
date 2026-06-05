# D:/study-flat/dl2/dry_bean_streamlit/utils/report.py

import json
from datetime import datetime

import pandas as pd
from pandas.errors import EmptyDataError
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

from utils.paths import LOG_PATH

MACRO = 'macro'
WEIGHTED = 'weighted'


def compute_classification_metrics(y_true, y_pred):
    """
    classification_metrics 평가 실행 함수
    """
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_precision": precision_score(y_true, y_pred, average=MACRO, zero_division=0),
        "macro_recall": recall_score(y_true, y_pred, average=MACRO, zero_division=0),
        "macro_f1": f1_score(y_true, y_pred, average=MACRO, zero_division=0),
        "weighted_precision": precision_score(y_true, y_pred, average=WEIGHTED, zero_division=0),
        "weighted_recall": recall_score(y_true, y_pred, average=WEIGHTED, zero_division=0),
        "weighted_f1": f1_score(y_true, y_pred, average=WEIGHTED, zero_division=0),
    }

    return metrics

def append_experiment_log(row):
    row['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_df = pd.DataFrame([row])

    if LOG_PATH.exists() and LOG_PATH.stat().st_size > 0:
        try:
            old_df = pd.read_csv(LOG_PATH)
            log_df = pd.concat([old_df, new_df], ignore_index=True)
        except EmptyDataError:
            log_df = new_df
    else:
        log_df = new_df
    
    log_df.to_csv(LOG_PATH, index=False, encoding='utf-8-sig')

def load_experiment_log():
    if not LOG_PATH.exists():
        return pd.DataFrame()

    if LOG_PATH.stat().st_size == 0:
        return pd.DataFrame()

    try:
        return pd.read_csv(LOG_PATH)
    except EmptyDataError:
        return pd.DataFrame()

def make_notion_markdown(row):
    """
    Streamlit st.code()에 넣어서 노션 복붙용으로 출력.
    """

    model_type = row.get("model_type", "")
    model_name = row.get("model_name", "")
    experiment_name = row.get("experiment_name", "")

    md = f"""
### {experiment_name}

---

### 실험 정보

| 항목 | 값 |
| --- | --- |
| 모델 유형 | {model_type} |
| 모델명 | {model_name} |
| 생성 시간 | {row.get("created_at", "")} |
| 데이터셋 | Dry Bean Dataset |
| target | Class |

---

### 평가 결과

| 지표 | 값 |
| --- | ---: |
| accuracy | {float(row.get("accuracy", 0)):.4f} |
| macro precision | {float(row.get("macro_precision", 0)):.4f} |
| macro recall | {float(row.get("macro_recall", 0)):.4f} |
| macro f1 | {float(row.get("macro_f1", 0)):.4f} |
| weighted precision | {float(row.get("weighted_precision", 0)):.4f} |
| weighted recall | {float(row.get("weighted_recall", 0)):.4f} |
| weighted f1 | {float(row.get("weighted_f1", 0)):.4f} |
| test loss | {row.get("test_loss", "N/A")} |

---

### 하이퍼파라미터

```json
{row.get("hyperparams", "{}")}

---

### 저장파일
| 항목              | 경로                                 |
| --------------- | ---------------------------------- |
| model path      | `{row.get("model_path", "")}`      |
| best model path | `{row.get("best_model_path", "")}` |
| weight path     | `{row.get("weight_path", "")}`     |
| report path     | `{row.get("report_path", "")}`     |

---

### 메모
{row.get("memo", "")}
"""
    return md.strip()


def make_comparison_markdown(df):
    if df.empty:
        return "아직 기록된 실험 결과가 없습니다."
    cols = [
    "experiment_name",
    "model_type",
    "model_name",
    "accuracy",
    "macro_f1",
    "weighted_f1",
    "test_loss"
]
    
    available_cols = [col for col in cols if col in df.columns]
    view = df[available_cols].copy()

    md = "### Dry Bean Dataset 모델 비교\n\n"
    md += "| 실험명 | 유형 | 모델 | accuracy | macro f1 | weighted f1 | test loss |\n"
    md += "| --- | --- | --- | ---: | ---: | ---: | ---: |\n"

    for _, row in view.iterrows():
        md += (
            f"| {row.get('experiment_name', '')} "
            f"| {row.get('model_type', '')} "
            f"| {row.get('model_name', '')} "
            f"| {float(row.get('accuracy', 0)):.4f} "
            f"| {float(row.get('macro_f1', 0)):.4f} "
            f"| {float(row.get('weighted_f1', 0)):.4f} "
            f"| {row.get('test_loss', 'N/A')} |\n"
        )

    return md

