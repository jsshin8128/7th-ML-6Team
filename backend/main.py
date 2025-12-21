"""
FastAPI 백엔드 서버
서울 관광지 혼잡도 예측을 위한 REST API 제공
"""
import sys
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))

from ml_service import PredictionService, MLConfig
from scripts.evaluate_models import evaluate_model

prediction_service = PredictionService()


def calculate_performance_level(r2: float) -> str:
    """R² 점수에 따른 성능 등급 계산"""
    if r2 < 0:
        return "poor"
    elif r2 < 0.3:
        return "poor"
    elif r2 < 0.5:
        return "fair"
    elif r2 < 0.7:
        return "good"
    elif r2 < 0.9:
        return "excellent"
    else:
        return "excellent"


def calculate_overfitting_risk(train_r2: float, test_r2: float) -> str:
    """학습/테스트 R² 차이에 따른 과적합 위험도 계산"""
    r2_diff = abs(train_r2 - test_r2)
    if r2_diff > 0.2:
        return "high"
    elif r2_diff > 0.1:
        return "medium"
    else:
        return "low"


class TouristSite(BaseModel):
    code: str
    korean_name: str
    max_capacity: int
    district_code: str
    nx: int
    ny: int

class TouristSitesResponse(BaseModel):
    sites: List[TouristSite]

class PredictionResponse(BaseModel):
    predicted_visitors: int
    congestion_level: float

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str


