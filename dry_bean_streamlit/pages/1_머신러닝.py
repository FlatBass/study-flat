# D:/study-flat/dl2/dry_bean_streamlit/pages/1_머신러닝.py

import json
import joblib
import streamlit as st
import pandas as pd
import plotly.express as px

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report

from utils.data import load_drybean_data, split_ml_data
from utils.report import compute_classification_metrics, append_experiment_log
from utils.paths import MODEL_DIR, REPORT_DIR



st.set_page_config(page_title="머신러닝 실험", page_icon="🧪", layout="wide")

st.title("🧪 머신러닝 실험")
st.caption("SVM / RandomForest 모델을 학습하고 평가 결과를 저장합니다.")

with st.sidebar :
    st.header("데이터 설정")

    use_uci = st.checkbox("UCI에서 Dry Bean Dataset 불러오기", value=True)
    uploaded_file = st.file_uploader("또는 CSV/XLSX 업로드", type=['csv', 'xlsx'])

    target_col = st.text_input("Target Column", value = "Class")

    test_size = st.slider("test_size", 0.1, 0.4, 0.2, 0.05)
    random_state = st.number_input("random_state", value=42, step=1)

    st.header("모델 선택")
    model_name = st.selectbox("모델", ["SVM", "RandomForest"])

    if model_name == "SVM":
        C = st.slider("C", 0.1, 20.0, 1.0, 0.1)
        kernel = st.selectbox("kernel", ["rbf", "linear", "poly", "sigmoid"])
        gamma = st.selectbox("gamma", ["scale", "auto"])
        # probability = st.checkbox("probability=True", value=True)

    elif model_name == "RandomForest":
        n_estimators = st.slider("n_estimators", 50, 500, 100, 50)
        max_depth = st.slider("max_depth", 2, 30, 10, 1)
        min_samples_split = st.slider("min_samples_split", 2, 20, 2, 1)
        min_samples_leaf = st.slider("min_samples_leaf", 1, 10, 1, 1)

    experiment_name = st.text_input(
        "실험명",
        value=f"ML_{model_name}_drybean"
    )

    memo = st.text_area("메모", value="")

@st.cache_data
def get_data_from_uci():
    return load_drybean_data()


if use_uci:
    df = get_data_from_uci()
elif uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
else:
    st.warning("UCI 데이터 사용 또는 파일 업로드를 선택해주세요.")
    st.stop()

st.subheader("데이터 미리보기")
st.dataframe(df.head())

st.write("데이터 shape:", df.shape)
st.write("Class 분포")
st.bar_chart(df[target_col].value_counts())


if st.button("머신러닝 모델 학습 시작"):
    X_train, X_test, y_train, y_test, label_encoder = split_ml_data(
        df,
        target_col=target_col,
        test_size=test_size,
        random_state=random_state
    )

    if model_name == "SVM":
        """
        C :  SVM에서 오분류를 얼마나 봐줄 것인가를 정하는 값
        kernel : SVM이 결정 경계를 어떤 방식으로 만들지 정하는 옵션
            - rbf : 데이터가 복잡하게 섞여 있어도 부드러운 곡선으로 나눠보자
        gamma ; 데이터 하나하나가 결정 경계에 얼마나 강하게 영향을 주는가
        """
        model = Pipeline([
            ("scaler", StandardScaler()),
            ("model", SVC(
                C=C,
                kernel=kernel,
                gamma=gamma,
                # probability=probability,
                random_state=random_state
            ))
        ])

        hyperparams = {
            "C": C,
            "kernel": kernel,
            "gamma": gamma,
            # "probability": probability,
            "test_size": test_size,
            "random_state": random_state
        }

    else:
        model = Pipeline([
            ("model", RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                min_samples_split=min_samples_split,
                min_samples_leaf=min_samples_leaf,
                random_state=random_state,
                n_jobs=-1
            ))
        ])

        hyperparams = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "min_samples_split": min_samples_split,
            "min_samples_leaf": min_samples_leaf,
            "test_size": test_size,
            "random_state": random_state
        }

    with st.spinner("모델 학습 중..."):
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

    metrics = compute_classification_metrics(y_test, y_pred)

    st.success("학습 완료!")

    st.subheader("평가 지표")
    metric_df = pd.DataFrame([metrics])
    st.dataframe(metric_df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Accuracy", f"{metrics['accuracy']:.4f}")
    col2.metric("Macro F1", f"{metrics['macro_f1']:.4f}")
    col3.metric("Weighted F1", f"{metrics['weighted_f1']:.4f}")

    st.subheader("Confusion Matrix")

    cm = confusion_matrix(y_test, y_pred)
    class_names = label_encoder.classes_

    cm_df = pd.DataFrame(cm, index=class_names, columns=class_names)

    fig = px.imshow(
        cm_df,
        text_auto=True,
        title=f"{model_name} Confusion Matrix",
        aspect="auto"
    )
    st.plotly_chart(fig, use_container_width=True)

    model_path = MODEL_DIR / f"{experiment_name}.joblib"
    report_path = REPORT_DIR / f"{experiment_name}_classification_report.json"

    joblib.dump(
        {
            "model": model,
            "label_encoder": label_encoder,
            "target_col": target_col,
            "feature_names": list(df.drop(columns=[target_col]).columns),
            "hyperparams": hyperparams
        },
        model_path
    )

    report = classification_report(
        y_test,
        y_pred,
        target_names=class_names,
        output_dict=True,
        zero_division=0
    )

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    log_row = {
        "experiment_name": experiment_name,
        "model_type": "Machine Learning",
        "model_name": model_name,
        "accuracy": metrics["accuracy"],
        "macro_precision": metrics["macro_precision"],
        "macro_recall": metrics["macro_recall"],
        "macro_f1": metrics["macro_f1"],
        "weighted_precision": metrics["weighted_precision"],
        "weighted_recall": metrics["weighted_recall"],
        "weighted_f1": metrics["weighted_f1"],
        "test_loss": "N/A",
        "hyperparams": json.dumps(hyperparams, ensure_ascii=False),
        "model_path": str(model_path),
        "best_model_path": "N/A",
        "weight_path": "N/A",
        "report_path": str(report_path),
        "memo": memo
    }

    append_experiment_log(log_row)

    st.success(f"모델 저장 완료: {model_path}")
    st.success(f"리포트 저장 완료: {report_path}")

    st.subheader("노션 복붙용 간단 기록")

    notion_md = f"""
### {experiment_name}

| 항목 | 값 |
| --- | --- |
| 모델 유형 | Machine Learning |
| 모델명 | {model_name} |
| accuracy | {metrics["accuracy"]:.4f} |
| macro precision | {metrics["macro_precision"]:.4f} |
| macro recall | {metrics["macro_recall"]:.4f} |
| macro f1 | {metrics["macro_f1"]:.4f} |
| weighted f1 | {metrics["weighted_f1"]:.4f} |
| test loss | N/A |
| 모델 저장 경로 | `{model_path}` |

#### Hyperparameters

```json
{json.dumps(hyperparams, ensure_ascii=False, indent=2)}
```
### Memo
{memo}
"""
    st.code(notion_md, language="markdown")
