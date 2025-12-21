# API 문서

백엔드 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 기본 정보

- **Base URL**: `http://localhost:8000`
- **API 버전**: `1.0.0`
- **Content-Type**: `application/json`
- **인증**: 없음 (공개 API)

## 엔드포인트 상세

### 1. API 루트

#### `GET /`

API 루트 엔드포인트. 사용 가능한 모든 API 엔드포인트 목록을 반환합니다.

**요청**
```http
GET / HTTP/1.1
Host: localhost:8000
```

**응답 (200 OK)**
```json
{
  "message": "KOREA TOUR GUIDE API",
  "version": "1.0.0",
  "endpoints": {
    "tourist_sites": "/api/tourist-sites",
    "predict": "/api/predict/{tourist_code}",
    "predict_all": "/api/predict-all",
    "evaluate": "/api/evaluate/{tourist_code}",
    "evaluate_all": "/api/evaluate-all",
    "health": "/api/health"
  },
  "docs": "/docs"
}
```

**응답 필드**
- `message` (string): API 이름
- `version` (string): API 버전
- `endpoints` (object): 사용 가능한 엔드포인트 목록
- `docs` (string): API 문서 URL

---

### 2. 헬스 체크

#### `GET /api/health`

API 서버의 상태를 확인합니다.

**요청**
```http
GET /api/health HTTP/1.1
Host: localhost:8000
```

