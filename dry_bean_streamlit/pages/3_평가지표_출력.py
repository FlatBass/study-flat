# D:/study-flat/dl2/dry_bean_streamlit/pages/3_평가지표_출력.py

import pandas as pd
import streamlit as st
import plotly.express as px

from utils.report import (
    load_experiment_log,
    make_notion_markdown,
    make_comparison_markdown
)


st.set_page_config(page_title="평가 지표 출력", page_icon="📊", layout="wide")

st.title("📊 평가 지표 출력 / 모델 비교")
st.caption("저장된 experiment_log.csv를 기반으로 ML / DL 실험 결과를 비교합니다.")

df = load_experiment_log()

if df.empty:
    st.warning("아직 저장된 실험 결과가 없습니다. 머신러닝 또는 딥러닝 페이지에서 먼저 학습을 실행하세요.")
    st.stop()


st.subheader("전체 실험 로그")
st.dataframe(df, width="stretch")

metric_cols = [
    "accuracy",
    "macro_precision",
    "macro_recall",
    "macro_f1",
    "weighted_f1"
]

available_metric_cols = [col for col in metric_cols if col in df.columns]

st.subheader("모델별 성능 비교")

fig = px.bar(
    df,
    x="experiment_name",
    y=available_metric_cols,
    color="model_type",
    barmode="group",
    title="ML / DL 모델 성능 비교"
)
st.plotly_chart(fig, width="stretch")


if "test_loss" in df.columns:
    dl_df = df[df["test_loss"] != "N/A"].copy()

    if not dl_df.empty:
        dl_df["test_loss"] = pd.to_numeric(dl_df["test_loss"], errors="coerce")

        st.subheader("딥러닝 Test Loss 비교")

        loss_fig = px.bar(
            dl_df,
            x="experiment_name",
            y="test_loss",
            color="model_name",
            title="Deep Learning Test Loss 비교"
        )
        st.plotly_chart(loss_fig, width="stretch")


st.subheader("실험별 노션 복붙용 Markdown")

selected_exp = st.selectbox(
    "실험 선택",
    df["experiment_name"].tolist()
)

selected_row = df[df["experiment_name"] == selected_exp].iloc[-1]
notion_md = make_notion_markdown(selected_row)

st.code(notion_md, language="markdown")


st.subheader("전체 비교표 노션 복붙용 Markdown")

comparison_md = make_comparison_markdown(df)
st.code(comparison_md, language="markdown")


st.download_button(
    label="experiment_log.csv 다운로드",
    data=df.to_csv(index=False, encoding="utf-8-sig"),
    file_name="dry_bean_experiment_log.csv",
    mime="text/csv"
)