"""
모델 학습 및 Pipeline 저장 스크립트

모든 관광지별 모델을 학습하고 Pipeline으로 저장합니다.

Usage:
    python scripts/train_models.py
    
환경변수로 모델 타입 변경 가능:
    MODEL_TYPE=xgboost python scripts/train_models.py
    MODEL_TYPE=random_forest python scripts/train_models.py
    MODEL_TYPE=lightgbm python scripts/train_models.py
    MODEL_TYPE=catboost python scripts/train_models.py
"""
import sys
import warnings
from pathlib import Path

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

sys.path.append(str(Path(__file__).parent.parent))

from ml_service.config import MLConfig
from ml_service.data_loader import load_tourist_data
from ml_service.model_factory import ModelFactory

TOURIST_SITES = MLConfig.TOURIST_SITES
MODELS_SAVED_DIR = MLConfig.MODELS_SAVED_DIR
MODEL_FILES = MLConfig.MODEL_FILES
MODEL_TYPE = MLConfig.MODEL_TYPE
MODEL_CONFIG = MLConfig.MODEL_CONFIG

warnings.simplefilter("ignore")


def train_and_save_model(tourist_code: str) -> bool:
    """
    관광지별 모델 학습 및 Pipeline 저장
    
    Args:
        tourist_code: 관광지 코드 (예: "changdeok_palace")
    
    Returns:
        bool: 성공 여부
    """
    if tourist_code not in TOURIST_SITES:
        print(f"[ERROR] 알 수 없는 관광지 코드: {tourist_code}")
        return False
    
    site_info = TOURIST_SITES[tourist_code]
    korean_name = site_info["korean_name"]
    
    print(f"\n{'='*60}")
    print(f"[INFO] {korean_name} 모델 학습 시작")
    print(f"{'='*60}")
    
    try:
        # 데이터 로드
        print("[INFO] 데이터 로드 중...")
        X, y = load_tourist_data(korean_name)
        print(f"[INFO] 데이터 로드 완료: {len(X)}행, {len(X.columns)}개 피처")
        
        # 결측값 처리
        print("[INFO] 결측값 처리 중...")
        X = X.fillna(0)
        mask = ~y.isnull()
        X = X[mask]
        y = y[mask]
        print(f"[INFO] 결측값 처리 완료: {len(X)}행")
        
        # 데이터 분할
        print("[INFO] 데이터 분할 중...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=MODEL_CONFIG["test_size"], 
            random_state=MODEL_CONFIG["random_state"]
        )
        print(f"[INFO] 학습 데이터: {len(X_train)}행, 테스트 데이터: {len(X_test)}행")
        
        # 모델 생성 및 학습
        print(f"[INFO] 모델 타입: {MODEL_TYPE}")
        print("[INFO] 모델 학습 중...")
        
        # 모델 팩토리를 사용하여 모델 생성
        model_config = {
            "n_estimators": MODEL_CONFIG["n_estimators"],
            "learning_rate": MODEL_CONFIG["learning_rate"],
            "max_depth": MODEL_CONFIG["max_depth"],
            "random_state": MODEL_CONFIG["random_state"]
        }
        
        # XGBoost의 경우 objective 추가
        if MODEL_TYPE == "xgboost":
            model_config["objective"] = "reg:squarederror"
        
        model = ModelFactory.create_model(MODEL_TYPE, model_config)
        
        # Pipeline 생성 (향후 전처리 단계 추가 가능)
        pipeline = Pipeline([
            ('model', model)
        ])
        
        pipeline.fit(X_train, y_train)
        
        # 테스트 데이터로 평가
        train_score = pipeline.score(X_train, y_train)
        test_score = pipeline.score(X_test, y_test)
        print(f"[INFO] 학습 완료")
        print(f"[INFO] 학습 데이터 R²: {train_score:.4f}")
        print(f"[INFO] 테스트 데이터 R²: {test_score:.4f}")
        
        # 모델 저장 디렉토리 생성
        MODELS_SAVED_DIR.mkdir(parents=True, exist_ok=True)
        
        # Pipeline 저장
        model_filename = MODEL_FILES[tourist_code]
        model_path = MODELS_SAVED_DIR / model_filename
        
        joblib.dump(pipeline, model_path)
        print(f"[INFO] 모델 저장 완료: {model_path}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def train_all_models():
    """
    모든 관광지 모델 학습
    
    Returns:
        dict: 관광지 코드별 학습 성공 여부
    """
    print("\n" + "="*60)
    print("[INFO] 모든 관광지 모델 학습 시작")
    print(f"[INFO] 사용 모델 타입: {MODEL_TYPE}")
    print(f"[INFO] 사용 가능한 모델 타입: {', '.join(ModelFactory.get_available_models())}")
    print("="*60)
    
    results = {}
    for tourist_code in TOURIST_SITES.keys():
        success = train_and_save_model(tourist_code)
        results[tourist_code] = success
    
    # 결과 요약
    print("\n" + "="*60)
    print("[INFO] 학습 결과 요약")
    print("="*60)
    
    success_count = sum(results.values())
    total_count = len(results)
    
    for tourist_code, success in results.items():
        korean_name = TOURIST_SITES[tourist_code]["korean_name"]
        status = "[SUCCESS]" if success else "[FAILED]"
        print(f"  {korean_name}: {status}")
    
    print(f"\n총 {total_count}개 중 {success_count}개 성공")
    
    if success_count == total_count:
        print(f"\n[INFO] 모든 모델 학습이 완료되었습니다")
        print(f"[INFO] 저장 위치: {MODELS_SAVED_DIR}")
    else:
        print(f"\n[WARNING] {total_count - success_count}개 모델 학습 실패")
    
    return results


if __name__ == "__main__":
    train_all_models()

