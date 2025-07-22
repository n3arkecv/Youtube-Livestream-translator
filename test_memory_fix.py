#!/usr/bin/env python3
"""
記憶體使用監控腳本 - 測試修復效果
"""

import time
import psutil
import threading
import logging
from src.core.translator import GemmaTranslator
from src.core.transcriber import Transcriber

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MemoryMonitor:
    """記憶體使用監控器"""
    
    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread = None
        self.max_memory_used = 0
        self.start_memory = 0
        
    def start_monitoring(self):
        """開始監控記憶體使用"""
        self.is_monitoring = True
        self.start_memory = psutil.virtual_memory().used / 1024**3
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info(f"開始監控記憶體使用 (起始: {self.start_memory:.2f} GB)")
    
    def stop_monitoring(self):
        """停止監控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        end_memory = psutil.virtual_memory().used / 1024**3
        memory_increase = end_memory - self.start_memory
        
        logger.info(f"監控結束:")
        logger.info(f"  起始記憶體: {self.start_memory:.2f} GB")
        logger.info(f"  結束記憶體: {end_memory:.2f} GB")
        logger.info(f"  最大記憶體: {self.max_memory_used:.2f} GB")
        logger.info(f"  記憶體增加: {memory_increase:.2f} GB")
        
        return memory_increase
    
    def _monitor_loop(self):
        """監控循環"""
        while self.is_monitoring:
            current_memory = psutil.virtual_memory().used / 1024**3
            self.max_memory_used = max(self.max_memory_used, current_memory)
            
            # 每 2 秒檢查一次
            time.sleep(2)

def test_gemma_memory_usage():
    """測試 Gemma 翻譯器記憶體使用"""
    logger.info("=== 測試 Gemma 翻譯器記憶體使用 ===")
    
    monitor = MemoryMonitor()
    monitor.start_monitoring()
    
    try:
        # 初始化翻譯器
        logger.info("初始化 Gemma 翻譯器...")
        translator = GemmaTranslator()
        translator.initialize()
        
        # 測試多次翻譯
        test_texts = [
            "Hello world",
            "How are you today?",
            "This is a test message",
            "YouTube live streaming translation",
            "Artificial intelligence is amazing"
        ]
        
        logger.info("開始翻譯測試...")
        for i, text in enumerate(test_texts):
            logger.info(f"翻譯 {i+1}/5: {text}")
            result = translator.translate(text, "中文")
            logger.info(f"結果: {result}")
            time.sleep(1)
        
        # 清理資源
        translator.cleanup()
        
    except Exception as e:
        logger.error(f"測試失敗: {e}")
        import traceback
        traceback.print_exc()
    finally:
        memory_increase = monitor.stop_monitoring()
        return memory_increase

def test_whisper_memory_usage():
    """測試 Whisper 轉錄器記憶體使用"""
    logger.info("=== 測試 Whisper 轉錄器記憶體使用 ===")
    
    monitor = MemoryMonitor()
    monitor.start_monitoring()
    
    try:
        # 初始化轉錄器
        logger.info("初始化 Whisper 轉錄器...")
        transcriber = Transcriber()
        transcriber.initialize()
        
        # 創建測試音頻數據
        import numpy as np
        
        # 生成 3 秒的測試音頻（16kHz）
        sample_rate = 16000
        duration = 3
        test_audio = np.random.random(sample_rate * duration).astype(np.float32) * 0.1
        
        logger.info("開始轉錄測試...")
        for i in range(5):
            logger.info(f"轉錄測試 {i+1}/5")
            result = transcriber.transcribe(test_audio)
            logger.info(f"結果: {result}")
            time.sleep(1)
        
        # 清理資源
        transcriber.cleanup()
        
    except Exception as e:
        logger.error(f"測試失敗: {e}")
        import traceback
        traceback.print_exc()
    finally:
        memory_increase = monitor.stop_monitoring()
        return memory_increase

def main():
    """主測試函數"""
    logger.info("🔍 開始記憶體使用測試...")
    
    # 顯示系統資訊
    memory_info = psutil.virtual_memory()
    logger.info(f"系統記憶體: {memory_info.total / 1024**3:.1f} GB")
    logger.info(f"可用記憶體: {memory_info.available / 1024**3:.1f} GB")
    logger.info(f"已用記憶體: {memory_info.used / 1024**3:.1f} GB")
    logger.info(f"使用率: {memory_info.percent}%")
    
    # 測試 Gemma 翻譯器
    try:
        gemma_memory = test_gemma_memory_usage()
        logger.info(f"✅ Gemma 測試完成，記憶體增加: {gemma_memory:.2f} GB")
    except Exception as e:
        logger.error(f"❌ Gemma 測試失敗: {e}")
    
    # 等待一段時間讓記憶體釋放
    time.sleep(5)
    
    # 測試 Whisper 轉錄器
    try:
        whisper_memory = test_whisper_memory_usage()
        logger.info(f"✅ Whisper 測試完成，記憶體增加: {whisper_memory:.2f} GB")
    except Exception as e:
        logger.error(f"❌ Whisper 測試失敗: {e}")
    
    logger.info("🎉 記憶體測試完成！")

if __name__ == "__main__":
    main() 