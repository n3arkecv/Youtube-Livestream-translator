@echo off
title Build YouTube Live Translator EXE
echo ===================================
echo 建立 YouTube Live Translator EXE
echo ===================================
echo.

:: 檢查虛擬環境
if not exist "venv" (
    echo 錯誤: 請先執行 run.bat 來設定環境
    pause
    exit /b 1
)

:: 啟動虛擬環境
call venv\Scripts\activate.bat

:: 安裝PyInstaller
echo 檢查PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo 安裝PyInstaller...
    pip install pyinstaller
)

:: 清理舊的建置
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

:: 建立exe
echo.
echo 開始建立執行檔...
echo 這可能需要幾分鐘時間...
echo.

:: 使用spec檔案建置
if exist "build.spec" (
    pyinstaller build.spec
) else (
    :: 如果沒有spec檔案，使用命令列參數
    pyinstaller --windowed --onefile ^
        --name "YouTube Live Translator" ^
        --add-data "assets;assets" ^
        --hidden-import whisper ^
        --hidden-import torch ^
        --hidden-import transformers ^
        main.py
)

:: 檢查建置結果
if exist "dist\YouTube Live Translator.exe" (
    echo.
    echo ===================================
    echo 建置成功！
    echo 執行檔位置: dist\YouTube Live Translator.exe
    echo ===================================
    
    :: 詢問是否要開啟資料夾
    echo.
    set /p open_folder=是否要開啟輸出資料夾？(Y/N): 
    if /i "%open_folder%"=="Y" (
        explorer dist
    )
) else (
    echo.
    echo ===================================
    echo 建置失敗！
    echo 請檢查錯誤訊息
    echo ===================================
)

echo.
pause
deactivate