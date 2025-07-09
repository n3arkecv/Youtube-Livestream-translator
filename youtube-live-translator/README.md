# YouTube Live Translator

即時YouTube直播翻譯字幕疊層應用程式

## 功能特色

- 🎥 即時擷取YouTube直播音訊
- 🎙️ 使用OpenAI Whisper進行語音辨識
- 🌐 使用Google Gemma進行智慧翻譯（支援上下文）
- 📺 螢幕疊層顯示雙語字幕
- 🎨 可自訂字幕樣式（大小、顏色、位置、陰影）
- 🌍 支援多種語言

## 系統需求

- Windows 10/11 (64-bit)
- Python 3.8 或更高版本
- 至少 8GB RAM（建議 16GB）
- NVIDIA GPU（可選，但建議用於更快的處理速度）
- 穩定的網路連線

## 安裝步驟

### 方法一：使用批次檔（推薦）

1. 下載整個專案資料夾
2. 雙擊執行 `run.bat`
3. 首次執行時會自動安裝所需的依賴套件

### 方法二：手動安裝

1. 安裝Python 3.8+
2. 開啟命令提示字元，進入專案目錄
3. 創建虛擬環境：
   ```bash
   python -m venv venv
   ```
4. 啟動虛擬環境：
   ```bash
   venv\Scripts\activate
   ```
5. 安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```
6. 執行應用程式：
   ```bash
   python main.py
   ```

## 使用說明

1. **輸入直播網址**
   - 在主視窗的URL欄位輸入YouTube直播連結
   - 支援格式：`https://www.youtube.com/watch?v=xxxxx`

2. **選擇語言**
   - 來源語言：選擇直播的語言
   - 目標語言：選擇要翻譯成的語言

3. **自訂字幕樣式**
   - 字體大小：12-72pt
   - 字體顏色：點擊按鈕選擇顏色
   - 背景顏色：可設定透明度
   - 垂直位置：0-100%（0%在頂部，100%在底部）
   - 文字陰影：可開啟/關閉及調整強度

4. **開始翻譯**
   - 點擊「開始翻譯」按鈕
   - 字幕會自動顯示在螢幕上
   - 點擊「停止翻譯」結束

## 建立執行檔（.exe）

如果您想要建立獨立的.exe執行檔：

1. 安裝PyInstaller：
   ```bash
   pip install pyinstaller
   ```

2. 執行打包命令：
   ```bash
   pyinstaller --windowed --onefile --name "YouTube Live Translator" --icon assets/icon.ico main.py
   ```

3. 執行檔會在 `dist` 資料夾中生成

## 注意事項

- 首次執行時需要下載AI模型，可能需要較長時間
- 確保有足夠的硬碟空間（模型檔案約2-5GB）
- 字幕疊層會覆蓋在所有視窗之上
- 建議在觀看直播的螢幕上使用

## 故障排除

**問題：無法連接到YouTube直播**
- 確認直播連結正確且直播正在進行中
- 檢查網路連線
- 嘗試更新yt-dlp：`pip install --upgrade yt-dlp`

**問題：翻譯不準確**
- 確保選擇了正確的來源語言
- 語音清晰度會影響辨識效果
- 可嘗試調整Whisper模型大小

**問題：字幕沒有顯示**
- 檢查是否有其他全螢幕應用程式
- 嘗試調整字幕位置
- 確認字幕顏色與背景有足夠對比

## 開發者資訊

### 專案結構
```
youtube-live-translator/
├── main.py              # 主程式入口
├── run.bat             # Windows執行批次檔
├── requirements.txt    # Python依賴列表
├── src/
│   ├── gui/           # GUI相關模組
│   ├── audio/         # 音訊處理模組
│   ├── models/        # AI模型模組
│   └── utils/         # 工具模組
└── assets/            # 資源檔案
```

### 使用的技術
- PyQt5 - GUI框架
- OpenAI Whisper - 語音辨識
- Google Gemma - 語言翻譯
- yt-dlp - YouTube影片下載
- FFmpeg - 音訊處理

## 授權

本專案採用 MIT 授權條款

## 貢獻

歡迎提交Issue和Pull Request！

---

如有任何問題或建議，請在GitHub上開啟Issue。