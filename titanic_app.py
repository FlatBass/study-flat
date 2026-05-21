import streamlit as st
import pandas as pd
import plotly.express as px

# ===========================================================================
# mission 1 : 타이타닉 대시보드 만들기
#         B1: 사이드바 필터 4종(multiselect·selectbox·slider·checkbox) 추가
#         B2: metric 3개(전체·생존자·생존율) 표시
#         B3: tabs(차트/데이터) 분리
#         B4: 차트 종류 바꿔보기 (px.histogram → px.scatter)
# ===========================================================================

# 데이터 캐시 설정
@st.cache_data
def load_titanic():
    url = 'https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv'
    return pd.read_csv(url)

# 캐시 데이터 카피
titanic = load_titanic().copy()
titanic['Age'] = titanic['Age'].fillna(titanic['Age'].median())


# 사이드바
with st.sidebar:
    st.header("Filter")
    pclass_options = st.multiselect("Class", [1,2,3], default=[1,2,3])
    gender = st.selectbox('Sex', ['All', 'male', 'female'])
    ate_range = st.slider("Age", 0, 80, (0, 80))
    survived_only = st.checkbox('Only Alive')

# 필터

base_filtered = titanic[titanic['Pclass'].isin(pclass_options)]
base_filtered = base_filtered[
    (base_filtered['Age'] >= ate_range[0]) & 
    (base_filtered['Age'] <= ate_range[1])
]
if gender != 'All':
    base_filtered = base_filtered[base_filtered['Sex'] == gender]

filtered = base_filtered.copy()

if survived_only:
    filtered = filtered[filtered['Survived'] == 1]

# 
total_count = len(filtered)
survivor_count = base_filtered['Survived'].sum()
death_count = (base_filtered['Survived'] == 0).sum()

survival_rate = f"{filtered['Survived'].mean() * 100 : .1f}%" if total_count > 0 else "N/A"
death_rate = f"{(base_filtered['Survived'] == 0).mean() * 100 : .1f}%" if total_count > 0 else "N/A"

# title
st.title("Titanic dashboard")


col1, col2, col3 = st.columns(3)
with col1:
    st.metric('Passenger', total_count)

with col2:
    if survived_only:
        st.metric('dead', death_count)
    else:
        st.metric('survivor', survivor_count)

with col3:
    if survived_only:
        st.metric('death rate', death_rate)
    else:
        st.metric("survival rate", survival_rate)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["data","histogram","scatter"])
with tab1 :
    st.dataframe(filtered[['Name','Pclass','Sex', 'Age', 'Survived']], hide_index=True)
with tab2 :
    fig_his = px.histogram(filtered, x="Age", nbins=20,
                           title='나이 분포', template='simple_white')
    st.plotly_chart(fig_his, width='stretch')
with tab3 :
    fig_scat = px.scatter(filtered, x='Age', y='Pclass',
                          title='나이별 승객 분포', template='simple_white',
                          opacity=0.6)
    fig_scat.update_traces(marker=dict(size=12))   
    fig_scat.update_yaxes(
    tickmode='array',
    tickvals=[1, 2, 3],
    ticktext=['1', '2', '3']) 
    st.plotly_chart(fig_scat, width='stretch')



