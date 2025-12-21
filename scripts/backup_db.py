"""
데이터베이스 백업/복원 유틸리티

작업용 DB를 백업하거나 백업 DB에서 복원합니다.

Usage:
    python scripts/backup_db.py backup   # 작업용 DB를 백업
    python scripts/backup_db.py restore  # 백업에서 복원
"""
import sys
import shutil
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from ml_service.config import MLConfig

DB_PATH = MLConfig.DB_PATH
DB_BACKUP_PATH = MLConfig.DATA_BACKUP_DIR / "tourist_data_backup.db"
DATA_BACKUP_DIR = MLConfig.DATA_BACKUP_DIR


def backup_database():
    """
    작업용 DB를 백업 DB로 복사
    
    Raises:
        FileNotFoundError: 작업용 DB가 없을 경우
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(f"작업용 데이터베이스를 찾을 수 없습니다: {DB_PATH}")
    
    # 백업 디렉토리 생성
    DATA_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # 기존 백업 삭제
    if DB_BACKUP_PATH.exists():
        DB_BACKUP_PATH.unlink()
        print(f"[INFO] 기존 백업 삭제: {DB_BACKUP_PATH}")
    
    # 백업 생성
    shutil.copy2(DB_PATH, DB_BACKUP_PATH)
    print(f"[INFO] 백업 완료: {DB_PATH.name} → {DB_BACKUP_PATH.name}")
    print(f"[INFO] 위치: {DB_BACKUP_PATH}")


def restore_database():
    """
    백업 DB에서 작업용 DB로 복원
    
    Raises:
        FileNotFoundError: 백업 DB가 없을 경우
    """
    if not DB_BACKUP_PATH.exists():
        raise FileNotFoundError(f"백업 데이터베이스를 찾을 수 없습니다: {DB_BACKUP_PATH}")
    
    # 기존 작업용 DB 삭제
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"[INFO] 기존 작업용 DB 삭제: {DB_PATH}")
    
    # 복원
    shutil.copy2(DB_BACKUP_PATH, DB_PATH)
    print(f"[INFO] 복원 완료: {DB_BACKUP_PATH.name} → {DB_PATH.name}")
    print(f"[INFO] 위치: {DB_PATH}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="데이터베이스 백업/복원")
    parser.add_argument(
        "action",
        choices=["backup", "restore"],
        help="backup: 작업용 DB를 백업, restore: 백업에서 복원"
    )
    
    args = parser.parse_args()
    
    try:
        if args.action == "backup":
            backup_database()
        elif args.action == "restore":
            restore_database()
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        sys.exit(1)

