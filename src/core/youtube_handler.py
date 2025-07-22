"""
YouTube 直播音訊處理器
"""
import logging
import threading
import queue
import time
import subprocess
import os
import tempfile
from pathlib import Path

import yt_dlp
import numpy as np
from pydub import AudioSegment
import sounddevice as sd

from ..config import AUDIO_SAMPLE_RATE, AUDIO_CHUNK_DURATION, AUDIO_BUFFER_SIZE

logger = logging.getLogger(__name__)


class YouTubeHandler:
    """YouTube 直播處理器"""
    
    def __init__(self):
        self.url = None
        self.is_connected = False
        self.is_downloading = False
        self.audio_queue = queue.Queue(maxsize=100)
        self.download_thread = None
        self.process = None
        self.temp_dir = None
        
        # yt-dlp 設定
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,  # 只獲取資訊，不下載
        }
    
    def connect(self, url):
        """連接到 YouTube 直播"""
        try:
            self.url = url
            logger.info(f"正在連接到 YouTube 直播: {url}")
            
            # 驗證 URL 並獲取直播資訊
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # 檢查是否為直播
                if not info.get('is_live', False):
                    logger.error("這不是一個直播串流")
                    return False
                
                # 獲取音訊串流 URL
                formats = info.get('formats', [])
                audio_url = None
                
                # 尋找最佳音訊格式
                for fmt in formats:
                    if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                        audio_url = fmt.get('url')
                        break
                
                if not audio_url:
                    # 如果沒有純音訊串流，使用最佳格式
                    audio_url = info.get('url')
                
                if not audio_url:
                    logger.error("無法獲取音訊串流 URL")
                    return False
                
                self.stream_url = audio_url
                self.is_connected = True
                
                # 創建臨時目錄
                self.temp_dir = tempfile.mkdtemp(prefix="youtube_translator_")
                
                # 開始下載執行緒
                self.is_downloading = True
                self.download_thread = threading.Thread(target=self._download_stream)
                self.download_thread.daemon = True
                self.download_thread.start()
                
                logger.info("成功連接到 YouTube 直播")
                return True
                
        except Exception as e:
            logger.error(f"連接 YouTube 直播失敗: {e}")
            return False
    
    def _download_stream(self):
        """下載串流音訊"""
        try:
            # 使用 ffmpeg 下載並轉換音訊
            output_path = os.path.join(self.temp_dir, "audio.wav")
            
            cmd = [
                'ffmpeg',
                '-i', self.stream_url,
                '-acodec', 'pcm_s16le',
                '-ar', str(AUDIO_SAMPLE_RATE),
                '-ac', '1',  # 單聲道
                '-f', 'wav',
                '-y',  # 覆蓋輸出檔案
                output_path
            ]
            
            # 啟動 ffmpeg 程序
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            
            # 持續讀取音訊數據
            chunk_samples = int(AUDIO_SAMPLE_RATE * AUDIO_CHUNK_DURATION)
            
            while self.is_downloading:
                try:
                    # 檢查輸出檔案是否存在且有新數據
                    if os.path.exists(output_path):
                        # 讀取音訊檔案
                        audio = AudioSegment.from_wav(output_path)
                        
                        # 分割成固定長度的片段
                        duration_ms = len(audio)
                        chunk_ms = AUDIO_CHUNK_DURATION * 1000
                        
                        for i in range(0, duration_ms - chunk_ms, chunk_ms):
                            chunk = audio[i:i + chunk_ms]
                            
                            # 轉換為 numpy 陣列
                            samples = np.array(chunk.get_array_of_samples())
                            
                            # 正規化到 [-1, 1]
                            samples = samples.astype(np.float32) / 32768.0
                            
                            # 加入佇列
                            try:
                                self.audio_queue.put(samples, timeout=0.1)
                            except queue.Full:
                                # 佇列滿了，丟棄舊的音訊
                                try:
                                    self.audio_queue.get_nowait()
                                    self.audio_queue.put(samples, timeout=0.1)
                                except:
                                    pass
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"處理音訊時發生錯誤: {e}")
                    time.sleep(1)
            
        except Exception as e:
            logger.error(f"下載串流失敗: {e}")
        finally:
            if self.process:
                self.process.terminate()
                self.process = None
    
    def get_audio_chunk(self):
        """獲取音訊片段"""
        try:
            # 從佇列獲取音訊數據
            return self.audio_queue.get(timeout=1.0)
        except queue.Empty:
            return None
    
    def disconnect(self):
        """斷開連接"""
        logger.info("正在斷開 YouTube 連接...")
        
        self.is_downloading = False
        self.is_connected = False
        
        # 等待下載執行緒結束
        if self.download_thread and self.download_thread.is_alive():
            self.download_thread.join(timeout=5)
        
        # 終止 ffmpeg 程序
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            self.process = None
        
        # 清理臨時檔案
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
            except:
                pass
        
        # 清空佇列
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except:
                break
        
        logger.info("已斷開 YouTube 連接")


