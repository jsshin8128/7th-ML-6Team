# 모델 교체 가이드

이 문서는 프로젝트에서 사용하는 머신러닝 모델을 교체하는 방법을 설명합니다.

## 개요

프로젝트는 **팩토리 패턴**을 사용하여 모델 교체를 용이하게 설계되었습니다. 코드 수정 없이 환경변수나 설정 파일만으로 모델을 변경할 수 있습니다.

## 지원하는 모델 타입

### 기본 제공 모델

1. **xgboost** (기본값)
   - XGBoost 회귀 모델
   - 설치: `pip install xgboost`

2. **random_forest**
   - Scikit-learn의 Random Forest 회귀 모델
   - 설치: `pip install scikit-learn` (이미 설치되어 있음)

### 선택적 모델

3. **lightgbm**
   - LightGBM 회귀 모델
   - 설치: `pip install lightgbm`

4. **catboost**
   - CatBoost 회귀 모델
   - 설치: `pip install catboost`

## 모델 교체 방법

### 방법 1: 환경변수 사용 (권장)

학습 시 환경변수로 모델 타입을 지정합니다:

```bash
# Random Forest 사용
MODEL_TYPE=random_forest python scripts/train_models.py

# LightGBM 사용
MODEL_TYPE=lightgbm python scripts/train_models.py

# CatBoost 사용
MODEL_TYPE=catboost python scripts/train_models.py
```

### 방법 2: .env 파일 사용

프로젝트 루트의 `.env` 파일에 다음을 추가:

```env
MODEL_TYPE=random_forest
```

그 후 학습 스크립트 실행:

```bash
python scripts/train_models.py
```

### 방법 3: 코드에서 직접 변경

`ml_service/config.py` 파일의 `MODEL_TYPE` 값을 수정:

```python
# 기본값: "xgboost"
MODEL_TYPE = os.getenv("MODEL_TYPE", "random_forest").lower()
```

## 모델 하이퍼파라미터 설정

모델의 하이퍼파라미터는 `ml_service/config.py`의 `MODEL_CONFIG`에서 설정할 수 있습니다:

```python
MODEL_CONFIG = {
    "n_estimators": int(os.getenv("MODEL_N_ESTIMATORS", "48")),
    "learning_rate": float(os.getenv("MODEL_LEARNING_RATE", "0.1")),
    "max_depth": int(os.getenv("MODEL_MAX_DEPTH", "5")),
    "random_state": int(os.getenv("MODEL_RANDOM_STATE", "42")),
    "test_size": float(os.getenv("MODEL_TEST_SIZE", "0.2"))
}
```

환경변수로도 변경 가능:

```bash
MODEL_TYPE=random_forest \
MODEL_N_ESTIMATORS=100 \
MODEL_MAX_DEPTH=10 \
python scripts/train_models.py
```

## 커스텀 모델 추가

새로운 모델 타입을 추가하려면 다음 단계를 따르세요:

### 1. 모델 팩토리 클래스 생성

`ml_service/model_factory.py`에 새로운 팩토리 클래스를 추가:

```python
class MyCustomModelFactory(BaseModelFactory):
    """커스텀 모델 팩토리"""
    
    def create_model(self, config: Dict[str, Any]):
        """커스텀 모델 생성"""
        from my_custom_package import MyCustomRegressor
        
        return MyCustomRegressor(
            param1=config.get("param1", 10),
            param2=config.get("param2", 0.1),
            random_state=config.get("random_state", 42),
            **config.get("extra_params", {})
        )
    
    def get_default_config(self) -> Dict[str, Any]:
        """커스텀 모델 기본 설정"""
        return {
            "param1": 10,
            "param2": 0.1,
            "random_state": 42
        }
```

### 2. 팩토리 등록

`ModelFactory` 클래스의 `_factories` 딕셔너리에 추가하거나, 런타임에 등록:

```python
from ml_service.model_factory import ModelFactory, MyCustomModelFactory

# 런타임 등록
ModelFactory.register_factory("my_custom_model", MyCustomModelFactory())
```

### 3. 사용

등록한 모델 타입을 사용하여 학습:

```bash
MODEL_TYPE=my_custom_model python scripts/train_models.py
```

## 모델 아키텍처

### 팩토리 패턴 구조

```
ml_service/
├── model_factory.py      # 모델 팩토리 및 베이스 클래스
├── config.py             # 모델 타입 및 설정 관리
└── predictor.py          # 예측 서비스 (모델 로드)

scripts/
└── train_models.py       # 모델 학습 (팩토리 사용)
```

### 데이터 흐름

1. **학습 단계** (`scripts/train_models.py`):
   - `MLConfig.MODEL_TYPE`에서 모델 타입 읽기
   - `ModelFactory.create_model()`로 모델 인스턴스 생성
   - Pipeline으로 래핑하여 학습 및 저장

2. **예측 단계** (`ml_service/predictor.py`):
   - 저장된 Pipeline 파일 로드 (모델 타입과 무관)
   - Pipeline을 사용하여 예측 수행

## 주의사항

1. **모델 호환성**: 저장된 모델 파일은 학습 시 사용한 모델 타입과 일치해야 합니다. 다른 타입의 모델로 학습한 파일을 로드하면 오류가 발생할 수 있습니다.

2. **하이퍼파라미터**: 각 모델 타입마다 지원하는 하이퍼파라미터가 다를 수 있습니다. 모델별 문서를 참조하세요.

3. **의존성**: 선택적 모델(lightgbm, catboost)을 사용하려면 해당 패키지를 설치해야 합니다.

4. **성능 비교**: 모델을 교체한 후 성능을 비교하여 최적의 모델을 선택하세요.

## 예제: 모델 성능 비교

여러 모델의 성능을 비교하려면:

```bash
# XGBoost 학습
MODEL_TYPE=xgboost python scripts/train_models.py

# Random Forest 학습
MODEL_TYPE=random_forest python scripts/train_models.py

# LightGBM 학습
MODEL_TYPE=lightgbm python scripts/train_models.py

# 각 모델 평가
python scripts/evaluate_models.py

# API를 통한 평가 (프론트엔드 시각화용)
curl http://localhost:8000/api/evaluate-all
```

## 문제 해결

### 모델 타입을 찾을 수 없음

```
ValueError: 지원하지 않는 모델 타입: invalid_model
```

**해결**: 사용 가능한 모델 타입 확인:
```python
from ml_service.model_factory import ModelFactory
print(ModelFactory.get_available_models())
```

### 모델 패키지가 설치되지 않음

```
ImportError: lightgbm이 설치되지 않았습니다.
```

**해결**: 해당 패키지 설치:
```bash
pip install lightgbm
```

### 저장된 모델과 다른 타입 사용

학습 시 사용한 모델 타입과 다른 타입으로 예측하려고 하면 오류가 발생할 수 있습니다. 항상 동일한 모델 타입으로 학습한 모델 파일을 사용하세요.
