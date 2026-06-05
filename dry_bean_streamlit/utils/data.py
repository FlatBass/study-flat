# D:/study-flat/dl2/dry_bean_streamlit/utils/data.py

import pandas as pd
from ucimlrepo import fetch_ucirepo
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler



def load_drybean_data():
    """
    UCI Dry Bean Dataset 로드
    실패할 경우 Streamlit 페이지에서 파일 업로드 방식으로 대체 가능.
    """
    dry_bean = fetch_ucirepo(id=602)

    X = dry_bean.data.features
    y = dry_bean.data.targets

    if isinstance(y, pd.DataFrame):
        y = y.iloc[:, 0]
    
    df = X.copy()

    df['Class'] = y

    return df

def split_ml_data(df, target_col='Class', test_size=0.2, random_state=42):
    """
    머신러닝 트레인 테스트 셋 분리
    라벨 인코딩
    """
    X = df.drop(columns=[target_col])
    y = df[target_col]

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=test_size,
        random_state=random_state,
        stratify=y_encoded
    )

    return X_train, X_test, y_train, y_test, label_encoder

def split_dl_data(
        df,
        target_col = 'Class',
        test_size = 0.2,
        val_size = 0.2,
        random_state = 42
):
    """
    딥러닝 트레인 테스트셋 분리
    트레인 - 학습데이터 / 검증 데이터 분리
    스케일링
    """
    X = df.drop(columns=[target_col])
    y = df[target_col]

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    # train-test split
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X,
        y_encoded,
        test_size=test_size,
        random_state=random_state,
        stratify=y_encoded
    )

    # val_train-val_test split
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_full,
        y_train_full,
        test_size=val_size,
        random_state=random_state,
        stratify=y_train_full
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    return {
        "X_train": X_train_scaled,
        "X_val": X_val_scaled,
        "X_test": X_test_scaled,
        "y_train": y_train,
        "y_val": y_val,
        "y_test": y_test,
        "scaler": scaler,
        "label_encoder": label_encoder,
        "feature_names": list(X.columns)
    }