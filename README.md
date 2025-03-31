# 식단 플래너 (Google Calendar 연동)

Google Calendar와 연동되는 식단 플래너 애플리케이션입니다. 이 프로그램을 사용하여 식단 계획을 수립하고 Google Calendar에 자동으로 일정을 추가할 수 있습니다.

## 주요 기능

- 단일 날짜 식단 추가
- 여러 날짜에 동일한 식단 추가
- 반복 식단 일정 추가 (매일, 매주, 매월)
- 식단 조회
- 자주 사용하는 식단 템플릿 관리
- 식사 시간 및 기간 설정 커스터마이징

## 설치 방법

### 필요한 패키지 설치

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client tzdata customtkinter tkcalendar
```

### Google Calendar API 설정

1. [Google Cloud Platform](https://console.cloud.google.com/) 에서 프로젝트를 생성합니다.
2. Google Calendar API를 활성화합니다.
3. OAuth 2.0 클라이언트 ID를 생성합니다.
4. 다운로드한 JSON 파일의 이름을 `client_secret.json`으로 변경하고 애플리케이션 폴더에 저장합니다.

## 실행 방법

```bash
python main.py
```

첫 실행 시 Google 계정 인증 창이 표시됩니다. 인증 후에는 `token.json` 파일이 생성되어 이후 자동 로그인됩니다.

## EXE 파일로 변환

### PyInstaller 설치

```bash
pip install pyinstaller
```

### EXE 파일 생성

```bash
pyinstaller --onefile --windowed --icon=icon.ico --name="식단플래너" --add-data "client_secret.json;." main.py
```

옵션 설명:
- `--onefile`: 단일 실행 파일로 생성
- `--windowed`: 콘솔 창 없이 실행
- `--icon`: 애플리케이션 아이콘 설정
- `--name`: 실행 파일 이름 설정
- `--add-data`: 추가 데이터 파일 포함

### 주의사항

- CustomTkinter 사용 시 추가 옵션이 필요할 수 있습니다:
  ```bash
  --add-data "C:/Python3x/Lib/site-packages/customtkinter;customtkinter/"
  ```
  실제 경로는 Python 설치 위치에 따라 다릅니다.

- PyInstaller에서 모든 의존성을 제대로 인식하지 못할 경우 다음과 같이 설정:
  ```bash
  --hidden-import=babel.numbers
  ```

## 사용 팁

1. 처음 실행 시 '식단' 이름의 Google 캘린더가 없다면 미리 생성해두세요.
2. 자주 사용하는 식단은 템플릿으로 저장하여 편리하게 이용하세요.
3. 식사 시간을 개인 일정에 맞게 조정할 수 있습니다.

## 문제 해결

- 인증 오류: `token.json` 파일을 삭제하고 재실행하여 다시 인증하세요.
- 캘린더를 찾을 수 없음: Google Calendar에 '식단' 이름의 캘린더가 있는지 확인하세요.
- 일정이 추가되지 않음: 인터넷 연결 및 캘린더 권한을 확인하세요.

## 개발 정보

- 프로그래밍 언어: Python 3.9 이상
- 주요 라이브러리: Google Calendar API, CustomTkinter, tkcalendar
- 개발 구조: 
  - `meal_planner_core.py`: 핵심 기능
  - `meal_planner_gui.py`: GUI 구현
  - `main.py`: 메인 실행 파일 