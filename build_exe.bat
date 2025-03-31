@echo off
echo ===== 식단 플래너 EXE 빌드 스크립트 =====

REM Python 환경 확인
python --version
if %ERRORLEVEL% neq 0 (
    echo Python이 설치되어 있지 않거나 PATH에 등록되지 않았습니다.
    exit /b 1
)

REM PyInstaller 설치 확인 및 설치
pip show pyinstaller > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo PyInstaller 설치 중...
    pip install pyinstaller
)

REM 필요한 패키지 설치
echo 필요한 패키지 설치 중...
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client tzdata customtkinter tkcalendar

REM CustomTkinter 경로 확인
for /f %%i in ('python -c "import os, customtkinter; print(os.path.dirname(customtkinter.__file__))"') do set CTK_PATH=%%i

echo CustomTkinter 경로: %CTK_PATH%

REM PyInstaller 실행
echo EXE 파일 빌드 중...
pyinstaller --onefile --windowed --clean ^
    --name="식단플래너" ^
    --add-data "client_secret.json;." ^
    --add-data "%CTK_PATH%;customtkinter/" ^
    --hidden-import babel.numbers ^
    main.py

echo.
echo 빌드 완료! dist 폴더의 식단플래너.exe 파일을 확인하세요.
echo.

pause 