"""
語音轉文字模組 - 使用 OpenAI Whisper
"""
import logging
import threading
import queue
import time
import numpy as np
import torch
import whisper
from typing import Optional, List, Tuple

from ..config import (
    WHISPER_MODEL, WHISPER_DEVICE, WHISPER_LANGUAGE,
    AUDIO_SAMPLE_RATE, MODELS_DIR
)

logger = logging.getLogger(__name__)


class Transcriber:
    """語音轉文字處理器"""
    
    def __init__(self):
        self.model = None
        self.device = WHISPER_DEVICE
        self.is_initialized = False
        self._model_dtype = torch.float32  # 默認數據類型
        
        # 語言映射
        self.language_map = {
            "auto": None,
            "en": "english",
            "zh": "chinese",
            "ja": "japanese",
            "ko": "korean",
            "es": "spanish",
            "fr": "french",
            "de": "german",
            "ru": "russian",
            "pt": "portuguese",
            "it": "italian",
            "th": "thai",
            "vi": "vietnamese",
            "ar": "arabic",
            "hi": "hindi",
            "id": "indonesian",
        }
        
        # 上下文緩衝區
        self.context_buffer = []
        self.max_context_length = 5  # 保留最近 5 個轉錄結果作為上下文
    
    def initialize(self):
        """初始化 Whisper 模型"""
        try:
            logger.info("正在初始化 Whisper 模型...")
            
            # 設定設備
            if WHISPER_DEVICE == "cuda" and torch.cuda.is_available():
                self.device = "cuda"
                logger.info("使用 CUDA 加速")
            else:
                self.device = "cpu"
                logger.info("使用 CPU")
            
            # 載入模型
            model_name = WHISPER_MODEL
            if model_name == "turbo":
                # Whisper turbo 是 large-v3 的優化版本
                model_name = "large-v3"
            
            logger.info(f"正在載入 Whisper {model_name} 模型...")
            
            # 設定模型下載路徑
            download_root = str(MODELS_DIR)
            
            # 載入模型
            self.model = whisper.load_model(
                model_name, 
                device=self.device,
                download_root=download_root
            )
            
            # 如果是 turbo 模式或 large-v3-turbo，進行額外的優化
            if "turbo" in WHISPER_MODEL.lower():
                self._optimize_for_turbo()
            
            self.is_initialized = True
            logger.info("Whisper 模型初始化完成")
            
        except Exception as e:
            logger.error(f"初始化 Whisper 模型失敗: {e}")
            raise
    
    def _optimize_for_turbo(self):
        """優化模型以獲得更好的即時性能"""
        try:
            # 暫時禁用半精度優化以避免兼容性問題
            # 主要優化來自於減少的解碼器層數
            self._model_dtype = torch.float32
            
            # 啟用 PyTorch 優化
            if hasattr(torch, 'compile'):
                try:
                    self.model = torch.compile(self.model)
                    logger.info("PyTorch 編譯優化已啟用")
                except Exception as compile_error:
                    logger.warning(f"PyTorch 編譯失敗: {compile_error}")
            
            logger.info("Turbo 模型優化完成")
            
        except Exception as e:
            logger.warning(f"Turbo 優化失敗，使用標準模式: {e}")
            self._model_dtype = torch.float32
    
    def transcribe(self, audio_data: np.ndarray, language: str = "auto") -> Optional[str]:
        """
        轉錄音訊為文字
        
        Args:
            audio_data: 音訊數據 (numpy array)
            language: 語言代碼
            
        Returns:
            轉錄的文字或 None
        """
        if not self.is_initialized:
            logger.error("Whisper 模型尚未初始化")
            return None
        
        try:
            # 確保音訊數據格式正確
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # 正規化音訊
            if np.abs(audio_data).max() > 1.0:
                audio_data = audio_data / np.abs(audio_data).max()
            
            # 設定語言
            whisper_language = self.language_map.get(language, None)
            
            # 準備轉錄選項
            options = {
                "language": whisper_language,
                "task": "transcribe",
                "fp16": self.device == "cuda",
                "no_speech_threshold": 0.6,
                "logprob_threshold": -1.0,
                "compression_ratio_threshold": 2.4,
                "condition_on_previous_text": True,
                "initial_prompt": self._get_context_prompt(),
            }
            
            # 執行轉錄
            with torch.no_grad():
                result = self.model.transcribe(
                    audio_data,
                    **options
                )
            
            # 獲取文字
            text = result.get("text", "").strip()
            
            if text:
                # 更新上下文
                self._update_context(text)
                logger.debug(f"轉錄結果: {text}")
                return text
            
            return None
            
        except Exception as e:
            logger.error(f"轉錄失敗: {e}")
            return None
    
    def transcribe_with_timestamps(
        self, audio_data: np.ndarray, language: str = "auto"
    ) -> Optional[List[Tuple[float, float, str]]]:
        """
        轉錄音訊並返回時間戳記
        
        Returns:
            [(start_time, end_time, text), ...] 或 None
        """
        if not self.is_initialized:
            return None
        
        try:
            # 設定語言
            whisper_language = self.language_map.get(language, None)
            
            # 轉錄選項
            options = {
                "language": whisper_language,
                "task": "transcribe",
                "fp16": self.device == "cuda",
                "word_timestamps": True,  # 啟用詞級時間戳記
                "condition_on_previous_text": True,
                "initial_prompt": self._get_context_prompt(),
            }
            
            # 執行轉錄
            with torch.no_grad():
                result = self.model.transcribe(
                    audio_data,
                    **options
                )
            
            # 提取帶時間戳記的片段
            segments_with_timestamps = []
            
            for segment in result.get("segments", []):
                start_time = segment.get("start", 0)
                end_time = segment.get("end", 0)
                text = segment.get("text", "").strip()
                
                if text:
                    segments_with_timestamps.append((start_time, end_time, text))
            
            return segments_with_timestamps
            
        except Exception as e:
            logger.error(f"帶時間戳記的轉錄失敗: {e}")
            return None
    
    def _get_context_prompt(self) -> str:
        """獲取上下文提示詞"""
        if not self.context_buffer:
            return ""
        
        # 組合最近的文字作為上下文
        context = " ".join(self.context_buffer)
        
        # 限制長度
        max_length = 200
        if len(context) > max_length:
            context = context[-max_length:]
        
        return context
    
    def _update_context(self, text: str):
        """更新上下文緩衝區"""
        self.context_buffer.append(text)
        
        # 保持緩衝區大小
        if len(self.context_buffer) > self.max_context_length:
            self.context_buffer.pop(0)
    
    def clear_context(self):
        """清除上下文"""
        self.context_buffer.clear()
    
    def cleanup(self):
        """清理資源"""
        if self.model:
            del self.model
            self.model = None
        
        if self.device == "cuda":
            torch.cuda.empty_cache()
        
        self.is_initialized = False
        logger.info("Whisper 模型已清理")


