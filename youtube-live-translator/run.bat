@echo off
title YouTube Live Translator
echo ===================================
echo YouTube Live Translator
echo 即時直播翻譯字幕疊層應用程式
echo ===================================
echo.

:: 檢查Python是否已安裝
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 錯誤: 未找到Python，請先安裝Python 3.8或更高版本
    echo 下載地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 檢查虛擬環境是否存在
if not exist "venv" (
    echo 首次執行，正在創建虛擬環境...
    python -m venv venv
)

:: 啟動虛擬環境
call venv\Scripts\activate.bat

:: 檢查依賴是否已安裝
pip show PyQt5 >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安裝依賴套件，這可能需要幾分鐘...
    pip install -r requirements.txt
)

:: 執行主程式
echo.
echo 啟動應用程式...
python main.py

:: 如果程式崩潰，暫停以查看錯誤訊息
if %errorlevel% neq 0 (
    echo.
    echo 程式發生錯誤！
    pause
)

deactivate