#!/usr/bin/env python3
"""
設備配置測試腳本
測試 Whisper (GPU) 和 Gemma (CPU) 的設備配置是否正確
"""

import torch
import logging
import sys
import os

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_gpu_availability():
    """測試 GPU 可用性"""
    logger.info("=== GPU 可用性測試 ===")
    
    if torch.cuda.is_available():
        gpu_count = torch.cuda.device_count()
        current_gpu = torch.cuda.current_device()
        gpu_name = torch.cuda.get_device_name(current_gpu)
        
        logger.info(f"✅ CUDA 可用")
        logger.info(f"GPU 數量: {gpu_count}")
        logger.info(f"當前 GPU: {current_gpu}")
        logger.info(f"GPU 名稱: {gpu_name}")
        logger.info(f"GPU 記憶體: {torch.cuda.get_device_properties(current_gpu).total_memory / 1024**3:.1f} GB")
        return True
    else:
        logger.warning("❌ CUDA 不可用，所有模型將使用 CPU")
        return False

def test_whisper_device():
    """測試 Whisper 設備配置"""
    logger.info("\n=== Whisper 設備測試 ===")
    
    try:
        from src.config import WHISPER_DEVICE
        logger.info(f"配置中的 Whisper 設備: {WHISPER_DEVICE}")
        
        # 測試 Whisper 初始化
        from src.core.transcriber import Transcriber
        transcriber = Transcriber()
        
        # 不實際初始化模型，只檢查設備邏輯
        if WHISPER_DEVICE == "cuda" and torch.cuda.is_available():
            expected_device = "cuda"
        else:
            expected_device = "cpu"
        
        logger.info(f"✅ Whisper 預期使用設備: {expected_device.upper()}")
        return expected_device
        
    except ImportError as e:
        logger.error(f"❌ 無法導入 Whisper 相關模組: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Whisper 設備測試失敗: {e}")
        return None

def test_gemma_device():
    """測試 Gemma 設備配置"""
    logger.info("\n=== Gemma 設備測試 ===")
    
    try:
        from src.config import GEMMA_DEVICE, GEMMA_QUANTIZATION
        logger.info(f"配置中的 Gemma 設備: {GEMMA_DEVICE}")
        logger.info(f"配置中的 Gemma 量化: {GEMMA_QUANTIZATION}")
        
        # 測試 Gemma 翻譯器
        from src.core.translator import GemmaTranslator
        translator = GemmaTranslator()
        
        logger.info(f"✅ Gemma 預期使用設備: {GEMMA_DEVICE.upper()}")
        
        if GEMMA_DEVICE == "cpu":
            logger.info("✅ CPU 模式：將不使用量化，使用全精度模型")
        else:
            logger.info(f"✅ GPU 模式：將使用 {GEMMA_QUANTIZATION} 量化")
        
        return GEMMA_DEVICE
        
    except ImportError as e:
        logger.error(f"❌ 無法導入 Gemma 相關模組: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Gemma 設備測試失敗: {e}")
        return None

def test_memory_usage():
    """測試記憶體使用情況"""
    logger.info("\n=== 記憶體使用測試 ===")
    
    # CPU 記憶體
    try:
        import psutil
        cpu_memory = psutil.virtual_memory()
        logger.info(f"CPU 記憶體總量: {cpu_memory.total / 1024**3:.1f} GB")
        logger.info(f"CPU 記憶體可用: {cpu_memory.available / 1024**3:.1f} GB")
        logger.info(f"CPU 記憶體使用率: {cpu_memory.percent:.1f}%")
    except ImportError:
        logger.warning("無法獲取 CPU 記憶體資訊 (需要 psutil)")
    
    # GPU 記憶體
    if torch.cuda.is_available():
        gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        gpu_memory_allocated = torch.cuda.memory_allocated(0) / 1024**3
        gpu_memory_cached = torch.cuda.memory_reserved(0) / 1024**3
        
        logger.info(f"GPU 記憶體總量: {gpu_memory_total:.1f} GB")
        logger.info(f"GPU 記憶體已分配: {gpu_memory_allocated:.1f} GB")
        logger.info(f"GPU 記憶體已快取: {gpu_memory_cached:.1f} GB")

def main():
    """主測試函數"""
    logger.info("🚀 開始設備配置測試...\n")
    
    # 測試 GPU 可用性
    gpu_available = test_gpu_availability()
    
    # 測試 Whisper 設備配置
    whisper_device = test_whisper_device()
    
    # 測試 Gemma 設備配置
    gemma_device = test_gemma_device()
    
    # 測試記憶體使用
    test_memory_usage()
    
    # 總結
    logger.info("\n=== 測試總結 ===")
    
    if whisper_device == "cuda" and gemma_device == "cpu":
        logger.info("✅ 配置正確：Whisper 使用 GPU，Gemma 使用 CPU")
        logger.info("✅ 這樣的配置可以最大化 GPU 利用率，避免記憶體衝突")
    elif whisper_device == "cpu" and gemma_device == "cpu":
        logger.info("⚠️  兩個模型都使用 CPU（可能因為沒有 GPU 或 GPU 不可用）")
    elif whisper_device == "cuda" and gemma_device == "cuda":
        logger.info("⚠️  兩個模型都使用 GPU（可能會有記憶體不足問題）")
    else:
        logger.warning("❓ 未預期的設備配置組合")
    
    logger.info("\n🎯 測試完成！")

if __name__ == "__main__":
    main() 