class WhisperTurbo(Transcriber):
    """
    Whisper Turbo 實作 - 針對即時轉錄優化
    """
    
    def __init__(self):
        super().__init__()
        self.vad_model = None  # Voice Activity Detection
        self.buffer_size = 3  # 秒
        self.stride = 1  # 秒
        self.audio_buffer = []
        self.buffer_lock = threading.Lock()
    
    def initialize(self):
        """初始化 Turbo 模式"""
        super().initialize()
        
        try:
            # 載入 VAD 模型以提高效率
            self._load_vad_model()
            
            # 設定即時轉錄參數
            self.chunk_length = 3  # 處理 3 秒片段
            self.stride_length = 1  # 1 秒重疊
            
        except Exception as e:
            logger.warning(f"VAD 初始化失敗: {e}")
    
    def _load_vad_model(self):
        """載入語音活動檢測模型"""
        try:
            import webrtcvad
            self.vad = webrtcvad.Vad(3)  # 激進程度 0-3
            logger.info("VAD 模型已載入")
        except ImportError:
            logger.info("webrtcvad 未安裝，將使用簡單的音量檢測替代 VAD 功能")
            self.vad = None
    
    def transcribe_streaming(self, audio_stream):
        """
        串流轉錄 - 專為即時處理設計
        
        Args:
            audio_stream: 音訊串流生成器
            
        Yields:
            轉錄的文字片段
        """
        if not self.is_initialized:
            logger.error("模型尚未初始化")
            return
        
        buffer = []
        
        for audio_chunk in audio_stream:
            # 加入緩衝區
            buffer.append(audio_chunk)
            
            # 計算緩衝區時長
            buffer_duration = len(buffer) * len(audio_chunk) / AUDIO_SAMPLE_RATE
            
            # 當緩衝區足夠大時進行轉錄
            if buffer_duration >= self.chunk_length:
                # 合併音訊
                audio_data = np.concatenate(buffer)
                
                # 檢測是否有語音
                if self._has_speech(audio_data):
                    # 轉錄
                    text = self.transcribe(audio_data)
                    if text:
                        yield text
                
                # 移除已處理的部分，保留重疊
                samples_to_remove = int(self.stride_length * AUDIO_SAMPLE_RATE)
                total_samples = sum(len(chunk) for chunk in buffer)
                
                # 重新建立緩衝區
                remaining_audio = audio_data[samples_to_remove:]
                buffer = [remaining_audio]
    
    def _has_speech(self, audio_data: np.ndarray) -> bool:
        """檢測音訊中是否有語音"""
        if self.vad is None:
            # 使用簡單的音量檢測替代 VAD
            return self._simple_voice_detection(audio_data)
        
        try:
            # 轉換為 16-bit PCM
            pcm_data = (audio_data * 32767).astype(np.int16).tobytes()
            
            # 分割成 30ms 幀
            frame_duration = 30  # ms
            frame_length = int(AUDIO_SAMPLE_RATE * frame_duration / 1000)
            
            num_frames = len(audio_data) // frame_length
            speech_frames = 0
            
            for i in range(num_frames):
                start = i * frame_length * 2  # 2 bytes per sample
                end = start + frame_length * 2
                frame = pcm_data[start:end]
                
                if self.vad.is_speech(frame, AUDIO_SAMPLE_RATE):
                    speech_frames += 1
            
            # 如果超過 30% 的幀包含語音，則認為有語音
            return speech_frames > num_frames * 0.3
            
        except Exception as e:
            logger.warning(f"VAD 檢測失敗，使用簡單檢測: {e}")
            return self._simple_voice_detection(audio_data)

    def _simple_voice_detection(self, audio_data: np.ndarray) -> bool:
        """簡單的語音檢測（基於音量）"""
        # 計算 RMS 音量
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        # 設定閾值（可以根據需要調整）
        threshold = 0.01
        
        return rms > threshold 