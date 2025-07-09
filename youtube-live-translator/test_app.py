#!/usr/bin/env python3
"""
測試應用程式 - 使用模擬模型
"""

import sys
import os

# 設定使用模擬模型
os.environ['USE_MOCK_MODELS'] = '1'

# 修改導入以使用模擬類別
import src.models.whisper_model
import src.models.gemma_translator
import src.audio.stream_capture

# 替換為模擬類別
src.models.whisper_model.WhisperModel = src.models.whisper_model.MockWhisperModel
src.models.gemma_translator.GemmaTranslator = src.models.gemma_translator.MockGemmaTranslator
src.audio.stream_capture.StreamCapture = src.audio.stream_capture.MockStreamCapture

# 執行主程式
from main import main

if __name__ == "__main__":
    print("執行測試模式...")
    print("使用模擬模型，不需要下載實際的AI模型")
    print("這可以用來測試GUI和基本功能")
    print()
    main()