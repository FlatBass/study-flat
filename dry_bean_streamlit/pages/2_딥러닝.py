# D:/study-flat/dl2/dry_bean_streamlit/pages/2_딥러닝.py

import os
import json
import random
import joblib

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import tensorflow as tf

from sklearn.metrics import confusion_matrix, classification_report

from utils.data import load_drybean_data, split_dl_data
from utils.report import compute_classification_metrics, append_experiment_log
from utils.paths import MODEL_DIR, WEIGHT_DIR, REPORT_DIR


st.set_page_config(page_title="딥러닝 실험", page_icon="🤖", layout="wide")

st.title("🤖 딥러닝 실험")
st.caption("Dense Neural Network 기반 Dry Bean 다중분류 실험")


def set_global_seed(seed=42):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def build_dense_model(
    input_dim,
    num_classes,
    hidden_units,
    activation,
    dropout_rate,
    optimizer_name,
    learning_rate
):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Input(shape=(input_dim,)))

    for units in hidden_units:
        model.add(tf.keras.layers.Dense(units, activation=activation))

        if dropout_rate > 0:
            model.add(tf.keras.layers.Dropout(dropout_rate))

    model.add(tf.keras.layers.Dense(num_classes, activation="softmax"))

    if optimizer_name == "adam":
        optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    elif optimizer_name == "rmsprop":
        optimizer = tf.keras.optimizers.RMSprop(learning_rate=learning_rate)
    else:
        optimizer = tf.keras.optimizers.SGD(learning_rate=learning_rate)

    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


@st.cache_data
def get_data_from_uci():
    return load_drybean_data()


with st.sidebar:
    st.header("데이터 설정")

    use_uci = st.checkbox("UCI에서 Dry Bean Dataset 불러오기", value=True)
    uploaded_file = st.file_uploader("또는 CSV/XLSX 업로드", type=["csv", "xlsx"])

    target_col = st.text_input("Target Column", value="Class")

    test_size = st.slider("test_size", 0.1, 0.4, 0.2, 0.05)
    val_size = st.slider("val_size", 0.1, 0.4, 0.2, 0.05)
    random_state = st.number_input("random_state", value=42, step=1)

    st.header("모델 구조")
    units_text = st.text_input("hidden_units", value="128,64,32")
    activation = st.selectbox("activation", ["relu", "tanh", "sigmoid"])
    dropout_rate = st.slider("dropout_rate", 0.0, 0.7, 0.2, 0.05)

    st.header("학습 설정")
    optimizer_name = st.selectbox("optimizer", ["adam", "rmsprop", "sgd"])
    learning_rate = st.number_input("learning_rate", value=0.001, format="%.5f")
    epochs = st.slider("epochs", 5, 200, 50, 5)
    batch_size = st.selectbox("batch_size", [16, 32, 64, 128, 256], index=1)

    use_early_stopping = st.checkbox("EarlyStopping 사용", value=True)
    patience = st.slider("patience", 2, 20, 5, 1)

    experiment_name = st.text_input(
        "실험명",
        value="DL_dense_drybean"
    )

    memo = st.text_area("메모", value="")


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

