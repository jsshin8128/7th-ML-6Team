"""
ML Service Package
머신러닝 예측 서비스를 제공하는 패키지
"""
from ml_service.predictor import PredictionService
from ml_service.config import MLConfig
from ml_service.model_factory import ModelFactory

__version__ = "1.0.0"
__all__ = ["PredictionService", "MLConfig", "ModelFactory"]

