# 7th-ML-6Team
# KOREA TOUR GUIDE - 관광지 혼잡도 예측 서비스

## 📖 소개
**KOREA TOUR GUIDE**는 서울 내 주요 관광지의 실시간 혼잡도를 예측하여 쾌적한 여행을 돕는 서비스입니다. 머신러닝 모델을 활용하여 기상 정보, 요일, 계절, 미세먼지 등의 요소를 분석하고, 예상 방문자 수와 혼잡도를 예측합니다.

## 🚀 주요 기능
### 1. 실시간 관광지 혼잡도 예측
- 창덕궁, 창경궁, 덕수궁, 경복궁, 종묘, 예술의전당, 서울대공원의 혼잡도를 예측합니다.
- 최신 기상 및 환경 데이터를 기반으로 XGBoost 모델을 활용하여 방문자 수를 예측합니다.

### 2. 지역별 맞춤형 추천
- 사용자가 선택한 관광지의 혼잡도를 비교하여 여유로운 관광지를 추천합니다.
- 혼잡도가 낮은 대체 관광지를 제안하여 쾌적한 여행을 지원합니다.

### 3. 실시간 데이터 통합
- 서울시 공공 API를 활용하여 날씨 및 미세먼지 데이터를 실시간으로 수집합니다.
- 실시간 환율 데이터를 가져와 분석에 반영합니다.
- 머신러닝 모델을 사용하여 방문자 수를 예측하고 대시보드를 통해 시각화합니다.

### 4. 직관적인 데이터 시각화
- Streamlit과 Plotly를 활용하여 혼잡도 예측 결과를 시각적으로 표현합니다.
- 관광지별 예상 방문자 수 및 혼잡도 랭킹을 한눈에 볼 수 있습니다.

## 🛠️ 기술 스택
- **프론트엔드**: Streamlit, Plotly
- **백엔드**: Python, Flask
- **데이터 처리**: Pandas, NumPy, Requests
- **머신러닝**: XGBoost, Scikit-learn
- **데이터 수집**: 서울시 공공 API, Web Scraping, Currencylayer API (환율 데이터)
- **모델 저장**: Joblib (scaler 및 학습된 모델 관리)

## 📂 프로젝트 구조
```
koreatourguide/
├── assets/                      # 폰트 및 기타 리소스
│   ├── BMHANNAPro.ttf           # 한글 폰트 파일
├── dataset_filtered_csv/        # 관광지별 정제된 데이터셋
│   ├── 창덕궁_filtered2.csv
│   ├── 창경궁_filtered2.csv
│   ├── 덕수궁_filtered2.csv
│   ├── 경복궁_filtered2.csv
│   ├── 종묘_filtered2.csv
│   ├── 예술의전당_filtered2.csv
│   ├── 서울대공원_filtered2.csv
├── pkl/                         # 학습된 모델 및 스케일러 저장 폴더
│   ├── scaler_Exchange_rate.pkl
│   ├── scaler_Humidity.pkl
│   ├── scaler_Rainfall.pkl
│   ├── scaler_Temperature.pkl
│   ├── scaler_Tinydust.pkl
│   ├── scaler_Windspeed.pkl
├── train_and_predict/           # 머신러닝 모델 및 예측 코드
│   ├── changdeokgung.py
│   ├── changgyeonggung.py
│   ├── deoksugung.py
│   ├── gyeongbokgung.py
│   ├── jongmyo.py
│   ├── seoul_arts_center.py
│   ├── seoul_grand_park.py
├── dashboard.py                 # Streamlit 대시보드
└── README.md                    # 프로젝트 문서
```

## 🔧 설치 및 사용법
### 1. 사전 준비
- Python 3.8 이상
- 필수 라이브러리 설치: Pandas, NumPy, XGBoost, Scikit-learn, Streamlit, Plotly, Requests
- Currencylayer API 키 발급 (환율 데이터 사용 시 필요)

### 2. 리포지토리 클론
```bash
git clone https://github.com/your-repo/koreatourguide.git
cd koreatourguide
```

### 3. 필수 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 머신러닝 모델 실행
```bash
python train_and_predict/changgyeonggung.py 등등
```

### 5. 대시보드 실행
```bash
streamlit run dashboard.py
```

### 6. 웹 대시보드 접속
- 실행 후 브라우저에서 [http://localhost:8501](http://localhost:8501) 접속

## 🌟 주요 API 엔드포인트
### 1. 관광지 혼잡도 예측
- **Method**: GET
- **Endpoint**: `/predict?place=창덕궁`
- **Response**:
```json
{
  "predicted_visitors": 20400,
  "congestion_level": 43
}
```

### 2. 실시간 기상 데이터 조회
- **Method**: GET
- **Endpoint**: `/weather?place=창덕궁`
- **Response**:
```json
{
  "temperature": 18.5,
  "humidity": 55,
  "windspeed": 2.1,
  "rainfall": 0.0
}
```

### 3. 실시간 환율 데이터 조회
- **Method**: GET
- **Endpoint**: `/exchange-rate`
- **Response**:
```json
{
  "USD_KRW": 1320.5,
  "USD_JPY": 147.2,
  "USD_EUR": 0.92
}
```

## 🔒 보안
- API 키 및 민감 데이터는 `.gitignore`에 포함하여 외부 노출 방지
- API 요청 속도 제한 적용 (Throttle)으로 서버 과부하 방지
- 환경 변수 활용하여 API 키 관리

## 📈 향후 개선 사항
- 사용자 맞춤 추천 기능 추가
- 날씨 예측 모델 적용하여 미래 혼잡도 예측
- 서울 외 지역 관광지 확장
- 모바일 앱 개발 및 배포
