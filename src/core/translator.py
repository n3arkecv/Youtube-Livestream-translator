"""
翻譯模組 - 使用 Google Gemma 模型
"""
import logging
import threading
import queue
from typing import Optional, List, Dict
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    BitsAndBytesConfig, pipeline
)

from ..config import (
    GEMMA_MODEL_NAME, GEMMA_DEVICE, GEMMA_QUANTIZATION, GEMMA_MAX_LENGTH,
    GEMMA_TEMPERATURE, MODELS_DIR, TRANSLATION_CACHE_SIZE
)

logger = logging.getLogger(__name__)


class TranslationCache:
    """翻譯快取"""
    
    def __init__(self, max_size: int = TRANSLATION_CACHE_SIZE):
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[str]:
        """獲取快取的翻譯"""
        with self.lock:
            if key in self.cache:
                self.access_count[key] = self.access_count.get(key, 0) + 1
                return self.cache[key]
        return None
    
    def put(self, key: str, value: str):
        """加入快取"""
        with self.lock:
            # 如果快取滿了，移除最少使用的項目
            if len(self.cache) >= self.max_size:
                # 找出最少使用的鍵
                min_count = min(self.access_count.values())
                for k, count in list(self.access_count.items()):
                    if count == min_count:
                        del self.cache[k]
                        del self.access_count[k]
                        break
            
            self.cache[key] = value
            self.access_count[key] = 1
    
    def clear(self):
        """清空快取"""
        with self.lock:
            self.cache.clear()
            self.access_count.clear()


class Translator:
    """翻譯處理器"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.is_initialized = False
        self.translation_cache = TranslationCache()
        self.context_buffer = []  # 保存上下文
        self.max_context_length = 5  # 保留最近5段對話
        
        # 語言代碼映射
        self.language_names = {
            "zh": "Chinese",
            "en": "English",
            "ja": "Japanese",
            "ko": "Korean",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "ru": "Russian",
            "pt": "Portuguese",
            "it": "Italian",
            "th": "Thai",
            "vi": "Vietnamese",
            "ar": "Arabic",
            "hi": "Hindi",
            "id": "Indonesian",
        }
    
    def initialize(self):
        """初始化 Gemma 模型"""
        try:
            logger.info("正在初始化 Gemma 翻譯模型...")
            
            # 使用配置中指定的設備
            device = GEMMA_DEVICE
            logger.info(f"Gemma 翻譯模型將使用: {device.upper()}")
            
            # 設定量化配置（僅在 GPU 模式下使用）
            quantization_config = None
            if device == "cuda" and GEMMA_QUANTIZATION in ["int4", "int8"]:
                if GEMMA_QUANTIZATION == "int4":
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4"
                    )
                elif GEMMA_QUANTIZATION == "int8":
                    quantization_config = BitsAndBytesConfig(
                        load_in_8bit=True,
                        bnb_8bit_compute_dtype=torch.float16
                    )
                logger.info(f"使用 {GEMMA_QUANTIZATION} 量化")
            else:
                logger.info("CPU 模式：不使用量化，使用全精度模型")
            
            # 載入分詞器
            logger.info("載入分詞器...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                GEMMA_MODEL_NAME,
                cache_dir=str(MODELS_DIR),
                trust_remote_code=True  # 支援 Gemma 3n
            )
            
            # 載入模型
            logger.info(f"載入 {GEMMA_MODEL_NAME} 模型...")
            
            if quantization_config and device == "cuda":
                # GPU 模式：使用量化模型
                self.model = AutoModelForCausalLM.from_pretrained(
                    GEMMA_MODEL_NAME,
                    quantization_config=quantization_config,
                    device_map="auto",
                    cache_dir=str(MODELS_DIR),
                    torch_dtype=torch.float16,
                    trust_remote_code=True  # 支援 Gemma 3n
                )
            else:
                # CPU 模式：使用全精度模型
                self.model = AutoModelForCausalLM.from_pretrained(
                    GEMMA_MODEL_NAME,
                    cache_dir=str(MODELS_DIR),
                    torch_dtype=torch.float32,  # CPU 模式使用 float32 以獲得更好穩定性
                    trust_remote_code=True  # 支援 Gemma 3n
                )
                # 明確將模型移到指定設備
                self.model = self.model.to(device)
            
            # 創建 pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if device == "cuda" else -1,  # -1 表示 CPU
                max_new_tokens=GEMMA_MAX_LENGTH,
                temperature=GEMMA_TEMPERATURE,
                do_sample=True,
                top_p=0.95,
                top_k=50
            )
            
            self.is_initialized = True
            logger.info(f"Gemma 翻譯模型初始化完成 (設備: {device.upper()})")
            
        except Exception as e:
            logger.error(f"初始化 Gemma 模型失敗: {e}")
            raise
    
    def translate(self, text: str, target_language: str) -> Optional[str]:
        """
        翻譯文字
        
        Args:
            text: 要翻譯的文字
            target_language: 目標語言代碼
            
        Returns:
            翻譯後的文字或 None
        """
        if not self.is_initialized:
            logger.error("翻譯模型尚未初始化")
            return None
        
        if not text.strip():
            return None
        
        try:
            # 檢查快取
            cache_key = f"{text}:{target_language}"
            cached_translation = self.translation_cache.get(cache_key)
            if cached_translation:
                logger.debug("使用快取的翻譯")
                return cached_translation
            
            # 準備提示詞
            target_lang_name = self.language_names.get(target_language, target_language)
            
            # 建構包含上下文的提示詞
            prompt = self._build_translation_prompt(text, target_lang_name)
            
            # 執行翻譯
            with torch.no_grad():
                outputs = self.pipeline(
                    prompt,
                    max_new_tokens=GEMMA_MAX_LENGTH,
                    temperature=GEMMA_TEMPERATURE,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    return_full_text=False
                )
            
            # 提取翻譯結果
            if outputs and len(outputs) > 0:
                translation = outputs[0]['generated_text'].strip()
                
                # 清理翻譯結果
                translation = self._clean_translation(translation)
                
                if translation:
                    # 加入快取
                    self.translation_cache.put(cache_key, translation)
                    
                    # 更新上下文
                    self._update_context(text, translation)
                    
                    logger.debug(f"翻譯結果: {translation}")
                    return translation
            
            return None
            
        except Exception as e:
            logger.error(f"翻譯失敗: {e}")
            return None
    
    def _build_translation_prompt(self, text: str, target_language: str) -> str:
        """建構翻譯提示詞"""
        # 基礎提示詞
        prompt = f"""You are a professional translator. Translate the following text to {target_language}.
