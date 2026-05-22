import streamlit as st
import plotly.express as px
import pandas as pd

@st.cache_data
def load_maketing():
    market = pd.read_csv('./marketing_campaign_dataset.xls')

    market['Acquisition_Cost'] = (
    market['Acquisition_Cost'].str.replace(
            '[$,]', '', regex=True)
            .astype(float)        
        )
    
    market['Date'] = pd.to_datetime(market['Date'])
    return market

df = load_maketing().copy()

campaign_options = sorted(df["Campaign_Type"].unique().tolist())
location_options = ["All"] + sorted(df["Location"].unique().tolist())
target_options = ["All"] + sorted(df["Target_Audience"].unique().tolist())

def reset_filters():
    st.session_state["campaign_types"] = campaign_options
    st.session_state["location"] = 'All'
    st.session_state['target_audience'] = 'All'

if 'campaign_types' not in st.session_state:
    st.session_state['campaign_types'] = campaign_options

if 'location' not in st.session_state:
    st.session_state['location'] = 'All'

if 'target_audience' not in st.session_state:
    st.session_state['target_audience'] = 'All'



with st.sidebar:
    st.header("Filter")     
    st.button('Reset', on_click=reset_filters)

    location = st.selectbox(
        "Location",
        location_options,
        key="location"
    )

    target = st.selectbox(
        "Target",
        target_options,
        key="target_audience"
    )

    campaign_types = st.multiselect(
        "Campaign Type",
        campaign_options,
        key="campaign_types"
    )

filtered = df[df['Campaign_Type'].isin(st.session_state['campaign_types'])]
if st.session_state['location'] != 'All':
    filtered = filtered[(filtered['Location'] == st.session_state["location"])]

if st.session_state['target_audience'] != 'All':
    filtered = filtered[(filtered['Target_Audience'] == st.session_state["target_audience"])]


st.session_state['market_df'] = df
st.session_state['market_filtered'] = filtered


overview = st.Page('overview.py', title='요약', icon='📊')
detail = st.Page('detail.py', title='상세 분석', icon='📈')

pg = st.navigation([overview, detail])
pg.run()