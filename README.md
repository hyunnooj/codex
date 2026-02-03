# 파이썬 테트리스 게임

`pygame`로 만든 데스크톱 테트리스 게임입니다. 방향키로 이동하고 스페이스 바로 하드 드롭을 할 수 있습니다.

## 요구 사항

- Python 3.9+
- macOS/Windows/Linux

## 설치 방법

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 실행 방법

```bash
python tetris.py
```

## 조작 방법

- ← / →: 좌우 이동
- ↓: 빠르게 내리기
- ↑: 회전
- Space: 하드 드롭
- R: 게임 오버 후 재시작

## 프로젝트 구조

- `tetris.py`: 게임 로직 및 렌더링
- `requirements.txt`: 의존성 목록

## 참고

창이 열리지 않으면 그래픽 드라이버 업데이트 후 다시 실행하세요.
