@echo off
echo ========================================
echo   YouTube 直播即時翻譯器
echo ========================================
echo.

REM 檢查 Python 是否安裝
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 錯誤: 未檢測到 Python 安裝
    echo 請先安裝 Python 3.8 或更高版本
    echo 下載連結: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 檢查是否有虛擬環境
if not exist "venv" (
    echo 首次執行，正在創建虛擬環境...
    python -m venv venv
    echo.
)

REM 啟動虛擬環境
echo 正在啟動虛擬環境...
call venv\Scripts\activate.bat

REM 檢查並安裝依賴
echo.
echo 正在檢查依賴項...
pip show PyQt5 >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安裝依賴項，這可能需要幾分鐘...
    echo.
    REM 使用正確的方式升級 pip
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo.
    echo 依賴項安裝完成！
    echo.
)

REM 檢查 ffmpeg 是否安裝
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo 警告: 未檢測到 FFmpeg
    echo YouTube 音訊擷取需要 FFmpeg
    echo 請從以下連結下載並安裝:
    echo https://ffmpeg.org/download.html
    echo.
    pause
)

REM 啟動應用程式
echo.
echo 正在啟動應用程式...
echo.
python main.py

REM 如果程式崩潰，保持視窗開啟
if %errorlevel% neq 0 (
    echo.
    echo 應用程式發生錯誤！
    echo 錯誤代碼: %errorlevel%
    echo.
    pause
)

deactivate 