**응답 (200 OK)**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-21T21:28:04.039450",
  "service": "KOREA TOUR GUIDE API"
}
```

**응답 필드**
- `status` (string): 서버 상태 (`"healthy"` 고정)
- `timestamp` (string): 응답 시각 (ISO 8601 형식)
- `service` (string): 서비스 이름

---

### 3. 관광지 정보 조회

#### `GET /api/tourist-sites`

서울 내 주요 관광지 7곳의 정보를 반환합니다.

**요청**
```http
GET /api/tourist-sites HTTP/1.1
Host: localhost:8000
```

**응답 (200 OK)**
```json
{
  "sites": [
    {
      "code": "changdeok_palace",
      "korean_name": "창덕궁",
      "max_capacity": 119765,
      "district_code": "111123",
      "nx": 60,
      "ny": 127
    },
    {
      "code": "changgyeong_palace",
      "korean_name": "창경궁",
      "max_capacity": 47126,
      "district_code": "111123",
      "nx": 60,
      "ny": 127
    }
    // ... 나머지 관광지들
  ]
}
```

**응답 필드**
- `sites` (array): 관광지 정보 배열
  - `code` (string): 관광지 코드 (영문, API 호출 시 사용)
  - `korean_name` (string): 관광지 한글 이름
  - `max_capacity` (integer): 최대 수용 인원
  - `district_code` (string): 자치구 코드
  - `nx` (integer): 기상청 격자 X 좌표
  - `ny` (integer): 기상청 격자 Y 좌표

---

### 4. 단일 관광지 혼잡도 예측

#### `GET /api/predict/{tourist_code}`

특정 관광지의 예상 방문자 수와 혼잡도를 예측합니다.

**요청**
```http
GET /api/predict/changdeok_palace HTTP/1.1
Host: localhost:8000
```

**경로 파라미터**
- `tourist_code` (string, required): 관광지 코드
  - 가능한 값: `changdeok_palace`, `changgyeong_palace`, `deoksugung_palace`, `gyeongbok_palace`, `jongmyo_shrine`, `seoul_arts_center`, `seoul_grand_park`

**응답 (200 OK)**
```json
{
  "창덕궁": {
    "predicted_visitors": 6025,
    "congestion_level": 5.03
  }
}
```

**응답 필드**
- `{관광지명}` (object): 관광지 한글 이름을 키로 하는 예측 결과
  - `predicted_visitors` (integer): 예상 방문자 수
  - `congestion_level` (float): 혼잡도 (0-100, 높을수록 혼잡)

**에러 응답**

**404 Not Found** - 관광지 코드를 찾을 수 없음
```json
{
  "detail": "알 수 없는 관광지 코드: invalid_code"
}
```

**503 Service Unavailable** - 모델 파일이 없음
```json
{
  "detail": "모델 파일을 찾을 수 없습니다: /path/to/model.pkl\n먼저 'python scripts/train_models.py'를 실행하여 모델을 학습하세요."
}
```

**500 Internal Server Error** - 서버 내부 오류
```json
{
  "detail": "예측 중 오류 발생: {에러 메시지}"
}
```

---

### 5. 모든 관광지 혼잡도 예측

#### `GET /api/predict-all`

모든 관광지의 예상 방문자 수와 혼잡도를 한 번에 예측합니다.

**요청**
```http
GET /api/predict-all HTTP/1.1
Host: localhost:8000
```

**응답 (200 OK)**
```json
{
  "predictions": {
    "창덕궁": {
      "predicted_visitors": 6025,
      "congestion_level": 5.03
    },
    "창경궁": {
      "predicted_visitors": 3631,
      "congestion_level": 7.7
    },
    "덕수궁": {
      "predicted_visitors": 14397,
      "congestion_level": 70.57
    }
    // ... 나머지 관광지들
  },
  "errors": [],
  "timestamp": "2025-12-21T21:28:14.123456"
}
```

**응답 필드**
- `predictions` (object): 성공한 예측 결과
  - 키: 관광지 한글 이름
  - 값: 예측 결과 객체 (`predicted_visitors`, `congestion_level`)
- `errors` (array): 실패한 관광지 정보 (있는 경우)
  - `site` (string): 관광지 한글 이름
  - `code` (string): 관광지 코드
  - `error` (string): 에러 메시지
- `timestamp` (string): 예측 시각 (ISO 8601 형식)

**에러 응답**

이 엔드포인트는 개별 관광지 예측 실패 시에도 전체 요청이 실패하지 않습니다. 실패한 관광지는 `errors` 배열에 포함됩니다.

**에러가 있는 경우 응답 예시 (200 OK)**
```json
{
  "predictions": {
    "창덕궁": {
      "predicted_visitors": 6025,
      "congestion_level": 5.03
    }
  },
  "errors": [
    {
      "site": "경복궁",
      "code": "gyeongbok_palace",
      "error": "모델 파일을 찾을 수 없습니다"
    }
  ],
  "timestamp": "2025-12-21T21:28:14.123456"
}
```

---

### 6. 단일 관광지 모델 성능 평가

#### `GET /api/evaluate/{tourist_code}`

특정 관광지 모델의 성능을 평가하고 시각화에 필요한 데이터를 반환합니다.

**요청**
```http
GET /api/evaluate/changdeok_palace HTTP/1.1
Host: localhost:8000
```

**경로 파라미터**
- `tourist_code` (string, required): 관광지 코드
  - 가능한 값: `changdeok_palace`, `changgyeong_palace`, `deoksugung_palace`, `gyeongbok_palace`, `jongmyo_shrine`, `seoul_arts_center`, `seoul_grand_park`
  - 자세한 목록은 [사용 가능한 관광지 코드](#사용-가능한-관광지-코드) 섹션 참조

**응답 (200 OK)**
```json
{
  "tourist_code": "changdeok_palace",
  "korean_name": "창덕궁",
  "train_metrics": {
    "MAE": 852.25,
    "MSE": 1645781.92,
    "RMSE": 1282.88,
    "R²": 0.8979,
    "MAPE": 22.45
  },
  "test_metrics": {
    "MAE": 2509.57,
    "MSE": 19184974.83,
    "RMSE": 4380.07,
    "R²": 0.0909,
    "MAPE": 54.89
  },
  "stats": {
    "train_size": 251,
    "test_size": 63,
    "feature_count": 15,
    "actual_mean": 5251.10,
    "actual_std": 4630.66,
    "predicted_mean": 5016.45,
    "predicted_std": 1941.07,
    "max_actual": 26851,
    "max_predicted": 12443,
    "min_actual": 1239,
    "min_predicted": 1580
  },
  "predictions": {
    "actual": [5999.0, 1650.0, 4743.0, ...],
    "predicted": [5617.15, 2468.31, 5973.26, ...]
  },
  "performance_level": "poor",
  "overfitting_risk": "high"
}
```

**응답 필드**

**기본 정보**
- `tourist_code` (string): 관광지 코드
- `korean_name` (string): 관광지 한글 이름

**학습 데이터 성능 지표 (`train_metrics`)**
- `MAE` (float): 평균 절대 오차 (Mean Absolute Error)
- `MSE` (float): 평균 제곱 오차 (Mean Squared Error)
- `RMSE` (float): 평균 제곱근 오차 (Root Mean Squared Error)
- `R²` (float): 결정계수 (R-squared, 0-1 사이, 높을수록 좋음)
- `MAPE` (float): 평균 절대 백분율 오차 (Mean Absolute Percentage Error, %)

**테스트 데이터 성능 지표 (`test_metrics`)**
- 동일한 구조로 테스트 데이터에 대한 성능 지표

**통계 정보 (`stats`)**
- `train_size` (integer): 학습 데이터 샘플 수
- `test_size` (integer): 테스트 데이터 샘플 수
- `feature_count` (integer): 사용된 피처 수
- `actual_mean` (float): 실제 방문자 수 평균
- `actual_std` (float): 실제 방문자 수 표준편차
- `predicted_mean` (float): 예측 방문자 수 평균
- `predicted_std` (float): 예측 방문자 수 표준편차
- `max_actual` (integer): 실제 방문자 수 최대값
- `max_predicted` (integer): 예측 방문자 수 최대값
- `min_actual` (integer): 실제 방문자 수 최소값
- `min_predicted` (integer): 예측 방문자 수 최소값

**예측 데이터 (`predictions`)**
- `actual` (array): 실제 방문자 수 배열 (scatter plot용)
- `predicted` (array): 예측 방문자 수 배열 (scatter plot용)

**성능 평가**
- `performance_level` (string): 성능 등급
  - `"excellent"`: 0.7 ≤ R² < 0.9 또는 R² ≥ 0.9
  - `"good"`: 0.5 ≤ R² < 0.7
  - `"fair"`: 0.3 ≤ R² < 0.5
  - `"poor"`: R² < 0.3
- `overfitting_risk` (string): 과적합 위험도
  - `"low"`: 학습/테스트 R² 차이 ≤ 0.1
  - `"medium"`: 0.1 < 차이 ≤ 0.2
  - `"high"`: 차이 > 0.2

**에러 응답**

**404 Not Found** - 관광지 코드를 찾을 수 없음
```json
{
  "detail": "알 수 없는 관광지 코드: invalid_code"
}
```

**503 Service Unavailable** - 모델 파일이 없음
```json
{
  "detail": "모델 파일을 찾을 수 없습니다: /path/to/model.pkl"
}
```

**500 Internal Server Error** - 서버 내부 오류
```json
{
  "detail": "평가 중 오류 발생: {에러 메시지}"
}
```

---

### 7. 모든 관광지 모델 성능 평가

#### `GET /api/evaluate-all`

모든 관광지 모델의 성능을 평가하고 시각화에 필요한 데이터를 반환합니다.

**요청**
```http
GET /api/evaluate-all HTTP/1.1
Host: localhost:8000
```

**응답 (200 OK)**
```json
{
  "results": [
    {
      "tourist_code": "changdeok_palace",
      "korean_name": "창덕궁",
      "train_metrics": { ... },
      "test_metrics": { ... },
      "stats": { ... },
      "predictions": { ... },
      "performance_level": "poor",
      "overfitting_risk": "high"
    },
    // ... 나머지 관광지 평가 결과
  ],
  "errors": [],
  "summary": {
    "total_models": 7,
    "average_r2": 0.1330,
    "average_mae": 3101.28,
    "average_rmse": 5697.39,
    "average_mape": 93.52,
    "performance_distribution": {
      "excellent": 0,
      "good": 0,
      "fair": 0,
      "poor": 7
    },
    "overfitting_distribution": {
      "low": 0,
      "medium": 0,
      "high": 7
    }
  },
  "timestamp": "2025-12-21T21:28:49.171941"
}
```

**응답 필드**

**결과 (`results`)**
- `results` (array): 성공한 평가 결과 배열
  - 각 요소는 단일 관광지 평가 응답과 동일한 구조

**에러 (`errors`)**
- `errors` (array): 평가 실패한 관광지 정보
  - `tourist_code` (string): 관광지 코드
  - `korean_name` (string): 관광지 한글 이름
  - `error` (string): 에러 메시지

**요약 통계 (`summary`)**
- `total_models` (integer): 평가된 모델 수
- `average_r2` (float): 평균 R² 점수
- `average_mae` (float): 평균 MAE
- `average_rmse` (float): 평균 RMSE
- `average_mape` (float): 평균 MAPE
- `performance_distribution` (object): 성능 등급별 분포
  - `excellent` (integer): excellent 등급 모델 수
  - `good` (integer): good 등급 모델 수
  - `fair` (integer): fair 등급 모델 수
  - `poor` (integer): poor 등급 모델 수
- `overfitting_distribution` (object): 과적합 위험도별 분포
  - `low` (integer): low 위험 모델 수
  - `medium` (integer): medium 위험 모델 수
  - `high` (integer): high 위험 모델 수

**타임스탬프**
- `timestamp` (string): 평가 시각 (ISO 8601 형식)

**에러 응답**

이 엔드포인트는 개별 관광지 평가 실패 시에도 전체 요청이 실패하지 않습니다. 실패한 관광지는 `errors` 배열에 포함됩니다.

**에러가 있는 경우 응답 예시 (200 OK)**
```json
{
  "results": [
    {
      "tourist_code": "changdeok_palace",
      "korean_name": "창덕궁",
      ...
    }
  ],
  "errors": [
    {
      "tourist_code": "gyeongbok_palace",
      "korean_name": "경복궁",
      "error": "모델 파일을 찾을 수 없습니다: /path/to/model.pkl"
    }
  ],
  "summary": { ... },
  "timestamp": "2025-12-21T21:28:49.171941"
}
```

---

## 사용 가능한 관광지 코드

| 코드 | 한글 이름 | 최대 수용 인원 |
|------|----------|---------------|
| `changdeok_palace` | 창덕궁 | 119,765 |
| `changgyeong_palace` | 창경궁 | 47,126 |
| `deoksugung_palace` | 덕수궁 | 20,401 |
| `gyeongbok_palace` | 경복궁 | 94,070 |
| `jongmyo_shrine` | 종묘 | 40,652 |
| `seoul_arts_center` | 예술의전당 | 50,734 |
| `seoul_grand_park` | 서울대공원 | 1,984,065 |

---

## 예제 요청

### cURL 예제

```bash
# 단일 관광지 예측
curl http://localhost:8000/api/predict/changdeok_palace

