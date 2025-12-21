"""
예측 서비스 모듈
실시간 데이터 수집 및 예측 로직
"""
import json
import warnings
from datetime import datetime, timedelta
from typing import Dict

import numpy as np
import pandas as pd
import requests
import joblib

from ml_service.config import MLConfig
from ml_service.data_loader import load_tourist_data

warnings.simplefilter("ignore")


class PredictionService:
    """예측 서비스 클래스"""
    
    def __init__(self):
        """초기화 및 설정 검증"""
        MLConfig.validate()
        self._scalers_cache = None
        self._pipelines_cache = {}
    
    @staticmethod
    def calculate_discomfort_index(temp_celsius: float, humidity_percent: float) -> float:
        """불쾌지수 계산"""
        return 0.81 * temp_celsius + 0.01 * humidity_percent * (0.99 * temp_celsius - 14.3) + 46.3
    
    @staticmethod
    def month_to_season(month: int) -> int:
        """월을 계절로 변환 (0: 봄, 1: 여름, 2: 가을, 3: 겨울)"""
        if month in [3, 4, 5]:
            return 0  # 봄
        elif month in [6, 7, 8]:
            return 1  # 여름
        elif month in [9, 10, 11]:
            return 2  # 가을
        else:
            return 3  # 겨울
    
    def fetch_air_quality_data(self, district_code: str) -> dict:
        """서울시 자치구별 실시간 대기환경 데이터 수집"""
        url = f"{MLConfig.SEOUL_AIR_QUALITY_API_BASE_URL}/{MLConfig.SEOUL_AIR_QUALITY_API_KEY}/{MLConfig.AIR_QUALITY_API_TYPE}/{MLConfig.AIR_QUALITY_API_SERVICE}/{MLConfig.AIR_QUALITY_API_START_INDEX}/{MLConfig.AIR_QUALITY_API_END_INDEX}/{district_code}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            contents = json.loads(response.text)
            
            if 'ListAirQualityByDistrictService' not in contents:
                raise ValueError("API 응답 형식이 올바르지 않습니다.")
            
            api_response = contents['ListAirQualityByDistrictService']
            
            if 'RESULT' in api_response:
                result_code = api_response['RESULT'].get('CODE', '')
                if result_code != 'INFO-000':
                    error_msg = api_response['RESULT'].get('MESSAGE', '알 수 없는 오류')
                    raise RuntimeError(f"API 오류: {error_msg} (코드: {result_code})")
            
            if 'row' not in api_response:
                raise ValueError("API 응답에 데이터가 없습니다.")
            
            if isinstance(api_response['row'], list):
                row_data = api_response['row'][0]
            else:
                row_data = api_response['row']
            
            msrmt_ymd = str(row_data.get('MSRMT_YMD', ''))
            if len(msrmt_ymd) >= 14:
                datetime_str = f"{msrmt_ymd[:4]}-{msrmt_ymd[4:6]}-{msrmt_ymd[6:8]} {msrmt_ymd[8:10]}:{msrmt_ymd[10:12]}"
                datetime_obj = pd.to_datetime(datetime_str)
            else:
                datetime_obj = pd.Timestamp.now()
            
            return {
                'pm10': float(row_data.get('PM', 0)),
                'datetime': datetime_obj
            }
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API 요청 실패: {e}")
        except (KeyError, ValueError, TypeError) as e:
            raise RuntimeError(f"데이터 파싱 실패: {e}")
    
    def fetch_weather_api_data(self, nx: int, ny: int) -> dict:
        """기상청 API에서 초단기실황 데이터 수집"""
        now = datetime.now()
        current_hour = now.hour
        base_time = f"{current_hour:02d}00"
        base_date = now.strftime("%Y%m%d")
        
        if current_hour == 0:
            base_date = (now - timedelta(days=1)).strftime("%Y%m%d")
            base_time = "2300"
        
        url = f"{MLConfig.KMA_API_BASE_URL}/{MLConfig.KMA_API_SERVICE}"
        params = {
            "ServiceKey": MLConfig.KMA_API_KEY,
            "pageNo": MLConfig.KMA_API_PAGE_NO,
            "numOfRows": MLConfig.KMA_API_NUM_OF_ROWS,
            "dataType": MLConfig.KMA_API_DATA_TYPE,
            "base_date": base_date,
            "base_time": base_time,
            "nx": nx,
            "ny": ny
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            contents = json.loads(response.text)
            
            if 'response' not in contents:
                raise ValueError("API 응답 형식이 올바르지 않습니다.")
            
            response_data = contents['response']
            
            if 'header' in response_data:
                result_code = response_data['header'].get('resultCode', '')
                if result_code != '00':
                    result_msg = response_data['header'].get('resultMsg', '알 수 없는 오류')
                    raise RuntimeError(f"기상청 API 오류: {result_msg} (코드: {result_code})")
            
            if 'body' not in response_data or 'items' not in response_data['body']:
                raise ValueError("API 응답에 데이터가 없습니다.")
            
            items = response_data['body']['items']['item']
            if not items:
                raise ValueError("API 응답에 아이템이 없습니다.")
            
            data_dict = {}
            for item in items:
                category = item.get('category', '')
                obsr_value = item.get('obsrValue', '0')
                try:
                    data_dict[category] = float(obsr_value)
                except (ValueError, TypeError):
                    data_dict[category] = 0.0
            
            return {
                'temperature': data_dict.get('T1H', 20.0),
                'humidity': data_dict.get('REH', 60.0),
                'windspeed': data_dict.get('WSD', 2.0),
                'rainfall': data_dict.get('RN1', 0.0),
                'datetime': pd.Timestamp.now()
            }
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"기상청 API 요청 실패: {e}")
        except (KeyError, ValueError, TypeError) as e:
            raise RuntimeError(f"기상청 데이터 파싱 실패: {e}")
    
    def fetch_weather_data(self, district_code: str, nx: int, ny: int) -> dict:
        """대기환경 API와 기상청 API를 모두 호출하여 통합 데이터 반환"""
        air_data = self.fetch_air_quality_data(district_code)
        
        try:
            weather_data = self.fetch_weather_api_data(nx, ny)
        except Exception as e:
            warnings.warn(f"기상청 API 호출 실패, 기본값 사용: {e}")
            weather_data = {
                'temperature': 20.0,
                'humidity': 60.0,
                'windspeed': 2.0,
                'rainfall': 0.0,
                'datetime': air_data['datetime']
            }
        
        return {
            'pm10': air_data['pm10'],
            'windspeed': weather_data['windspeed'],
            'temperature': weather_data['temperature'],
            'humidity': weather_data['humidity'],
            'rainfall': weather_data['rainfall'],
            'datetime': weather_data['datetime']
        }
    
    def load_scalers(self) -> dict:
        """모든 스케일러 로드 (캐싱)"""
        if self._scalers_cache is None:
            scalers = {}
            for key, filename in MLConfig.SCALER_FILES.items():
                scaler_path = MLConfig.SCALERS_DIR / filename
                if scaler_path.exists():
                    scalers[key] = joblib.load(scaler_path)
                else:
                    warnings.warn(f"스케일러 파일을 찾을 수 없습니다: {scaler_path}")
            self._scalers_cache = scalers
        return self._scalers_cache
    
    def load_pipeline(self, tourist_code: str):
        """저장된 Pipeline 모델 로드 (캐싱)"""
        if tourist_code not in self._pipelines_cache:
            if tourist_code not in MLConfig.MODEL_FILES:
                raise ValueError(f"알 수 없는 관광지 코드: {tourist_code}")
            
            model_filename = MLConfig.MODEL_FILES[tourist_code]
            model_path = MLConfig.MODELS_SAVED_DIR / model_filename
            
            if not model_path.exists():
                raise FileNotFoundError(
                    f"모델 파일을 찾을 수 없습니다: {model_path}\n"
                    f"먼저 'python scripts/train_models.py'를 실행하여 모델을 학습하세요."
                )
            
            self._pipelines_cache[tourist_code] = joblib.load(model_path)
        
        return self._pipelines_cache[tourist_code]
    
    def get_feature_columns(self, tourist_code: str) -> list:
        """관광지별 Feature 컬럼 목록 가져오기"""
        site_info = MLConfig.TOURIST_SITES[tourist_code]
        korean_name = site_info["korean_name"]
        
        X, _ = load_tourist_data(korean_name)
        return list(X.columns)
    
    def prepare_features(self, weather_data: dict, scalers: dict) -> pd.DataFrame:
        """실시간 기상 데이터를 모델 입력 형식으로 변환"""
        date = weather_data['datetime']
        weekday = date.weekday()
        season = self.month_to_season(date.month)
        
        # 스케일링
        scaled_pm10 = scalers['tinydust'].transform(np.array([[weather_data['pm10']]]))[0][0]
        scaled_windspeed = scalers['windspeed'].transform(np.array([[weather_data['windspeed']]]))[0][0]
        scaled_temperature = scalers['temperature'].transform(np.array([[weather_data['temperature']]]))[0][0]
        scaled_humidity = scalers['humidity'].transform(np.array([[weather_data['humidity']]]))[0][0]
        scaled_rainfall = scalers['rainfall'].transform(np.array([[weather_data['rainfall']]]))[0][0]
        
        # 불쾌지수 계산 및 스케일링
        scaled_discomfort = 0.01 * self.calculate_discomfort_index(scaled_temperature, scaled_humidity)
        
        # Feature 딕셔너리 생성
        feature_dict = {
            '미세먼지(PM10)': scaled_pm10,
            '불쾌지수': scaled_discomfort,
            'Windspeed(m/s)': scaled_windspeed,
            'Rainfall(mm)': scaled_rainfall,
            'weekday_0': 1 if weekday == 0 else 0,
            'weekday_1': 1 if weekday == 1 else 0,
            'weekday_2': 1 if weekday == 2 else 0,
            'weekday_3': 1 if weekday == 3 else 0,
            'weekday_4': 1 if weekday == 4 else 0,
            'weekday_5': 1 if weekday == 5 else 0,
            'weekday_6': 1 if weekday == 6 else 0,
            'season_0': 1 if season == 0 else 0,
            'season_1': 1 if season == 1 else 0,
            'season_2': 1 if season == 2 else 0,
            'season_3': 1 if season == 3 else 0
        }
        
        return pd.DataFrame([feature_dict])
    
    def predict(self, tourist_code: str) -> Dict[str, Dict[str, float]]:
        """
        Pipeline 모델을 사용한 예측
        
        Args:
            tourist_code: 관광지 코드 (예: "changdeok_palace")
        
        Returns:
            dict: 예측 결과 {"관광지명": {"predicted_visitors": int, "congestion_level": float}}
        """
        if tourist_code not in MLConfig.TOURIST_SITES:
            raise ValueError(f"알 수 없는 관광지 코드: {tourist_code}")
        
        site_info = MLConfig.TOURIST_SITES[tourist_code]
        korean_name = site_info["korean_name"]
        max_capacity = site_info["max_capacity"]
        district_code = site_info["district_code"]
        nx = site_info["nx"]
        ny = site_info["ny"]
        
        # Pipeline 모델 로드
        pipeline = self.load_pipeline(tourist_code)
        
        # Feature 컬럼 순서 가져오기
        feature_columns = self.get_feature_columns(tourist_code)
        
        # 실시간 데이터 수집 및 전처리
        weather_data = self.fetch_weather_data(district_code, nx, ny)
        scalers = self.load_scalers()
        features_df = self.prepare_features(weather_data, scalers)
        
        # 컬럼 순서 맞추기
        features_df = features_df[feature_columns]
        
        # 예측
        predicted_visitors = int(pipeline.predict(features_df)[0])
        congestion_level = (predicted_visitors / max_capacity) * 100
        
        return {
            korean_name: {
                "predicted_visitors": predicted_visitors,
                "congestion_level": round(congestion_level, 2)
            }
        }


# 편의 함수 (하위 호환성)
def predict(tourist_code: str) -> Dict[str, Dict[str, float]]:
    """
    편의 함수: PredictionService 인스턴스를 생성하여 예측
    
    Note: 프로덕션 환경에서는 PredictionService 인스턴스를 재사용하는 것을 권장합니다.
    """
    service = PredictionService()
    return service.predict(tourist_code)

