"""
應用程式配置設定
"""
import os
from pathlib import Path

# 應用程式基本設定
APP_NAME = "YouTube 直播即時翻譯器"
APP_VERSION = "1.0.0"

# 路徑設定
BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
MODELS_DIR = BASE_DIR / "models"

# 確保必要目錄存在
MODELS_DIR.mkdir(exist_ok=True)

# Whisper 模型設定
WHISPER_MODEL = "turbo"  # 使用 turbo 版本（即 large-v3-turbo）以獲得最佳的準確性和即時性能
WHISPER_DEVICE = "cuda"  # 強制使用 GPU 加速語音識別
WHISPER_LANGUAGE = None  # None 表示自動偵測

# Gemma 翻譯模型設定
GEMMA_MODEL_NAME = "google/gemma-3n-E2B-it"  # 使用更小的 E2B 版本（約 6GB vs 15GB）
GEMMA_DEVICE = "cpu"  # 強制使用 CPU 以節省 GPU 記憶體
GEMMA_QUANTIZATION = "int4"  # 4-bit 量化（CPU 模式下會自動忽略）
GEMMA_MAX_LENGTH = 512
GEMMA_TEMPERATURE = 0.7

# 音訊設定
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHUNK_DURATION = 5  # 每次處理的音訊長度（秒）
AUDIO_BUFFER_SIZE = 30  # 音訊緩衝區大小（秒）

# 字幕設定預設值
DEFAULT_SUBTITLE_SETTINGS = {
    "font_size": 24,
    "font_family": "Microsoft YaHei",  # 支援中文的字體
    "font_color": "#FFFFFF",
    "background_color": "#000000",
    "background_opacity": 0.7,
    "position_x": 0.5,  # 相對位置 (0-1)
    "position_y": 0.8,  # 相對位置 (0-1)
    "shadow_enabled": True,
    "shadow_color": "#000000",
    "shadow_offset": 2,
    "max_width": 0.8,  # 最大寬度（相對於螢幕寬度）
}

# 支援的語言列表
SUPPORTED_LANGUAGES = {
    "auto": "自動偵測",
    "en": "英文",
    "zh": "中文",
    "ja": "日文",
    "ko": "韓文",
    "es": "西班牙文",
    "fr": "法文",
    "de": "德文",
    "ru": "俄文",
    "pt": "葡萄牙文",
    "it": "義大利文",
    "th": "泰文",
    "vi": "越南文",
    "ar": "阿拉伯文",
    "hi": "印地文",
    "id": "印尼文",
}

# 效能設定
MAX_CONCURRENT_TASKS = 3
TRANSLATION_CACHE_SIZE = 1000
LOW_LATENCY_MODE = True

# 日誌設定
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "app.log" 