class YouTubeHandlerAlternative:
    """
    備用的 YouTube 處理器實作
    使用不同的方法來處理直播串流
    """
    
    def __init__(self):
        self.url = None
        self.is_connected = False
        self.audio_buffer = []
        self.buffer_lock = threading.Lock()
        self.download_thread = None
        self.is_downloading = False
    
    def connect(self, url):
        """連接到 YouTube 直播"""
        try:
            self.url = url
            logger.info(f"使用備用方法連接到 YouTube 直播: {url}")
            
            # 創建 yt-dlp 下載器
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'prefer_ffmpeg': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'outtmpl': '-',  # 輸出到 stdout
            }
            
            self.ydl = yt_dlp.YoutubeDL(ydl_opts)
            
            # 驗證 URL
            info = self.ydl.extract_info(url, download=False)
            if not info.get('is_live', False):
                logger.error("這不是一個直播串流")
                return False
            
            self.is_connected = True
            self.is_downloading = True
            
            # 開始下載執行緒
            self.download_thread = threading.Thread(target=self._download_stream_alternative)
            self.download_thread.daemon = True
            self.download_thread.start()
            
            logger.info("成功連接到 YouTube 直播（備用方法）")
            return True
            
        except Exception as e:
            logger.error(f"連接 YouTube 直播失敗: {e}")
            return False
    
    def _download_stream_alternative(self):
        """使用備用方法下載串流"""
        try:
            # 使用 yt-dlp 的 Python API 直接下載
            info = self.ydl.extract_info(self.url, download=False)
            
            # 獲取串流 URL
            stream_url = info['url']
            
            # 使用 ffmpeg-python 或直接調用 ffmpeg
            import ffmpeg
            
            # 創建 ffmpeg 串流
            stream = ffmpeg.input(stream_url)
            stream = ffmpeg.output(
                stream, 
                'pipe:', 
                format='f32le',
                acodec='pcm_f32le',
                ac=1,
                ar=AUDIO_SAMPLE_RATE
            )
            
            # 啟動 ffmpeg 程序
            process = ffmpeg.run_async(
                stream,
                pipe_stdout=True,
                pipe_stderr=True
            )
            
            # 讀取音訊數據
            chunk_size = int(AUDIO_SAMPLE_RATE * AUDIO_CHUNK_DURATION * 4)  # 4 bytes per float32
            
            while self.is_downloading:
                data = process.stdout.read(chunk_size)
                if not data:
                    break
                
                # 轉換為 numpy 陣列
                audio_chunk = np.frombuffer(data, dtype=np.float32)
                
                # 加入緩衝區
                with self.buffer_lock:
                    self.audio_buffer.append(audio_chunk)
                    
                    # 限制緩衝區大小
                    max_chunks = int(AUDIO_BUFFER_SIZE / AUDIO_CHUNK_DURATION)
                    if len(self.audio_buffer) > max_chunks:
                        self.audio_buffer.pop(0)
            
            process.wait()
            
        except Exception as e:
            logger.error(f"備用下載方法失敗: {e}")
    
    def get_audio_chunk(self):
        """獲取音訊片段"""
        with self.buffer_lock:
            if self.audio_buffer:
                return self.audio_buffer.pop(0)
        return None
    
    def disconnect(self):
        """斷開連接"""
        self.is_downloading = False
        self.is_connected = False
        
        if self.download_thread and self.download_thread.is_alive():
            self.download_thread.join(timeout=5)
        
        with self.buffer_lock:
            self.audio_buffer.clear() 