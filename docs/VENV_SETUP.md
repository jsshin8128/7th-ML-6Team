# 가상환경 설정

## 생성 및 활성화

```bash
# 가상환경 생성
python3 -m venv venv

# 활성화
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

## 패키지 설치

```bash
pip install -r ml_service/requirements.txt
pip install -r backend/requirements.txt
```

## 시스템 Python 사용 시

시스템 Python을 직접 사용하려면:

```bash
python3 -m pip install --user -r ml_service/requirements.txt
python3 -m pip install --user -r backend/requirements.txt
```

**주의**: 가상환경 사용을 권장합니다.

## 비활성화

```bash
deactivate
```
