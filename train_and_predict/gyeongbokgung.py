###########일반 코드#########################
import warnings
warnings.simplefilter("ignore")  # 모든 Warning 메시지 숨기기

import os
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 현재 파일(`gyeongbokgung.py`)이 위치한 디렉토리 찾기
base_dir = os.path.dirname(os.path.abspath(__file__))

# dataset_filtered_csv 폴더에 있는 파일의 상대 경로 지정
file_path = os.path.join(base_dir, "..", "dataset_filtered_csv", "경복궁_filtered2.csv")

# 파일 데이터 불러오기
df = pd.read_csv(file_path, encoding="cp949")  # 인코딩 오류 방지

# 불필요한 열 제거 
df = df.drop(columns=['Date'], errors='ignore')
df = df.drop(columns=['Unnamed: 1'], errors='ignore')

# Feature와 Label 분리
X = df.drop(columns=['경복궁']).iloc[1:315]  # Feature
y = df['경복궁'].iloc[1:315]  # Label

# 데이터 타입 변환: True/False → 1/0
for col in ['weekday_0', 'weekday_1', 'weekday_2', 'weekday_3', 'weekday_4', 'weekday_5', 'weekday_6',
            'season_0', 'season_1', 'season_2', 'season_3']:
    X[col] = X[col].astype(int)

#print(X)
#print(y)

# 데이터 분할 (학습: 80%, 테스트: 20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# XGBoost 회귀 모델 설정
model = xgb.XGBRegressor(
    objective="reg:squarederror",  # 회귀 문제
    n_estimators=48,  # 트리 개수
    learning_rate=0.1,  # 학습률
    max_depth=5,  # 트리 깊이
    random_state=42
)

# 모델 학습
model.fit(X_train, y_train)

# 예측
y_pred = model.predict(X_test)

# 성능 평가
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = mse ** 0.5
r2 = r2_score(y_test, y_pred)

#print(f"MAE: {mae:.4f}")
#print(f"RMSE: {rmse:.4f}")
#print(f"R^2 Score: {r2:.4f}")

###########실시간 코드#########################

from datetime import datetime
import numpy as np
import requests
import json
import urllib.parse
from sklearn.preprocessing import StandardScaler
import joblib

###########실시간 환율 데이터 받아오기#######################

# Currencylayer API 키
'''
API_KEY = "이곳에 본인 계정에 api 키를 입력하세요."

# API 요청을 위한 URL
url = f"http://api.currencylayer.com/live?access_key={API_KEY}&currencies=KRW,JPY,EUR"

# API 요청 보내기
response = requests.get(url)
data = response.json()

def get_exchange_rate_dataframe(data):
    if data.get('success', False):
        # 환율 정보 추출
        timestamp = data['timestamp']
        quotes = data['quotes']

        date = datetime.fromtimestamp(timestamp)

        # USD를 포함한 전체 데이터를 명확히 정의
        exchange_data = [{
            'Date': date,
            'Currency': 'USD',
            'Rate': 1.0
        }] + [
            {
                'Date': date,
                'Currency': currency_pair[3:],  # 통화 코드
                'Rate': rate
            }
            for currency_pair, rate in quotes.items()
        ]

        # 데이터프레임으로 변환
        df = pd.DataFrame(exchange_data)
        
        return df

    else:
        raise ValueError("데이터를 가져오는 데 실패했습니다: " + data.get('error', {}).get('info', '알 수 없는 오류"))
'''

# 함수 호출하여 데이터프레임 반환
#df_exchange_rates = get_exchange_rate_dataframe(data)
#print(df_exchange_rates)
#exchange_rate_KRW = df_exchange_rates.loc[df_exchange_rates['Currency'] == 'KRW', 'Rate']
#exchange_rate = float(exchange_rate_KRW)

##################실시간 기상 데이터 받아오기#########################

# API 데이터 불러오기
start_index = 1
end_index = 50
type = "citydata"
place = "경복궁"
encoded_place = urllib.parse.quote(place)

url = f"http://openapi.seoul.go.kr:8088/6656424f686b617436346362504976/json/{type}/{start_index}/{end_index}/{encoded_place}"
response = requests.get(url)
contents = json.loads(response.text)

data_dict = contents['CITYDATA']  # CITYDATA 키 접근

def calculate_discomfort_index(temp_celsius, humidity_percent):
    discomfort_index = (
        0.81 * temp_celsius + 0.01 * humidity_percent * 
        (0.99 * temp_celsius - 14.3) + 46.3
    )
    return discomfort_index

##################파싱#########################

