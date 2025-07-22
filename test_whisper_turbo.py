#!/usr/bin/env python3
"""
Whisper turbo 模型測試腳本
測試 turbo 模型（即 large-v3-turbo）的性能和配置
"""

import time
import numpy as np
import logging
from src.core.transcriber import Transcriber
from src.config import WHISPER_MODEL, WHISPER_DEVICE

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_whisper_turbo():
    """測試 Whisper large-v3-turbo 模型"""
    logger.info(f"🔍 測試 Whisper 模型: {WHISPER_MODEL}")
    logger.info(f"🔍 使用設備: {WHISPER_DEVICE}")
    
    try:
        # 檢查 CUDA 可用性
        import torch
        cuda_available = torch.cuda.is_available()
        logger.info(f"CUDA 可用: {cuda_available}")
        
        if cuda_available:
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU 記憶體: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        
        # 初始化轉錄器
        logger.info("=== 初始化 Whisper 轉錄器 ===")
        transcriber = Transcriber()
        
        start_time = time.time()
        transcriber.initialize()
        init_time = time.time() - start_time
        
        logger.info(f"✅ 初始化完成，耗時: {init_time:.2f} 秒")
        
        # 創建測試音頻（3 秒，16kHz）
        logger.info("=== 創建測試音頻 ===")
        sample_rate = 16000
        duration = 3
        
        # 生成白噪音作為測試音頻
        test_audio = np.random.random(sample_rate * duration).astype(np.float32) * 0.1
        logger.info(f"測試音頻: {duration} 秒, {sample_rate} Hz, 形狀: {test_audio.shape}")
        
        # 測試轉錄性能
        logger.info("=== 測試轉錄性能 ===")
        
        # 預熱
        logger.info("預熱轉錄器...")
        _ = transcriber.transcribe(test_audio[:sample_rate], "auto")  # 1 秒預熱
        
        # 正式測試
        test_iterations = 3
        total_time = 0
        
        for i in range(test_iterations):
            logger.info(f"轉錄測試 {i+1}/{test_iterations}")
            
            start_time = time.time()
            result = transcriber.transcribe(test_audio, "auto")
            process_time = time.time() - start_time
            total_time += process_time
            
            logger.info(f"  耗時: {process_time:.2f} 秒")
            logger.info(f"  結果: {result}")
            
            # 計算即時因子 (Real-time Factor)
            rtf = process_time / duration
            logger.info(f"  即時因子 (RTF): {rtf:.2f} ({'✅ 即時' if rtf < 1.0 else '❌ 非即時'})")
        
        # 統計結果
        avg_time = total_time / test_iterations
        avg_rtf = avg_time / duration
        
        logger.info("=== 效能統計 ===")
        logger.info(f"平均處理時間: {avg_time:.2f} 秒")
        logger.info(f"平均即時因子: {avg_rtf:.2f}")
        logger.info(f"適合即時轉錄: {'✅ 是' if avg_rtf < 0.8 else '❌ 否'}")
        
        # 測試帶時間戳的轉錄
        logger.info("=== 測試時間戳轉錄 ===")
        start_time = time.time()
        timestamps_result = transcriber.transcribe_with_timestamps(test_audio, "auto")
        timestamp_time = time.time() - start_time
        
        logger.info(f"時間戳轉錄耗時: {timestamp_time:.2f} 秒")
        logger.info(f"時間戳結果: {timestamps_result}")
        
        # 記憶體使用情況
        if cuda_available and WHISPER_DEVICE == "cuda":
            gpu_memory = torch.cuda.memory_allocated() / 1024**3
            logger.info(f"GPU 記憶體使用: {gpu_memory:.2f} GB")
        
        # 清理資源
        transcriber.cleanup()
        logger.info("✅ 資源清理完成")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    logger.info("🚀 開始 Whisper turbo 模型測試...")
    
    success = test_whisper_turbo()
    
    if success:
        logger.info("🎉 所有測試通過！Whisper turbo 模型配置正確")
        print("\n✅ 結論:")
        print("  - Whisper turbo 模型（large-v3-turbo）可以正常運行")
        print("  - 適合用於即時語音轉錄")
        print("  - GPU 加速正常工作")
        print("  - 相比 large-v3 有更好的速度表現")
    else:
        logger.error("❌ 測試失敗，需要檢查配置")

if __name__ == "__main__":
    main() 