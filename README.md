# YouTube 直播即時翻譯器

一款具備圖形化使用者介面的桌面應用程式，可即時翻譯 YouTube 直播內容並以疊層字幕顯示。

## 功能特色

- 🎥 支援 YouTube 直播即時翻譯
- 🎙️ 使用 OpenAI Whisper Local Turbo 進行語音轉文字
- 🌍 使用 Google Gemma 模型進行高品質翻譯
- 📝 即時疊層字幕顯示
- ⚙️ 可自訂字幕樣式（大小、顏色、位置、陰影）
- 💻 簡潔直觀的圖形使用者介面

## 系統需求

- Windows 10 或更高版本
- 至少 8GB RAM（建議 16GB）
- NVIDIA GPU（支援 CUDA）建議但非必需

## 安裝指南

1. 下載最新版本的執行檔
2. 執行 `YouTubeTranslator.exe`
3. 首次執行時會自動下載必要的模型檔案

## 使用說明

1. 輸入 YouTube 直播網址
2. 選擇來源語言和目標語言
3. 調整字幕設定（可選）
4. 點擊「開始翻譯」按鈕
5. 字幕會自動顯示在螢幕上

## 技術架構

- 前端：PyQt5 GUI 框架
- 語音識別：OpenAI Whisper Local Turbo
- 翻譯引擎：Google Gemma-3n-E4B-it-int4
- 音訊處理：yt-dlp + PyDub
- 字幕顯示：透明疊層視窗技術 