Maintain the original meaning and tone. Consider the context from previous translations.

"""
        
        # 加入上下文（如果有）
        if self.context_buffer:
            prompt += "Previous context:\n"
            for source, translated in self.context_buffer[-3:]:  # 最近3條
                prompt += f"Original: {source}\n"
                prompt += f"Translation: {translated}\n"
            prompt += "\n"
        
        # 加入要翻譯的文字
        prompt += f"Translate this text to {target_language}:\n{text}\n\nTranslation:"
        
        return prompt
    
    def _clean_translation(self, translation: str) -> str:
        """清理翻譯結果"""
        # 移除可能的多餘標記
        translation = translation.strip()
        
        # 移除可能的語言標記
        for lang_name in self.language_names.values():
            if translation.startswith(f"{lang_name}:"):
                translation = translation[len(f"{lang_name}:"):]
            if translation.startswith(f"Translation to {lang_name}:"):
                translation = translation[len(f"Translation to {lang_name}:"):]
        
        # 移除引號（如果整個翻譯被引號包圍）
        if len(translation) > 2:
            if (translation.startswith('"') and translation.endswith('"')) or \
               (translation.startswith("'") and translation.endswith("'")):
                translation = translation[1:-1]
        
        return translation.strip()
    
    def _update_context(self, source: str, translation: str):
        """更新上下文緩衝區"""
        self.context_buffer.append((source, translation))
        
        # 保持緩衝區大小
        if len(self.context_buffer) > self.max_context_length:
            self.context_buffer.pop(0)
    
    def translate_batch(self, texts: List[str], target_language: str) -> List[Optional[str]]:
        """批次翻譯多個文字"""
        translations = []
        
        for text in texts:
            translation = self.translate(text, target_language)
            translations.append(translation)
        
        return translations
    
    def clear_context(self):
        """清除上下文"""
        self.context_buffer.clear()
    
    def clear_cache(self):
        """清除翻譯快取"""
        self.translation_cache.clear()
    
    def cleanup(self):
        """清理資源"""
        if self.model:
            del self.model
            self.model = None
        
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
        
        if self.pipeline:
            del self.pipeline
            self.pipeline = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.is_initialized = False
        logger.info("翻譯模型已清理")


class GemmaTranslator(Translator):
    """
    Gemma 專用翻譯器 - 針對 Gemma 模型優化
    """
    
    def _build_translation_prompt(self, text: str, target_language: str) -> str:
        """建構 Gemma 3n 優化的提示詞"""
        # Gemma 3n IT 支援更自然的對話格式
        messages = [
            {
                "role": "system",
                "content": f"You are a professional real-time translator for live streaming content. Translate the given text to {target_language} while maintaining natural flow and fixing obvious speech recognition errors."
            }
        ]
        
        # 加入上下文
        if self.context_buffer:
            context_info = "Recent context: "
            for source, translated in self.context_buffer[-2:]:
                context_info += f"'{source}' → '{translated}'; "
            messages.append({
                "role": "user",
                "content": f"{context_info}\n\nNow translate: {text}"
            })
        else:
            messages.append({
                "role": "user",
                "content": f"Translate to {target_language}: {text}"
            })
        
        # 使用 tokenizer 的 chat template
        if hasattr(self.tokenizer, 'apply_chat_template') and self.tokenizer.chat_template:
            try:
                prompt = self.tokenizer.apply_chat_template(
                    messages, 
                    tokenize=False, 
                    add_generation_prompt=True
                )
                return prompt
            except Exception as e:
                logger.warning(f"無法使用 chat template，使用回退格式: {e}")
        
        # 回退到基礎格式
        prompt = f"<bos><start_of_turn>user\n"
        prompt += f"Translate to {target_language}: {text}\n"
        prompt += "<end_of_turn>\n<start_of_turn>model\n"
        
        return prompt
    
    def _optimize_for_streaming(self):
        """優化串流翻譯設定"""
        if self.pipeline:
            # 調整生成參數以提高速度
            self.pipeline.model.config.max_new_tokens = 100  # 限制輸出長度
            self.pipeline.model.config.temperature = 0.7    # 平衡創意和準確性
            self.pipeline.model.config.top_p = 0.9          # 核採樣
            self.pipeline.model.config.repetition_penalty = 1.1  # 避免重複 