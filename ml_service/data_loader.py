"""
데이터 로딩 모듈
SQLite 데이터베이스에서 관광지 데이터를 로드
"""
import pandas as pd
import sqlite3
from typing import Tuple
from ml_service.config import MLConfig


def load_tourist_data(tourist_name: str) -> Tuple[pd.DataFrame, pd.Series]:
    """
    SQLite 데이터베이스에서 관광지 데이터를 로드
    
    Args:
        tourist_name: 관광지 이름 (예: "창덕궁", "경복궁")
    
    Returns:
        tuple: (X: Feature DataFrame, y: Label Series)
    """
    if not MLConfig.DB_PATH.exists():
        raise FileNotFoundError(
            f"데이터베이스 파일을 찾을 수 없습니다: {MLConfig.DB_PATH}\n"
            "먼저 백업 DB에서 복원하세요: python scripts/backup_db.py restore"
        )
    
    # SQLite 연결
    conn = sqlite3.connect(str(MLConfig.DB_PATH))
    
    try:
        # 테이블에서 데이터 로드
        query = f"SELECT * FROM {tourist_name}"
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            raise ValueError(f"'{tourist_name}' 테이블에 데이터가 없습니다.")
        
        # Feature와 Label 분리
        X = df.drop(columns=[tourist_name])
        y = df[tourist_name]
        
        # 하드코딩된 피처 제거 (사용하지 않는 피처)
        features_to_remove = ['달러환율', 'total_7d_avg', '운항수_표준화']
        X = X.drop(columns=[col for col in features_to_remove if col in X.columns], errors='ignore')
        
        # 타입 확인 및 변환
        boolean_cols = ['weekday_0', 'weekday_1', 'weekday_2', 'weekday_3', 
                        'weekday_4', 'weekday_5', 'weekday_6',
                        'season_0', 'season_1', 'season_2', 'season_3']
        
        for col in boolean_cols:
            if col in X.columns:
                X[col] = X[col].astype(int)
        
        return X, y
        
    finally:
        conn.close()

