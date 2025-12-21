# 프로젝트 아키텍처

## 구조

```
7th-ML-6Team/
├── ml_service/          # ML 서비스 패키지
│   ├── config.py        # 설정 관리
│   ├── predictor.py     # 예측 서비스
│   ├── data_loader.py   # 데이터 로더
│   └── requirements.txt
│
├── backend/             # FastAPI 백엔드
│   ├── main.py          # API 엔드포인트
│   └── requirements.txt
│
├── models/saved/        # 학습된 모델 (.pkl)
├── pkl/                 # 스케일러 (.pkl)
├── data/                # 데이터베이스
└── scripts/             # 학습/유틸리티 스크립트
```

## 계층 구조

### ML Service (`ml_service/`)
- `PredictionService`: 예측 서비스 클래스
- `MLConfig`: 설정 관리
- `data_loader`: 데이터베이스 로더

**사용**:
```python
from ml_service import PredictionService
service = PredictionService()
result = service.predict("changdeok_palace")
```

### Backend (`backend/`)
- FastAPI 애플리케이션
- ML 서비스를 싱글톤으로 사용
- CORS 설정
- Swagger UI: `/docs`

**주요 API 엔드포인트:**
- 예측: `/api/predict/{tourist_code}`, `/api/predict-all`
- 평가: `/api/evaluate/{tourist_code}`, `/api/evaluate-all`
- 정보: `/api/tourist-sites`, `/api/health`

### Scripts (`scripts/`)
- `train_models.py`: 모델 학습 스크립트
- `evaluate_models.py`: 모델 평가 스크립트
- `backup_db.py`: 데이터베이스 백업/복원 유틸리티

**평가 함수 사용**:
```python
from scripts.evaluate_models import evaluate_model
result = evaluate_model("changdeok_palace")
```

## 데이터 흐름

### 예측 요청 흐름
```
API 요청 (클라이언트)
    ↓
FastAPI 백엔드 (/api/predict/{code})
    ↓
PredictionService.predict()
    ↓
├─→ 실시간 데이터 수집 (서울시 API, 기상청 API)
├─→ 데이터 전처리 (스케일러 로드, 피처 생성)
├─→ 모델 로드 (캐싱)
└─→ 예측 수행 → 결과 반환
```

### 평가 요청 흐름
```
API 요청 (클라이언트)
    ↓
FastAPI 백엔드 (/api/evaluate/{code})
    ↓
evaluate_model() (scripts/evaluate_models.py)
    ↓
├─→ 데이터 로드 (load_tourist_data)
├─→ 모델 로드 (joblib)
├─→ 예측 수행 (학습/테스트 데이터)
├─→ 성능 지표 계산 (R², MAE, RMSE, MAPE)
└─→ 시각화 데이터 생성 → 결과 반환
```

## 설정

### 환경 변수 (`.env`)
```bash
SEOUL_AIR_QUALITY_API_KEY=your_key
KMA_API_KEY=your_key
```

### 캐싱
- 스케일러 캐싱: `_scalers_cache`
- 모델 캐싱: `_pipelines_cache`
- 서비스 인스턴스: 백엔드 싱글톤
