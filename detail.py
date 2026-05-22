import streamlit as st
import plotly.express as px
import pandas as pd

filtered = st.session_state.get('market_filtered')

if filtered is None:
    st.warning("데이터가 아직 준비되지 않았습니다.")
    st.stop()

if filtered.empty:
    st.warning("선택한 필터에 해당하는 데이터가 없습니다.")
    st.stop()

st.title("상세 분석")

tab1, tab2, tab3= st.tabs(['채널별 캠페인 평균 참여도','언어별 캠페인 평균 ROI','고객 세그먼트별 채널 평균 참여도'])

with tab1:
    heatmap_df = (
    filtered
    .groupby(["Campaign_Type", "Channel_Used"])["Engagement_Score"]
    .mean()
    .reset_index()
)

    fig = px.density_heatmap(
    heatmap_df,
    x="Campaign_Type",
    y="Channel_Used",
    z="Engagement_Score",
    text_auto=".2f",
    title="채널별 캠페인 유형 평균 참여도",
    color_continuous_scale='Blues'
)

    st.plotly_chart(fig, use_container_width=True)


with tab2:
    heatmap_df = (
    filtered
    .groupby(["Language", "Campaign_Type"])["ROI"]
    .mean()
    .reset_index()
)

    fig = px.density_heatmap(
    heatmap_df,
    x="Campaign_Type",
    y="Language",
    z="ROI",
    text_auto=".2f",
    title="언어별 캠페인 유형 평균 ROI",
    color_continuous_scale='Oranges'
)

    st.plotly_chart(fig, use_container_width=True)

with tab3:
    heatmap_df = (
    filtered
    .groupby(["Customer_Segment", "Channel_Used"])["Engagement_Score"]
    .mean()
    .reset_index()
)

    fig = px.density_heatmap(
    heatmap_df,
    x="Customer_Segment",
    y="Channel_Used",
    z="Engagement_Score",
    text_auto=".2f",
    title="고객 세그먼트별 채널 평균 참여도",
    color_continuous_scale='Greens'
)

    st.plotly_chart(fig, use_container_width=True)