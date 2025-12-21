"""
모델 성능 평가 및 진단 스크립트

모든 관광지별 모델의 성능을 평가하고 상세한 진단 리포트를 생성합니다.

Usage:
    python scripts/evaluate_models.py
"""
import sys
import warnings
from pathlib import Path

import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    mean_absolute_percentage_error
)

sys.path.append(str(Path(__file__).parent.parent))

from ml_service.config import MLConfig
from ml_service.data_loader import load_tourist_data
from sklearn.model_selection import train_test_split

TOURIST_SITES = MLConfig.TOURIST_SITES
MODELS_SAVED_DIR = MLConfig.MODELS_SAVED_DIR
MODEL_FILES = MLConfig.MODEL_FILES

MODEL_CONFIG = {
    "n_estimators": 48,
    "learning_rate": 0.1,
    "max_depth": 5,
    "random_state": 42,
    "test_size": 0.2
}

warnings.simplefilter("ignore")


def evaluate_model(tourist_code: str) -> dict:
    """
    관광지별 모델 성능 평가
    
    Args:
        tourist_code: 관광지 코드 (예: "changdeok_palace")
    
    Returns:
        dict: 평가 결과 (지표 및 통계)
    """
    if tourist_code not in TOURIST_SITES:
        raise ValueError(f"알 수 없는 관광지 코드: {tourist_code}")
    
    site_info = TOURIST_SITES[tourist_code]
    korean_name = site_info["korean_name"]
    
    # 모델 파일 확인
    model_filename = MODEL_FILES[tourist_code]
    model_path = MODELS_SAVED_DIR / model_filename
    
    if not model_path.exists():
        return {
            "error": f"모델 파일을 찾을 수 없습니다: {model_path}",
            "tourist_code": tourist_code,
            "korean_name": korean_name
        }
    
    # 데이터 로드
    X, y = load_tourist_data(korean_name)
    
    # 결측값 처리
    X = X.fillna(0)
    mask = ~y.isnull()
    X = X[mask]
    y = y[mask]
    
    # 데이터 분할 (학습 시와 동일한 random_state 사용)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=MODEL_CONFIG["test_size"],
        random_state=MODEL_CONFIG["random_state"]
    )
    
    # 모델 로드
    pipeline = joblib.load(model_path)
    
    # 예측
    y_train_pred = pipeline.predict(X_train)
    y_test_pred = pipeline.predict(X_test)
    
    # 지표 계산
    train_metrics = {
        "MAE": mean_absolute_error(y_train, y_train_pred),
        "MSE": mean_squared_error(y_train, y_train_pred),
        "RMSE": np.sqrt(mean_squared_error(y_train, y_train_pred)),
        "R²": r2_score(y_train, y_train_pred),
        "MAPE": mean_absolute_percentage_error(y_train, y_train_pred) * 100
    }
    
    test_metrics = {
        "MAE": mean_absolute_error(y_test, y_test_pred),
        "MSE": mean_squared_error(y_test, y_test_pred),
        "RMSE": np.sqrt(mean_squared_error(y_test, y_test_pred)),
        "R²": r2_score(y_test, y_test_pred),
        "MAPE": mean_absolute_percentage_error(y_test, y_test_pred) * 100
    }
    
    # 통계 정보
    stats = {
        "train_size": len(X_train),
        "test_size": len(X_test),
        "feature_count": len(X.columns),
        "actual_mean": float(y_test.mean()),
        "actual_std": float(y_test.std()),
        "predicted_mean": float(y_test_pred.mean()),
        "predicted_std": float(y_test_pred.std()),
        "max_actual": int(y_test.max()),
        "max_predicted": int(y_test_pred.max()),
        "min_actual": int(y_test.min()),
        "min_predicted": int(y_test_pred.min())
    }
    
    return {
        "tourist_code": tourist_code,
        "korean_name": korean_name,
        "train_metrics": train_metrics,
        "test_metrics": test_metrics,
        "stats": stats,
        "predictions": {
            "actual": y_test.values.tolist(),
            "predicted": y_test_pred.tolist()
        }
    }


