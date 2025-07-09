"""
YouTube直播音訊串流擷取模組
"""

import yt_dlp
import numpy as np
import sounddevice as sd
import threading
import queue
import time
from urllib.parse import urlparse, parse_qs
import subprocess
import tempfile
import os

class StreamCapture:
    """YouTube直播音訊擷取器"""
    
    def __init__(self):
        self.is_capturing = False
        self.audio_queue = queue.Queue()
        self.capture_thread = None
        self.ffmpeg_process = None
        self.sample_rate = 16000  # Whisper需要16kHz
        self.chunk_duration = 3  # 每3秒一個音訊片段
        
    def start_capture(self, youtube_url):
        """開始擷取音訊串流"""
        if self.is_capturing:
            raise RuntimeError("Already capturing")
            
        self.is_capturing = True
        self.capture_thread = threading.Thread(
            target=self._capture_stream,
            args=(youtube_url,),
            daemon=True
        )
        self.capture_thread.start()
        
        # 返回音訊串流生成器
        return self._audio_generator()
        
    def stop_capture(self):
        """停止擷取"""
        self.is_capturing = False
        
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            self.ffmpeg_process = None
            
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
            
    def _capture_stream(self, youtube_url):
        """擷取串流的主要邏輯"""
        try:
            # 設定yt-dlp選項
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'live_from_start': True,  # 從直播開始處開始
            }
            
            # 獲取直播串流URL
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
                if not info.get('is_live'):
                    raise ValueError("This is not a live stream")
                    
                # 獲取音訊串流URL
                formats = info.get('formats', [])
                audio_url = None
                
                for fmt in formats:
                    if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                        audio_url = fmt.get('url')
                        break
                        
                if not audio_url:
                    # 如果找不到純音訊串流，使用最佳音訊
                    audio_url = info.get('url')
                    
            # 使用FFmpeg處理音訊串流
            self._process_with_ffmpeg(audio_url)
            
        except Exception as e:
            print(f"Error capturing stream: {e}")
            self.audio_queue.put(None)  # 發送結束信號
            
    def _process_with_ffmpeg(self, audio_url):
        """使用FFmpeg處理音訊串流"""
        # FFmpeg命令：將串流轉換為16kHz單聲道PCM
        cmd = [
            'ffmpeg',
            '-i', audio_url,
            '-f', 's16le',  # 16-bit PCM
            '-acodec', 'pcm_s16le',
            '-ar', str(self.sample_rate),  # 採樣率
            '-ac', '1',  # 單聲道
            '-'  # 輸出到stdout
        ]
        
        # 啟動FFmpeg進程
        self.ffmpeg_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0
        )
        
        # 讀取音訊數據
        chunk_size = int(self.sample_rate * self.chunk_duration * 2)  # 2 bytes per sample
        
        while self.is_capturing:
            try:
                # 讀取音訊數據
                audio_data = self.ffmpeg_process.stdout.read(chunk_size)
                
                if not audio_data:
                    break
                    
                # 轉換為numpy數組
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                
                # 正規化到[-1, 1]
                audio_normalized = audio_array.astype(np.float32) / 32768.0
                
                # 放入隊列
                self.audio_queue.put(audio_normalized)
                
            except Exception as e:
                print(f"Error processing audio: {e}")
                break
                
        # 發送結束信號
        self.audio_queue.put(None)
        
    def _audio_generator(self):
        """音訊串流生成器"""
        while self.is_capturing:
            try:
                # 從隊列獲取音訊數據
                audio_chunk = self.audio_queue.get(timeout=1)
                
                if audio_chunk is None:
                    break
                    
                yield audio_chunk
                
            except queue.Empty:
                continue
                
class MockStreamCapture:
    """模擬音訊擷取器（用於測試）"""
    
    def __init__(self):
        self.is_capturing = False
        self.sample_rate = 16000
        
    def start_capture(self, youtube_url):
        """開始模擬擷取"""
        self.is_capturing = True
        return self._mock_audio_generator()
        
    def stop_capture(self):
        """停止擷取"""
        self.is_capturing = False
        
    def _mock_audio_generator(self):
        """生成模擬音訊"""
        duration = 3  # 3秒片段
        
        while self.is_capturing:
            # 生成靜音或測試音訊
            samples = int(self.sample_rate * duration)
            audio_chunk = np.zeros(samples, dtype=np.float32)
            
            # 可以加入測試音訊，例如正弦波
            # t = np.linspace(0, duration, samples)
            # audio_chunk = 0.1 * np.sin(2 * np.pi * 440 * t)
            
            yield audio_chunk
            time.sleep(duration)