@echo off
echo ========================================
echo   YouTube 直播即時翻譯器 - 打包程式
echo ========================================
echo.

REM 檢查虛擬環境
if not exist "venv" (
    echo 錯誤: 請先執行 install.bat 安裝環境
    pause
    exit /b 1
)

REM 啟動虛擬環境
call venv\Scripts\activate.bat

REM 檢查 PyInstaller
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安裝 PyInstaller...
    pip install pyinstaller
)

REM 執行打包腳本
python build.py

deactivate 