# 모든 관광지 예측
curl http://localhost:8000/api/predict-all

# 관광지 목록 조회
curl http://localhost:8000/api/tourist-sites

# 단일 관광지 모델 평가
curl http://localhost:8000/api/evaluate/changdeok_palace

# 모든 관광지 모델 평가
curl http://localhost:8000/api/evaluate-all

# 헬스 체크
curl http://localhost:8000/api/health
```

### Python 예제

```python
import requests

BASE_URL = "http://localhost:8000"

response = requests.get(f"{BASE_URL}/api/tourist-sites")
sites = response.json()["sites"]
print(f"총 {len(sites)}개 관광지")

response = requests.get(f"{BASE_URL}/api/predict/changdeok_palace")
prediction = response.json()
print(f"창덕궁 예상 방문자: {prediction['창덕궁']['predicted_visitors']}명")

response = requests.get(f"{BASE_URL}/api/predict-all")
all_predictions = response.json()
print(f"예측 완료: {len(all_predictions['predictions'])}개 관광지")

response = requests.get(f"{BASE_URL}/api/evaluate/changdeok_palace")
evaluation = response.json()
print(f"테스트 R²: {evaluation['test_metrics']['R²']:.4f}")
print(f"성능 등급: {evaluation['performance_level']}")
print(f"과적합 위험: {evaluation['overfitting_risk']}")
```

### JavaScript 예제

```javascript
const BASE_URL = "http://localhost:8000";

