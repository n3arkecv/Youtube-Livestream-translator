@echo off
echo ========================================
echo   YouTube 直播即時翻譯器 - 安裝程式
echo ========================================
echo.

REM 檢查管理員權限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 請以管理員身份執行此安裝程式！
    echo 右鍵點擊此檔案，選擇"以系統管理員身分執行"
    pause
    exit /b 1
)

echo 正在檢查系統需求...
echo.

REM 檢查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 未檢測到 Python
    echo.
    echo 正在下載 Python 安裝程式...
    echo 請在安裝時勾選 "Add Python to PATH"
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [✓] Python 已安裝

REM 檢查 pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] pip 未正確安裝
    pause
    exit /b 1
)
echo [✓] pip 已安裝

REM 檢查 ffmpeg
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] FFmpeg 未安裝
    echo.
    echo FFmpeg 是處理 YouTube 音訊所必需的
    echo 請從以下網址下載並安裝:
    echo https://www.gyan.dev/ffmpeg/builds/
    echo.
    echo 下載 "full" 版本，解壓後將 bin 資料夾加入系統 PATH
    echo.
    set /p install_ffmpeg="是否要開啟 FFmpeg 下載頁面? (Y/N): "
    if /i "%install_ffmpeg%"=="Y" (
        start https://www.gyan.dev/ffmpeg/builds/
    )
) else (
    echo [✓] FFmpeg 已安裝
)

echo.
echo 正在創建虛擬環境...
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo 正在更新 pip...
python -m pip install --upgrade pip

echo.
echo 正在安裝相依套件...
echo 這可能需要 10-20 分鐘，請耐心等待...
echo.

REM 分步驟安裝以避免超時
echo [1/5] 安裝 GUI 框架...
pip install PyQt5==5.15.9

echo.
echo [2/5] 安裝音訊處理工具...
pip install yt-dlp pydub sounddevice numpy

echo.
echo [3/5] 安裝 PyTorch (這可能需要較長時間)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo.
echo [4/5] 安裝 Whisper...
pip install openai-whisper

echo.
echo [5/5] 安裝翻譯模型相關套件...
pip install transformers accelerate bitsandbytes

echo.
echo 安裝其他相依套件...
pip install requests pywin32 screeninfo webrtcvad

echo.
echo ========================================
echo   安裝完成！
echo ========================================
echo.
echo 首次執行時，程式會自動下載必要的模型檔案
echo 這可能需要額外的時間和網路頻寬
echo.
echo 執行 run.bat 來啟動應用程式
echo.
pause 