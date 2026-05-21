import streamlit as st
import pandas as pd
import plotly.express as px

# ===========================================================================
# mission 2 : IMDB 대시보드 만들기
#        A1 : metric 2개 + 평점 히스토그램
#        A2 : 투표 수 vs 평점 scatter 탭 추가 (hover_name='Series_Title')
# ===========================================================================

# 데이터 캐시 설정
@st.cache_data
def load_load():
    df = pd.read_csv('./imdb_top_1000.csv')
    df['Released_Year'] = pd.to_numeric(df['Released_Year'], errors='coerce')
    return df

# 캐시 데이터 카피
imdb = load_load().copy()

with st.sidebar:
    min_rating = st.slider("최소 평점", 7.0, 9.5, 7.6, step=0.1)
    year_range = st.slider("개봉 연도", 1920, 2020, (2000, 2020))

filtered = imdb[
    (imdb['IMDB_Rating'] >= min_rating) &
    (imdb['Released_Year'] >= year_range[0]) &
    (imdb['Released_Year'] <= year_range[1])
]

# title
st.title("IMDB dashboard")
st.markdown('---')


col1, col2, col3= st.columns(3)
with col1:
    user_text = st.text_input("영화 제목을 입력하세요", placeholder="The Dark Knight").strip()
    movie = filtered[filtered['Series_Title'].str.lower() == user_text.lower()]

    if user_text:
        movie = filtered[
            filtered['Series_Title'].str.contains(user_text, case=False, na=False)
        ]
    else:
        movie = pd.DataFrame()

    if user_text and not movie.empty:
        no_of_Votes = movie['No_of_Votes'].iloc[0]
        rating = movie['IMDB_Rating'].iloc[0]
    else:
        no_of_Votes = "-"
        rating = "-"

    def find_gross(user_text):
        if filtered[filtered['Series_Title'] == user_text]:
            no_of_Votes = movie['No_of_Votes'].iloc[0]
        return no_of_Votes
    def find_rating(user_text):
        if filtered[filtered['Series_Title'] == user_text]:
            rating = movie['IMDB_Rating'].iloc[0]
        return rating
with col2 :
    st.metric("Votes", no_of_Votes)

with col3 :
    st.metric("IMDB Rating", rating)


tab1, tab2, tab3 = st.tabs(['data','scatter', 'histogram'])
with tab1:
    st.dataframe(filtered[['Series_Title','Released_Year',
                       'Genre','IMDB_Rating','No_of_Votes',
                       'Meta_score','Gross']], hide_index=True)
with tab2:
    fig = px.scatter(
        filtered,
        x="No_of_Votes",
        y="IMDB_Rating",
        hover_name='Series_Title',
        hover_data=['No_of_Votes',
                'Genre'],
    title='투표 수 vs IMDB 평점',
    template='simple_white',
    opacity=0.6
    )
    st.plotly_chart(fig, width='stretch')

with tab3:
    fig_his = px.histogram(
        filtered,
        x="IMDB_Rating",
        nbins=20,
        title='평점 분포', template='simple_white'
    )
    st.plotly_chart(fig_his, width='stretch')
