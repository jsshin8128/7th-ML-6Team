"""
ML Service 설정 관리
환경변수 및 경로 설정
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 프로젝트 루트 디렉토리 (ml_service의 부모 디렉토리)
PROJECT_ROOT = Path(__file__).parent.parent


class MLConfig:
    """ML 서비스 설정 클래스"""
    
    # 디렉토리 경로
    DATA_DIR = PROJECT_ROOT / "data"
    DATA_PROCESSED_DIR = DATA_DIR / "processed"
    DATA_BACKUP_DIR = DATA_DIR / "backup"
    MODELS_SAVED_DIR = PROJECT_ROOT / "models" / "saved"
    SCALERS_DIR = PROJECT_ROOT / "pkl"
    
    # 데이터베이스 경로
    DB_PATH = DATA_PROCESSED_DIR / "tourist_data.db"
    
    # 관광지 정보
    TOURIST_SITES = {
        "changdeok_palace": {
            "korean_name": "창덕궁",
            "max_capacity": 119765,
            "district_code": "111123",
            "nx": 60,
            "ny": 127
        },
        "changgyeong_palace": {
            "korean_name": "창경궁",
            "max_capacity": 47126,
            "district_code": "111123",
            "nx": 60,
            "ny": 127
        },
        "deoksugung_palace": {
            "korean_name": "덕수궁",
            "max_capacity": 20401,
            "district_code": "111121",
            "nx": 60,
            "ny": 127
        },
        "gyeongbok_palace": {
            "korean_name": "경복궁",
            "max_capacity": 94070,
            "district_code": "111123",
            "nx": 60,
            "ny": 127
        },
        "jongmyo_shrine": {
            "korean_name": "종묘",
            "max_capacity": 40652,
            "district_code": "111123",
            "nx": 60,
            "ny": 127
        },
        "seoul_arts_center": {
            "korean_name": "예술의전당",
            "max_capacity": 50734,
            "district_code": "111262",
            "nx": 60,
            "ny": 125
        },
        "seoul_grand_park": {
            "korean_name": "서울대공원",
            "max_capacity": 1984065,
            "district_code": "111262",
            "nx": 61,
            "ny": 124
        }
    }
    
    # API 설정
    SEOUL_AIR_QUALITY_API_BASE_URL = "http://openapi.seoul.go.kr:8088"
    SEOUL_AIR_QUALITY_API_KEY = os.getenv("SEOUL_AIR_QUALITY_API_KEY")
    AIR_QUALITY_API_SERVICE = "ListAirQualityByDistrictService"
    AIR_QUALITY_API_START_INDEX = 1
    AIR_QUALITY_API_END_INDEX = 5
    AIR_QUALITY_API_TYPE = "json"
    
    KMA_API_BASE_URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"
    KMA_API_SERVICE = "getUltraSrtNcst"
    KMA_API_PAGE_NO = 1
    KMA_API_NUM_OF_ROWS = 10
    KMA_API_DATA_TYPE = "JSON"
    KMA_API_KEY = os.getenv("KMA_API_KEY")
    
    # 스케일러 파일명
    SCALER_FILES = {
        "humidity": "scaler_Humidity.pkl",
        "rainfall": "scaler_Rainfall.pkl",
        "temperature": "scaler_Temperature.pkl",
        "tinydust": "scaler_Tinydust.pkl",
        "windspeed": "scaler_Windspeed.pkl"
    }
    
    # 모델 파일명 매핑
    MODEL_FILES = {
        "changdeok_palace": "model_changdeok_palace.pkl",
        "changgyeong_palace": "model_changgyeong_palace.pkl",
        "deoksugung_palace": "model_deoksugung_palace.pkl",
        "gyeongbok_palace": "model_gyeongbok_palace.pkl",
        "jongmyo_shrine": "model_jongmyo_shrine.pkl",
        "seoul_arts_center": "model_seoul_arts_center.pkl",
        "seoul_grand_park": "model_seoul_grand_park.pkl"
    }
    
    # 모델 타입 설정 (환경변수로 변경 가능)
    # 사용 가능한 타입: "xgboost", "random_forest", "lightgbm", "catboost"
    MODEL_TYPE = os.getenv("MODEL_TYPE", "xgboost").lower()
    
    # 모델 하이퍼파라미터 설정
    # 각 관광지별로 다른 설정을 사용하려면 여기에 추가 가능
    MODEL_CONFIG = {
        "n_estimators": int(os.getenv("MODEL_N_ESTIMATORS", "48")),
        "learning_rate": float(os.getenv("MODEL_LEARNING_RATE", "0.1")),
        "max_depth": int(os.getenv("MODEL_MAX_DEPTH", "5")),
        "random_state": int(os.getenv("MODEL_RANDOM_STATE", "42")),
        "test_size": float(os.getenv("MODEL_TEST_SIZE", "0.2"))
    }
    
    @classmethod
    def validate(cls):
        """설정 유효성 검사"""
        if not cls.SEOUL_AIR_QUALITY_API_KEY:
            raise ValueError(
                "SEOUL_AIR_QUALITY_API_KEY가 설정되지 않았습니다. "
                ".env 파일을 생성하고 SEOUL_AIR_QUALITY_API_KEY를 설정하거나 "
                "환경 변수로 설정해주세요."
            )
        if not cls.KMA_API_KEY:
            raise ValueError(
                "KMA_API_KEY가 설정되지 않았습니다. "
                ".env 파일을 생성하고 KMA_API_KEY를 설정하거나 "
                "환경 변수로 설정해주세요."
            )