if st.button("🚀 딥러닝 모델 학습 시작"):
    set_global_seed(random_state)

    hidden_units = tuple(
        int(x.strip()) for x in units_text.split(",") if x.strip()
    )

    data = split_dl_data(
        df,
        target_col=target_col,
        test_size=test_size,
        val_size=val_size,
        random_state=random_state
    )

    X_train = data["X_train"]
    X_val = data["X_val"]
    X_test = data["X_test"]
    y_train = data["y_train"]
    y_val = data["y_val"]
    y_test = data["y_test"]

    label_encoder = data["label_encoder"]
    scaler = data["scaler"]
    class_names = label_encoder.classes_

    input_dim = X_train.shape[1]
    num_classes = len(class_names)

    model = build_dense_model(
        input_dim=input_dim,
        num_classes=num_classes,
        hidden_units=hidden_units,
        activation=activation,
        dropout_rate=dropout_rate,
        optimizer_name=optimizer_name,
        learning_rate=learning_rate
    )

    st.subheader("모델 요약")
    model.summary(print_fn=lambda x: st.text(x))

    model_path = MODEL_DIR / f"{experiment_name}_final.keras"
    best_model_path = MODEL_DIR / f"{experiment_name}_best.keras"
    weight_path = WEIGHT_DIR / f"{experiment_name}.weights.h5"
    preprocess_path = MODEL_DIR / f"{experiment_name}_preprocess.joblib"
    report_path = REPORT_DIR / f"{experiment_name}_classification_report.json"

    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(best_model_path),
            monitor="val_loss",
            save_best_only=True,
            mode="min",
            verbose=1
        )
    ]

    if use_early_stopping:
        callbacks.append(
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss",
                patience=patience,
                restore_best_weights=True,
                verbose=1
            )
        )

    with st.spinner("딥러닝 모델 학습 중..."):
        history = model.fit(
            X_train,
            y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )

    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)

    y_proba = model.predict(X_test)
    y_pred = np.argmax(y_proba, axis=1)

    metrics = compute_classification_metrics(y_test, y_pred)

    model.save(model_path)
    model.save_weights(weight_path)

    joblib.dump(
        {
            "scaler": scaler,
            "label_encoder": label_encoder,
            "feature_names": data["feature_names"],
            "target_col": target_col
        },
        preprocess_path
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

    st.success("딥러닝 학습 완료!")

    col1, col2, col3 = st.columns(3)
    col1.metric("Test Accuracy", f"{test_acc:.4f}")
    col2.metric("Test Loss", f"{test_loss:.4f}")
    col3.metric("Macro F1", f"{metrics['macro_f1']:.4f}")

    st.subheader("Loss / Accuracy 곡선")

    history_df = pd.DataFrame(history.history)
    history_df["epoch"] = range(1, len(history_df) + 1)

    loss_fig = px.line(
        history_df,
        x="epoch",
        y=["loss", "val_loss"],
        title="Train / Validation Loss"
    )
    st.plotly_chart(loss_fig, width="stretch")

    acc_fig = px.line(
        history_df,
        x="epoch",
        y=["accuracy", "val_accuracy"],
        title="Train / Validation Accuracy"
    )
    st.plotly_chart(acc_fig, width="stretch")

    st.subheader("Confusion Matrix")

    cm = confusion_matrix(y_test, y_pred)
    cm_df = pd.DataFrame(cm, index=class_names, columns=class_names)

    cm_fig = px.imshow(
        cm_df,
        text_auto=True,
        title="Deep Learning Confusion Matrix",
        aspect="auto"
    )
    st.plotly_chart(cm_fig, width="stretch")

    hyperparams = {
        "hidden_units": hidden_units,
        "activation": activation,
        "dropout_rate": dropout_rate,
        "optimizer": optimizer_name,
        "learning_rate": learning_rate,
        "epochs": epochs,
        "batch_size": batch_size,
        "early_stopping": use_early_stopping,
        "patience": patience if use_early_stopping else None,
        "test_size": test_size,
        "val_size": val_size,
        "random_state": random_state
    }

    best_val_loss = min(history.history["val_loss"])
    best_val_loss_epoch = int(np.argmin(history.history["val_loss"]) + 1)

    best_val_acc = max(history.history["val_accuracy"])
    best_val_acc_epoch = int(np.argmax(history.history["val_accuracy"]) + 1)

    log_row = {
        "experiment_name": experiment_name,
        "model_type": "Deep Learning",
        "model_name": "Dense Neural Network",
        "accuracy": metrics["accuracy"],
        "macro_precision": metrics["macro_precision"],
        "macro_recall": metrics["macro_recall"],
        "macro_f1": metrics["macro_f1"],
        "weighted_precision": metrics["weighted_precision"],
        "weighted_recall": metrics["weighted_recall"],
        "weighted_f1": metrics["weighted_f1"],
        "test_loss": test_loss,
        "best_val_loss": best_val_loss,
        "best_val_loss_epoch": best_val_loss_epoch,
        "best_val_acc": best_val_acc,
        "best_val_acc_epoch": best_val_acc_epoch,
        "hyperparams": json.dumps(hyperparams, ensure_ascii=False),
        "model_path": str(model_path),
        "best_model_path": str(best_model_path),
        "weight_path": str(weight_path),
        "report_path": str(report_path),
        "memo": memo
    }

    append_experiment_log(log_row)

    st.success(f"Final model 저장 완료: {model_path}")
    st.success(f"Best model 저장 완료: {best_model_path}")
    st.success(f"Weights 저장 완료: {weight_path}")
    st.success(f"Preprocess 저장 완료: {preprocess_path}")

    st.subheader("노션 복붙용 기록")

    notion_md = f"""
### {experiment_name}

---

### 실험 정보

| 항목 | 값 |
| --- | --- |
| 모델 유형 | Deep Learning |
| 모델명 | Dense Neural Network |
| 데이터셋 | Dry Bean Dataset |
| target | Class |
| random_state | {random_state} |

---

### 모델 구조

| 항목 | 값 |
| --- | --- |
| hidden_units | `{hidden_units}` |
| activation | `{activation}` |
| dropout_rate | {dropout_rate} |
| optimizer | `{optimizer_name}` |
| learning_rate | {learning_rate} |
| epochs | {epochs} |
| batch_size | {batch_size} |
| early_stopping | {use_early_stopping} |
| patience | {patience if use_early_stopping else "N/A"} |

---

### 결과 기록

| 기준 | 값 |
| --- | ---: |
| test acc | {test_acc:.4f} |
| test loss | {test_loss:.4f} |
| macro precision | {metrics["macro_precision"]:.4f} |
| macro recall | {metrics["macro_recall"]:.4f} |
| macro f1 | {metrics["macro_f1"]:.4f} |
| weighted f1 | {metrics["weighted_f1"]:.4f} |
| best val acc | {best_val_acc:.4f} |
| best val acc epoch | {best_val_acc_epoch} |
| best val loss | {best_val_loss:.4f} |
| best val loss epoch | {best_val_loss_epoch} |

---

### 저장 파일

| 항목 | 경로 |
| --- | --- |
| final model | `{model_path}` |
| best model | `{best_model_path}` |
| weights | `{weight_path}` |
| preprocess | `{preprocess_path}` |
| report | `{report_path}` |

---

### 메모

{memo}
"""

    st.code(notion_md, language="markdown")