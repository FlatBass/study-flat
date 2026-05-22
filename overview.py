import streamlit as st

filtered = st.session_state.get('market_filtered')

if filtered is None:
    st.warning('데이터가 아직 준비되지 않았습니다!')
    st.stop()

st.title("Marketing Campaign Dashboard")

c1, c2, c3 = st.columns(3)

c1.metric("총 캠페인 수", f"{len(filtered):,}")
c2.metric("평균 참여율", f"{filtered['Engagement_Score'].mean():.2f}")
c3.metric("평균 전환율", f"{filtered['Conversion_Rate'].mean():.1%}")

st.markdown("---")

st.dataframe(
    filtered[
        [
            "Location",
            "Customer_Segment",
            "Language",
            "Campaign_Type",
            "Target_Audience",
            "Channel_Used",
            "Conversion_Rate",
            "Engagement_Score",
            "ROI",
        ]
    ],
    hide_index=True
)

# TODO : CVR : 전환율(Conversion Rate)
# 마케팅이나 비즈니스에서 웹사이트 방문자 중 우리가 의도한
# 특정 행동(구매, 회원가입, 앱 다운로드 등)을 완료한 사람의 비율
# TODO :  사용자가 브랜드, 콘텐츠 또는 플랫폼에
# 얼마나 적극적으로 반응하고 상호작용하는지를 수치화한 '참여 점수'
