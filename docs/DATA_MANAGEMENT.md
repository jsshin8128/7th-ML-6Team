# 데이터 관리

## 데이터베이스 구조

- **백업 DB**: `data/backup/tourist_data_backup.db` (읽기 전용, 원본)
- **작업용 DB**: `data/processed/tourist_data.db` (실제 사용)

## 명령어

### 백업에서 복원
```bash
python scripts/backup_db.py restore
```

### 작업용 DB 백업
```bash
python scripts/backup_db.py backup
```

## 사용

- 모델 학습: `python scripts/train_models.py`
- 모델 평가: `python scripts/evaluate_models.py` (콘솔 출력)
- API를 통한 평가: `GET /api/evaluate/{tourist_code}` 또는 `GET /api/evaluate-all` (JSON 응답, 프론트엔드 시각화용)
