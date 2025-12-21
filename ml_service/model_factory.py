"""
모델 팩토리 모듈
다양한 모델 타입을 쉽게 교체할 수 있도록 팩토리 패턴 구현
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import warnings

warnings.simplefilter("ignore")


class BaseModelFactory(ABC):
    """모델 팩토리 베이스 클래스"""
    
    @abstractmethod
    def create_model(self, config: Dict[str, Any]):
        """
        모델 인스턴스 생성
        
        Args:
            config: 모델 하이퍼파라미터 딕셔너리
        
        Returns:
            학습 가능한 모델 인스턴스
        """
        pass
    
    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """
        기본 하이퍼파라미터 반환
        
        Returns:
            기본 설정 딕셔너리
        """
        pass


class XGBoostModelFactory(BaseModelFactory):
    """XGBoost 모델 팩토리"""
    
    def create_model(self, config: Dict[str, Any]):
        """XGBoost 모델 생성"""
        import xgboost as xgb
        
        return xgb.XGBRegressor(
            objective=config.get("objective", "reg:squarederror"),
            n_estimators=config.get("n_estimators", 48),
            learning_rate=config.get("learning_rate", 0.1),
            max_depth=config.get("max_depth", 5),
            random_state=config.get("random_state", 42),
            **config.get("extra_params", {})
        )
    
    def get_default_config(self) -> Dict[str, Any]:
        """XGBoost 기본 설정"""
        return {
            "objective": "reg:squarederror",
            "n_estimators": 48,
            "learning_rate": 0.1,
            "max_depth": 5,
            "random_state": 42
        }


class RandomForestModelFactory(BaseModelFactory):
    """Random Forest 모델 팩토리"""
    
    def create_model(self, config: Dict[str, Any]):
        """Random Forest 모델 생성"""
        from sklearn.ensemble import RandomForestRegressor
        
        return RandomForestRegressor(
            n_estimators=config.get("n_estimators", 100),
            max_depth=config.get("max_depth", 10),
            min_samples_split=config.get("min_samples_split", 2),
            min_samples_leaf=config.get("min_samples_leaf", 1),
            random_state=config.get("random_state", 42),
            **config.get("extra_params", {})
        )
    
    def get_default_config(self) -> Dict[str, Any]:
        """Random Forest 기본 설정"""
        return {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "random_state": 42
        }


class LightGBMModelFactory(BaseModelFactory):
    """LightGBM 모델 팩토리"""
    
    def create_model(self, config: Dict[str, Any]):
        """LightGBM 모델 생성"""
        try:
            import lightgbm as lgb  # type: ignore[import-untyped]
        except ImportError:
            raise ImportError(
                "lightgbm이 설치되지 않았습니다. "
                "설치하려면: pip install lightgbm"
            )
        
        return lgb.LGBMRegressor(
            objective=config.get("objective", "regression"),
            n_estimators=config.get("n_estimators", 100),
            learning_rate=config.get("learning_rate", 0.1),
            max_depth=config.get("max_depth", 5),
            random_state=config.get("random_state", 42),
            **config.get("extra_params", {})
        )
    
    def get_default_config(self) -> Dict[str, Any]:
        """LightGBM 기본 설정"""
        return {
            "objective": "regression",
            "n_estimators": 100,
            "learning_rate": 0.1,
            "max_depth": 5,
            "random_state": 42
        }


class CatBoostModelFactory(BaseModelFactory):
    """CatBoost 모델 팩토리"""
    
    def create_model(self, config: Dict[str, Any]):
        """CatBoost 모델 생성"""
        try:
            import catboost as cb  # type: ignore[import-untyped]
        except ImportError:
            raise ImportError(
                "catboost가 설치되지 않았습니다. "
                "설치하려면: pip install catboost"
            )
        
        return cb.CatBoostRegressor(
            iterations=config.get("iterations", 100),
            learning_rate=config.get("learning_rate", 0.1),
            depth=config.get("depth", 5),
            random_state=config.get("random_state", 42),
            verbose=config.get("verbose", False),
            **config.get("extra_params", {})
        )
    
    def get_default_config(self) -> Dict[str, Any]:
        """CatBoost 기본 설정"""
        return {
            "iterations": 100,
            "learning_rate": 0.1,
            "depth": 5,
            "random_state": 42,
            "verbose": False
        }


class ModelFactory:
    """모델 팩토리 메인 클래스"""
    
    # 지원하는 모델 팩토리 등록 (필수 모델만 기본 등록)
    _factories: Dict[str, BaseModelFactory] = {
        "xgboost": XGBoostModelFactory(),
        "random_forest": RandomForestModelFactory(),
    }
    
    @classmethod
    def _register_optional_factories(cls):
        """선택적 의존성을 가진 모델 팩토리 등록"""
        # LightGBM 등록 시도
        try:
            import lightgbm  # type: ignore[import-untyped]  # noqa: F401
            if "lightgbm" not in cls._factories:
                cls._factories["lightgbm"] = LightGBMModelFactory()
        except ImportError:
            pass
        
        # CatBoost 등록 시도
        try:
            import catboost  # type: ignore[import-untyped]  # noqa: F401
            if "catboost" not in cls._factories:
                cls._factories["catboost"] = CatBoostModelFactory()
        except ImportError:
            pass
    
    @classmethod
    def register_factory(cls, model_type: str, factory: BaseModelFactory):
        """
        새로운 모델 팩토리 등록
        
        Args:
            model_type: 모델 타입 이름 (예: "my_custom_model")
            factory: BaseModelFactory를 상속한 팩토리 인스턴스
        """
        cls._factories[model_type] = factory
    
    @classmethod
    def create_model(cls, model_type: str, config: Optional[Dict[str, Any]] = None):
        """
        모델 타입에 따라 모델 인스턴스 생성
        
        Args:
            model_type: 모델 타입 (예: "xgboost", "random_forest", "lightgbm", "catboost")
            config: 모델 하이퍼파라미터 딕셔너리 (None이면 기본값 사용)
        
        Returns:
            학습 가능한 모델 인스턴스
        
        Raises:
            ValueError: 지원하지 않는 모델 타입인 경우
        """
        if model_type not in cls._factories:
            available_types = ", ".join(cls._factories.keys())
            raise ValueError(
                f"지원하지 않는 모델 타입: {model_type}\n"
                f"사용 가능한 모델 타입: {available_types}"
            )
        
        factory = cls._factories[model_type]
        
        if config is None:
            config = factory.get_default_config()
        else:
            # 기본 설정과 사용자 설정 병합
            default_config = factory.get_default_config()
            default_config.update(config)
            config = default_config
        
        return factory.create_model(config)
    
    @classmethod
    def get_available_models(cls) -> list:
        """
        사용 가능한 모델 타입 목록 반환
        
        Returns:
            모델 타입 리스트
        """
        return list(cls._factories.keys())
    
    @classmethod
    def get_default_config(cls, model_type: str) -> Dict[str, Any]:
        """
        특정 모델 타입의 기본 설정 반환
        
        Args:
            model_type: 모델 타입
        
        Returns:
            기본 설정 딕셔너리
        
        Raises:
            ValueError: 지원하지 않는 모델 타입인 경우
        """
        if model_type not in cls._factories:
            available_types = ", ".join(cls._factories.keys())
            raise ValueError(
                f"지원하지 않는 모델 타입: {model_type}\n"
                f"사용 가능한 모델 타입: {available_types}"
            )
        
        return cls._factories[model_type].get_default_config()


# 초기화 시 선택적 팩토리 등록 (클래스 정의 후)
ModelFactory._register_optional_factories()
