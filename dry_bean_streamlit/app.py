# D:/study-flat/dl2/dry_bean_streamlit/app.py

import streamlit as st

st.set_page_config(
    page_title="Dry Bean ML/DL Experiment Lab",
    page_icon="🫘",
    layout='wide'
)

st.title("Dry Bean Datasets 실험 대시보드")

st.markdown("""
UCI Dry Bean Dataset을 이용해 SVM, RandomForest, 딥러닝 모델을 비교 실험하는 Streamlit 앱입니다.

### 페이지 구성

1. **머신러닝**
   - SVM
   - RandomForest
   - 하이퍼파라미터 튜닝
   - 모델 저장

2. **딥러닝**
   - Dense Neural Network
   - Dropout
   - EarlyStopping
   - Loss / Accuracy 곡선
   - Final model / Best model / Weights 저장

3. **평가 지표 출력**
   - ML / DL 실험 결과 비교
   - Acc, Loss, Precision, Recall, F1-score 비교
   - 노션 복붙용 Markdown 자동 생성
""")