def print_evaluation_report(results: dict):
    """평가 결과를 보기 좋게 출력"""
    korean_name = results["korean_name"]
    train_metrics = results["train_metrics"]
    test_metrics = results["test_metrics"]
    stats = results["stats"]
    
    print(f"\n{'='*70}")
    print(f"[EVALUATION] {korean_name} 모델 성능 평가")
    print(f"{'='*70}")
    
    print(f"\n[TRAIN] 학습 데이터 성능 ({stats['train_size']}개 샘플):")
    print(f"   R² Score:        {train_metrics['R²']:>8.4f}")
    print(f"   MAE (평균 절대 오차): {train_metrics['MAE']:>8.2f}명")
    print(f"   RMSE (평균 제곱근 오차): {train_metrics['RMSE']:>8.2f}명")
    print(f"   MAPE (평균 절대 백분율 오차): {train_metrics['MAPE']:>7.2f}%")
    
    print(f"\n[TEST] 테스트 데이터 성능 ({stats['test_size']}개 샘플):")
    print(f"   R² Score:        {test_metrics['R²']:>8.4f}")
    print(f"   MAE (평균 절대 오차): {test_metrics['MAE']:>8.2f}명")
    print(f"   RMSE (평균 제곱근 오차): {test_metrics['RMSE']:>8.2f}명")
    print(f"   MAPE (평균 절대 백분율 오차): {test_metrics['MAPE']:>7.2f}%")
    
    print(f"\n[STATS] 통계 정보:")
    print(f"   피처 수:         {stats['feature_count']}개")
    print(f"   실제 평균:       {stats['actual_mean']:>8.2f}명")
    print(f"   예측 평균:       {stats['predicted_mean']:>8.2f}명")
    print(f"   실제 표준편차:   {stats['actual_std']:>8.2f}명")
    print(f"   예측 표준편차:   {stats['predicted_std']:>8.2f}명")
    print(f"   실제 범위:       {stats['min_actual']:,} ~ {stats['max_actual']:,}명")
    print(f"   예측 범위:       {stats['min_predicted']:,} ~ {stats['max_predicted']:,}명")
    
    # 성능 평가
    print(f"\n[ANALYSIS] 성능 평가:")
    if test_metrics['R²'] >= 0.9:
        print("   [GOOD] 우수한 성능 (R² ≥ 0.9)")
    elif test_metrics['R²'] >= 0.7:
        print("   [OK] 양호한 성능 (0.7 ≤ R² < 0.9)")
    elif test_metrics['R²'] >= 0.5:
        print("   [WARNING] 보통 성능 (0.5 ≤ R² < 0.7)")
    else:
        print("   [ERROR] 낮은 성능 (R² < 0.5) - 모델 개선 필요")
    
    if abs(train_metrics['R²'] - test_metrics['R²']) > 0.2:
        print("   [WARNING] 과적합 가능성 (학습/테스트 R² 차이가 큼)")
    elif train_metrics['R²'] > test_metrics['R²']:
        print("   [WARNING] 약간의 과적합 가능성")
    else:
        print("   [GOOD] 일반화 성능 양호")


def evaluate_all_models():
    """모든 관광지 모델 평가"""
    print("\n" + "="*70)
    print("[INFO] 모든 관광지 모델 성능 평가 시작")
    print("="*70)
    
    all_results = []
    failed = []
    
    for tourist_code in TOURIST_SITES.keys():
        try:
            result = evaluate_model(tourist_code)
            if "error" in result:
                failed.append(result)
                print(f"\n[ERROR] {result['korean_name']}: {result['error']}")
            else:
                all_results.append(result)
                print_evaluation_report(result)
        except Exception as e:
            korean_name = TOURIST_SITES[tourist_code]["korean_name"]
            failed.append({
                "tourist_code": tourist_code,
                "korean_name": korean_name,
                "error": str(e)
            })
            print(f"\n[ERROR] {korean_name}: 평가 실패 - {e}")
    
    # 요약 리포트
    print("\n" + "="*70)
    print("[SUMMARY] 전체 모델 성능 요약")
    print("="*70)
    
    if all_results:
        print(f"\n[SUCCESS] 성공적으로 평가된 모델: {len(all_results)}개")
        print(f"\n{'관광지':<15} {'테스트 R²':<12} {'테스트 MAE':<15} {'테스트 RMSE':<15} {'테스트 MAPE':<15}")
        print("-" * 70)
        
        for result in sorted(all_results, key=lambda x: x['test_metrics']['R²'], reverse=True):
            korean_name = result['korean_name']
            metrics = result['test_metrics']
            print(f"{korean_name:<15} {metrics['R²']:>11.4f} {metrics['MAE']:>14.2f}명 {metrics['RMSE']:>14.2f}명 {metrics['MAPE']:>14.2f}%")
        
        # 평균 성능
        avg_r2 = np.mean([r['test_metrics']['R²'] for r in all_results])
        avg_mae = np.mean([r['test_metrics']['MAE'] for r in all_results])
        avg_rmse = np.mean([r['test_metrics']['RMSE'] for r in all_results])
        avg_mape = np.mean([r['test_metrics']['MAPE'] for r in all_results])
        
        print("-" * 70)
        print(f"{'평균':<15} {avg_r2:>11.4f} {avg_mae:>14.2f}명 {avg_rmse:>14.2f}명 {avg_mape:>14.2f}%")
    
    if failed:
        print(f"\n[ERROR] 평가 실패한 모델: {len(failed)}개")
        for f in failed:
            print(f"   - {f['korean_name']}: {f['error']}")
    
    return all_results, failed


if __name__ == "__main__":
    try:
        evaluate_all_models()
    except KeyboardInterrupt:
        print("\n\n[WARNING] 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