app = FastAPI(
    title="KOREA TOUR GUIDE API",
    version="1.0.0",
    description="서울 내 주요 관광지의 실시간 혼잡도를 예측하는 API",
    docs_url="/docs",
    tags_metadata=[
        {
            "name": "info",
            "description": "API 정보 및 헬스 체크",
        },
        {
            "name": "tourist-sites",
            "description": "관광지 정보 조회",
        },
        {
            "name": "predictions",
            "description": "혼잡도 예측",
        },
        {
            "name": "evaluation",
            "description": "모델 성능 평가",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["info"])
async def root():
    """
    API 루트 엔드포인트
    
    사용 가능한 모든 API 엔드포인트 목록을 반환합니다.
    """
    return {
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


@app.get(
    "/api/tourist-sites",
    response_model=TouristSitesResponse,
    tags=["tourist-sites"],
    summary="모든 관광지 정보 조회",
    description="서울 내 주요 관광지 7곳의 정보를 반환합니다."
)
async def get_tourist_sites():
    """
    모든 관광지 정보를 반환합니다.
    
    - **code**: 관광지 코드 (영문)
    - **korean_name**: 관광지 한글 이름
    - **max_capacity**: 최대 수용 인원
    - **district_code**: 자치구 코드
    - **nx, ny**: 기상청 격자 좌표
    """
    sites = []
    for code, info in MLConfig.TOURIST_SITES.items():
        sites.append({
            "code": code,
            "korean_name": info["korean_name"],
            "max_capacity": info["max_capacity"],
            "district_code": info["district_code"],
            "nx": info["nx"],
            "ny": info["ny"]
        })
    return {"sites": sites}


@app.get(
    "/api/predict/{tourist_code}",
    tags=["predictions"],
    summary="단일 관광지 혼잡도 예측",
    description="특정 관광지의 예상 방문자 수와 혼잡도를 예측합니다.",
    responses={
        200: {
            "description": "예측 성공",
            "content": {
                "application/json": {
                    "example": {
                        "창덕궁": {
                            "predicted_visitors": 7394,
                            "congestion_level": 6.17
                        }
                    }
                }
            }
        },
        404: {
            "description": "관광지 코드를 찾을 수 없음",
            "content": {
                "application/json": {
                    "example": {"detail": "알 수 없는 관광지 코드: invalid_code"}
                }
            }
        },
        503: {
            "description": "서비스 사용 불가 (모델 파일 없음)",
        },
        500: {
            "description": "서버 내부 오류",
        }
    }
)
async def predict_single(tourist_code: str):
    """
    단일 관광지의 혼잡도를 예측합니다.
    
    - **tourist_code**: 관광지 코드 (예: changdeok_palace)
    
    실시간 기상 데이터와 대기환경 데이터를 기반으로 XGBoost 모델을 사용하여 예측합니다.
    
    **사용 가능한 관광지 코드:**
    - changdeok_palace (창덕궁)
    - changgyeong_palace (창경궁)
    - deoksugung_palace (덕수궁)
    - gyeongbok_palace (경복궁)
    - jongmyo_shrine (종묘)
    - seoul_arts_center (예술의전당)
    - seoul_grand_park (서울대공원)
    """
    try:
        result = prediction_service.predict(tourist_code)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예측 중 오류 발생: {str(e)}")


@app.get(
    "/api/predict-all",
    tags=["predictions"],
    summary="모든 관광지 혼잡도 예측",
    description="모든 관광지의 예상 방문자 수와 혼잡도를 한 번에 예측합니다."
)
async def predict_all():
    """
    모든 관광지의 혼잡도를 한 번에 예측합니다.
    
    각 관광지별로 예측을 수행하며, 실패한 경우 errors 배열에 포함됩니다.
    
    **응답 구조:**
    - **predictions**: 성공한 예측 결과 (관광지명: 예측값)
    - **errors**: 실패한 관광지 정보 (있는 경우)
    - **timestamp**: 예측 시각
    """
    results = {}
    errors = []
    
    for tourist_code in MLConfig.TOURIST_SITES.keys():
        try:
            result = prediction_service.predict(tourist_code)
            results.update(result)
        except Exception as e:
            korean_name = MLConfig.TOURIST_SITES[tourist_code]["korean_name"]
            errors.append({
                "site": korean_name,
                "code": tourist_code,
                "error": str(e)
            })
    
    return {
        "predictions": results,
        "errors": errors,
        "timestamp": datetime.now().isoformat()
    }


@app.get(
    "/api/health",
    response_model=HealthResponse,
    tags=["info"],
    summary="헬스 체크",
    description="API 서버의 상태를 확인합니다."
)
async def health_check():
    """
    API 서버의 헬스 상태를 확인합니다.
    
    서버가 정상적으로 작동 중이면 "healthy" 상태를 반환합니다.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "KOREA TOUR GUIDE API"
    }


@app.get(
    "/api/evaluate/{tourist_code}",
    tags=["evaluation"],
    summary="단일 관광지 모델 성능 평가",
    description="특정 관광지 모델의 성능을 평가하고 시각화에 필요한 데이터를 반환합니다."
)
async def evaluate_single(tourist_code: str):
    """
    단일 관광지 모델의 성능을 평가합니다.
    
    - **tourist_code**: 관광지 코드 (예: changdeok_palace)
    
    **응답 구조:**
    - **train_metrics**: 학습 데이터 성능 지표 (R², MAE, RMSE, MAPE)
    - **test_metrics**: 테스트 데이터 성능 지표
    - **stats**: 통계 정보 (평균, 표준편차, 범위 등)
    - **predictions**: 실제값과 예측값 배열 (scatter plot용)
    - **performance_level**: 성능 등급 (excellent, good, fair, poor)
    - **overfitting_risk**: 과적합 위험도 (low, medium, high)
    """
    try:
        result = evaluate_model(tourist_code)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        train_r2 = result["train_metrics"]["R²"]
        test_r2 = result["test_metrics"]["R²"]
        
        result["performance_level"] = calculate_performance_level(test_r2)
        result["overfitting_risk"] = calculate_overfitting_risk(train_r2, test_r2)
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"평가 중 오류 발생: {str(e)}")


@app.get(
    "/api/evaluate-all",
    tags=["evaluation"],
    summary="모든 관광지 모델 성능 평가",
    description="모든 관광지 모델의 성능을 평가하고 시각화에 필요한 데이터를 반환합니다."
)
async def evaluate_all():
    """
    모든 관광지 모델의 성능을 평가합니다.
    
    각 관광지별로 평가를 수행하며, 실패한 경우 errors 배열에 포함됩니다.
    
    **응답 구조:**
    - **results**: 성공한 평가 결과 배열
    - **errors**: 실패한 관광지 정보 (있는 경우)
    - **summary**: 전체 요약 통계 (평균 R², 평균 MAE 등)
    - **timestamp**: 평가 시각
    """
    all_results = []
    errors = []
    
    for tourist_code in MLConfig.TOURIST_SITES.keys():
        try:
            result = evaluate_model(tourist_code)
            if "error" in result:
                errors.append({
                    "tourist_code": result["tourist_code"],
                    "korean_name": result["korean_name"],
                    "error": result["error"]
                })
            else:
                train_r2 = result["train_metrics"]["R²"]
                test_r2 = result["test_metrics"]["R²"]
                
                result["performance_level"] = calculate_performance_level(test_r2)
                result["overfitting_risk"] = calculate_overfitting_risk(train_r2, test_r2)
                all_results.append(result)
        except Exception as e:
            korean_name = MLConfig.TOURIST_SITES[tourist_code]["korean_name"]
            errors.append({
                "tourist_code": tourist_code,
                "korean_name": korean_name,
                "error": str(e)
            })
    
    if all_results:
        summary = {
            "total_models": len(all_results),
            "average_r2": float(np.mean([r["test_metrics"]["R²"] for r in all_results])),
            "average_mae": float(np.mean([r["test_metrics"]["MAE"] for r in all_results])),
            "average_rmse": float(np.mean([r["test_metrics"]["RMSE"] for r in all_results])),
            "average_mape": float(np.mean([r["test_metrics"]["MAPE"] for r in all_results])),
            "performance_distribution": {
                "excellent": len([r for r in all_results if r["performance_level"] == "excellent"]),
                "good": len([r for r in all_results if r["performance_level"] == "good"]),
                "fair": len([r for r in all_results if r["performance_level"] == "fair"]),
                "poor": len([r for r in all_results if r["performance_level"] == "poor"])
            },
            "overfitting_distribution": {
                "low": len([r for r in all_results if r["overfitting_risk"] == "low"]),
                "medium": len([r for r in all_results if r["overfitting_risk"] == "medium"]),
                "high": len([r for r in all_results if r["overfitting_risk"] == "high"])
            }
        }
    else:
        summary = {
            "total_models": 0,
            "average_r2": 0.0,
            "average_mae": 0.0,
            "average_rmse": 0.0,
            "average_mape": 0.0,
            "performance_distribution": {},
            "overfitting_distribution": {}
        }
    
    return {
        "results": all_results,
        "errors": errors,
        "summary": summary,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