async function getTouristSites() {
  const response = await fetch(`${BASE_URL}/api/tourist-sites`);
  const data = await response.json();
  console.log(`총 ${data.sites.length}개 관광지`);
  return data.sites;
}

async function predictSingle(touristCode) {
  const response = await fetch(`${BASE_URL}/api/predict/${touristCode}`);
  const data = await response.json();
  return data;
}

async function evaluateModel(touristCode) {
  const response = await fetch(`${BASE_URL}/api/evaluate/${touristCode}`);
  const data = await response.json();
  return data;
}

(async () => {
  const sites = await getTouristSites();
  const prediction = await predictSingle("changdeok_palace");
  const evaluation = await evaluateModel("changdeok_palace");
  
  console.log("예측:", prediction);
  console.log("평가 R²:", evaluation.test_metrics["R²"]);
})();
```

---

## 에러 코드

| HTTP 상태 코드 | 설명 |
|---------------|------|
| 200 | 성공 |
| 404 | 리소스를 찾을 수 없음 (잘못된 관광지 코드, 모델 파일 없음) |
| 500 | 서버 내부 오류 |
| 503 | 서비스 사용 불가 (모델 파일 없음) |

---

## CORS 설정

백엔드는 다음 도메인에서의 요청을 허용합니다:
- `http://localhost:5173` (Vite 기본 포트)
- `http://localhost:3000` (React 기본 포트)