미세먼지 = float(data_dict['WEATHER_STTS'][0]['PM10'])
Windspeed = float(data_dict['WEATHER_STTS'][0]['WIND_SPD'])
temperature = float(data_dict['WEATHER_STTS'][0]['TEMP'])
humidity = float(data_dict['WEATHER_STTS'][0]['HUMIDITY'])
불쾌지수 = calculate_discomfort_index(temperature, humidity)
rainfall_str = data_dict['WEATHER_STTS'][0]['PRECIPITATION']
Rainfall = float(rainfall_str) if rainfall_str != '-' else 0.0
date_str = data_dict['WEATHER_STTS'][0]['WEATHER_TIME']

# 날짜를 datetime 형식으로 변환
date = pd.to_datetime(date_str)

# 요일 추출 (월요일:0 ~ 일요일:6)
weekday = date.weekday()

# 계절 추출
def month_to_season(month):
    if month in [3, 4, 5]:
        return 0  # 봄
    elif month in [6, 7, 8]:
        return 1  # 여름
    elif month in [9, 10, 11]:
        return 2  # 가을
    else:
        return 3  # 겨울

season = month_to_season(date.month)

##################저장된 스케일러 정보 불러오기#########################

# 현재 실행 중인 파일(`gyeongbokgung.py`)이 위치한 디렉토리 찾기
base_dir = os.path.dirname(os.path.abspath(__file__))

# pkl 파일들이 있는 디렉토리 상대 경로 지정
pkl_dir = os.path.join(base_dir, "..", "pkl")

# 각 스케일러 로드 (상대 경로 사용)
#scaler_Exchange_rate = joblib.load(os.path.join(pkl_dir, "scaler_Exchange_rate.pkl"))
#scaled_Exchange_rate = scaler_Exchange_rate.transform(np.array([[exchange_rate]]))[0][0]

scaler_Tinydust = joblib.load(os.path.join(pkl_dir, "scaler_Tinydust.pkl"))
scaled_미세먼지 = scaler_Tinydust.transform(np.array([[미세먼지]]))[0][0]

scaler_Windspeed = joblib.load(os.path.join(pkl_dir, "scaler_Windspeed.pkl"))
scaled_Windspeed = scaler_Windspeed.transform(np.array([[Windspeed]]))[0][0]

scaler_Temperature = joblib.load(os.path.join(pkl_dir, "scaler_Temperature.pkl"))
scaled_temperature = scaler_Temperature.transform(np.array([[temperature]]))[0][0]

scaler_Humidity = joblib.load(os.path.join(pkl_dir, "scaler_Humidity.pkl"))
scaled_humidity = scaler_Humidity.transform(np.array([[humidity]]))[0][0]

scaled_불쾌지수 = 0.01 * calculate_discomfort_index(scaled_temperature, scaled_humidity)

scaler_Rainfall = joblib.load(os.path.join(pkl_dir, "scaler_Rainfall.pkl"))
scaled_Rainfall = scaler_Rainfall.transform(np.array([[Rainfall]]))[0][0]

##############

feature_dict = {
    '달러환율': 4,  # 하드코딩 처리 (데이터 확보 어려움)
    '미세먼지(PM10)': scaled_미세먼지,
    '불쾌지수': scaled_불쾌지수,
    'Windspeed(m/s)': scaled_Windspeed,
    'Rainfall(mm)': scaled_Rainfall,
    'total_7d_avg': 0.5,  # 하드코딩 처리 (데이터 확보 어려움)
    'weekday_0': 1 if weekday == 0 else 0,
    'weekday_1': 1 if weekday == 1 else 0,
    'weekday_2': 1 if weekday == 2 else 0,
    'weekday_3': 1 if weekday == 3 else 0,
    'weekday_4': 1 if weekday == 4 else 0,
    'weekday_5': 1 if weekday == 5 else 0,
    'weekday_6': 1 if weekday == 6 else 0,
    'season_0': 1 if season == 0 else 0,
    'season_1': 1 if season == 1 else 0,
    'season_2': 1 if season == 2 else 0,
    'season_3': 1 if season == 3 else 0,
    '운항수_표준화': 0.1  # 하드코딩 처리 (데이터 확보 어려움)
}

df_live = pd.DataFrame([feature_dict])
df_live = df_live[X.columns]

# 실시간 데이터 예측
y_live_pred = model.predict(df_live)

# 결과 출력
result = {
    "경복궁": {
        "predicted_visitors": int(y_live_pred.tolist()[0]),  # ndarray를 리스트로 변환
        "congestion_level": int((y_live_pred.tolist()[0] / 94070) * 100)
    }
}
print(json.dumps(result, ensure_ascii=False), flush=True)