추가 도메인을 허용하려면 `backend/main.py`의 CORS 설정을 수정하세요.

---

## 성능 지표 설명

### R² (결정계수)
- **범위**: -∞ ~ 1
- **의미**: 모델이 데이터를 얼마나 잘 설명하는지 나타내는 지표
- **해석**: 1에 가까울수록 좋음, 0에 가까우면 평균 수준, 음수면 평균보다 나쁨

### MAE (평균 절대 오차)
- **단위**: 명 (방문자 수)
- **의미**: 예측값과 실제값의 평균 차이
- **해석**: 값이 작을수록 좋음

### RMSE (평균 제곱근 오차)
- **단위**: 명 (방문자 수)
- **의미**: 큰 오차에 더 큰 가중치를 주는 오차 지표
- **해석**: 값이 작을수록 좋음

### MAPE (평균 절대 백분율 오차)
- **단위**: %
- **의미**: 오차를 백분율로 나타낸 지표
- **해석**: 값이 작을수록 좋음

---

## 참고사항

1. **모델 학습 필요**: 예측 및 평가 API를 사용하려면 먼저 모델을 학습해야 합니다.
   ```bash
   python scripts/train_models.py
   ```

2. **실시간 데이터**: 예측 API는 실시간 기상 데이터와 대기환경 데이터를 사용합니다.
   - 기상청 API 키 (`KMA_API_KEY`) 필요
   - 서울시 대기환경 API 키 (`SEOUL_AIR_QUALITY_API_KEY`) 필요

3. **데이터베이스**: 평가 API는 SQLite 데이터베이스의 학습 데이터를 사용합니다.
   - 데이터베이스 경로: `data/processed/tourist_data.db`

4. **모델 타입**: 기본값은 XGBoost이며, 환경변수로 변경 가능합니다.
   ```bash
   MODEL_TYPE=random_forest python scripts/train_models.py
   ```
