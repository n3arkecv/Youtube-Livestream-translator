"""
主視窗GUI - 控制面板
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QComboBox,
                            QSpinBox, QColorDialog, QSlider, QGroupBox,
                            QTextEdit, QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QTime
from PyQt5.QtGui import QFont, QIcon, QColor
import sys
import os

from ..audio.stream_capture import StreamCapture
from ..models.whisper_model import WhisperModel
from ..models.gemma_translator import GemmaTranslator
from .overlay_window import OverlayWindow
from ..utils.config import Config

class TranslationThread(QThread):
    """翻譯處理執行緒"""
    status_update = pyqtSignal(str)
    subtitle_update = pyqtSignal(str, str)  # 原文, 譯文
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.stream_capture = None
        self.whisper_model = None
        self.translator = None
        self.is_running = False
        self.youtube_url = ""
        self.source_lang = "en"
        self.target_lang = "zh"
        
    def setup(self, youtube_url, source_lang, target_lang):
        self.youtube_url = youtube_url
        self.source_lang = source_lang
        self.target_lang = target_lang
        
    def run(self):
        try:
            self.is_running = True
            self.status_update.emit("正在初始化模型...")
            
            # 初始化模型
            self.whisper_model = WhisperModel(language=self.source_lang)
            self.translator = GemmaTranslator(target_lang=self.target_lang)
            self.stream_capture = StreamCapture()
            
            self.status_update.emit("正在連接到YouTube直播...")
            
            # 開始擷取音訊
            audio_stream = self.stream_capture.start_capture(self.youtube_url)
            
            self.status_update.emit("開始轉錄和翻譯...")
            
            # 處理音訊串流
            for audio_chunk in audio_stream:
                if not self.is_running:
                    break
                    
                # 使用Whisper轉錄
                transcription = self.whisper_model.transcribe(audio_chunk)
                
                if transcription:
                    # 使用Gemma翻譯
                    translation = self.translator.translate(transcription, context=True)
                    
                    # 發送字幕更新
                    self.subtitle_update.emit(transcription, translation)
                    
        except Exception as e:
            self.error_occurred.emit(f"錯誤: {str(e)}")
        finally:
            self.cleanup()
            
    def stop(self):
        self.is_running = False
        self.status_update.emit("正在停止...")
        
    def cleanup(self):
        if self.stream_capture:
            self.stream_capture.stop_capture()
        self.status_update.emit("已停止")

class MainWindow(QMainWindow):
    """主控制視窗"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.overlay_window = None
        self.translation_thread = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("YouTube Live Translator - 即時直播翻譯字幕")
        self.setGeometry(100, 100, 800, 600)
        
        # 主要元件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # URL輸入區域
        url_group = QGroupBox("直播設定")
        url_layout = QVBoxLayout()
        
        url_input_layout = QHBoxLayout()
        url_input_layout.addWidget(QLabel("YouTube直播網址:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        url_input_layout.addWidget(self.url_input)
        url_layout.addLayout(url_input_layout)
        
        # 語言設定
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("來源語言:"))
        self.source_lang_combo = QComboBox()
        self.source_lang_combo.addItems([
            "en - English",
            "ja - 日本語",
            "ko - 한국어",
            "es - Español",
            "fr - Français",
            "de - Deutsch",
            "it - Italiano",
            "pt - Português",
            "ru - Русский",
            "ar - العربية",
            "hi - हिन्दी"
        ])
        lang_layout.addWidget(self.source_lang_combo)
        
        lang_layout.addWidget(QLabel("目標語言:"))
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems([
            "zh - 中文",
            "en - English",
            "ja - 日本語",
            "ko - 한국어",
            "es - Español",
            "fr - Français",
            "de - Deutsch"
        ])
        lang_layout.addWidget(self.target_lang_combo)
        url_layout.addLayout(lang_layout)
        
        url_group.setLayout(url_layout)
        main_layout.addWidget(url_group)
        
        # 字幕樣式設定
        style_group = QGroupBox("字幕樣式")
        style_layout = QVBoxLayout()
        
        # 字體大小
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("字體大小:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(12, 72)
        self.font_size_spin.setValue(24)
        self.font_size_spin.valueChanged.connect(self.update_overlay_style)
        font_layout.addWidget(self.font_size_spin)
        
        # 字體顏色
        self.font_color_btn = QPushButton("選擇字體顏色")
        self.font_color_btn.clicked.connect(self.select_font_color)
        self.font_color = QColor(255, 255, 255)
        font_layout.addWidget(self.font_color_btn)
        
        # 背景顏色
        self.bg_color_btn = QPushButton("選擇背景顏色")
        self.bg_color_btn.clicked.connect(self.select_bg_color)
        self.bg_color = QColor(0, 0, 0, 180)
        font_layout.addWidget(self.bg_color_btn)
        
        style_layout.addLayout(font_layout)
        
        # 位置設定
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("垂直位置:"))
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 100)
        self.position_slider.setValue(80)  # 預設在螢幕下方
        self.position_slider.valueChanged.connect(self.update_overlay_position)
        position_layout.addWidget(self.position_slider)
        self.position_label = QLabel("80%")
        position_layout.addWidget(self.position_label)
        
        style_layout.addLayout(position_layout)
        
        # 陰影設定
        shadow_layout = QHBoxLayout()
        self.shadow_check = QCheckBox("啟用文字陰影")
        self.shadow_check.setChecked(True)
        self.shadow_check.stateChanged.connect(self.update_overlay_style)
        shadow_layout.addWidget(self.shadow_check)
        
        shadow_layout.addWidget(QLabel("陰影強度:"))
        self.shadow_slider = QSlider(Qt.Horizontal)
        self.shadow_slider.setRange(0, 10)
        self.shadow_slider.setValue(5)
        self.shadow_slider.valueChanged.connect(self.update_overlay_style)
        shadow_layout.addWidget(self.shadow_slider)
        
        style_layout.addLayout(shadow_layout)
        
        style_group.setLayout(style_layout)
        main_layout.addWidget(style_group)
        
        # 控制按鈕
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("開始翻譯")
        self.start_btn.clicked.connect(self.start_translation)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止翻譯")
        self.stop_btn.clicked.connect(self.stop_translation)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        self.preview_btn = QPushButton("預覽字幕疊層")
        self.preview_btn.clicked.connect(self.preview_overlay)
        control_layout.addWidget(self.preview_btn)
        
        main_layout.addLayout(control_layout)
        
        # 狀態顯示
        status_group = QGroupBox("狀態")
        status_layout = QVBoxLayout()
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)
        status_layout.addWidget(self.status_text)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # 應用樣式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
    def start_translation(self):
        """開始翻譯"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "警告", "請輸入YouTube直播網址")
            return
            
        # 獲取語言設定
        source_lang = self.source_lang_combo.currentText().split(" - ")[0]
        target_lang = self.target_lang_combo.currentText().split(" - ")[0]
        
        # 創建並顯示疊層視窗
        if not self.overlay_window:
            self.overlay_window = OverlayWindow()
            self.update_overlay_style()
            self.update_overlay_position()
            
        self.overlay_window.show()
        
        # 創建並啟動翻譯執行緒
        self.translation_thread = TranslationThread()
        self.translation_thread.setup(url, source_lang, target_lang)
        self.translation_thread.status_update.connect(self.update_status)
        self.translation_thread.subtitle_update.connect(self.update_subtitle)
        self.translation_thread.error_occurred.connect(self.handle_error)
        self.translation_thread.start()
        
        # 更新UI狀態
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.url_input.setEnabled(False)
        
    def stop_translation(self):
        """停止翻譯"""
        if self.translation_thread:
            self.translation_thread.stop()
            self.translation_thread.wait()
            
        if self.overlay_window:
            self.overlay_window.hide()
            
        # 更新UI狀態
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.url_input.setEnabled(True)
        
    def preview_overlay(self):
        """預覽字幕疊層"""
        if not self.overlay_window:
            self.overlay_window = OverlayWindow()
            self.update_overlay_style()
            self.update_overlay_position()
            
        self.overlay_window.show()
        self.overlay_window.update_subtitle("這是預覽文字\nThis is preview text", 
                                          "這是翻譯後的文字\nThis is translated text")
        
    def update_status(self, status):
        """更新狀態顯示"""
        self.status_text.append(f"[{QTime.currentTime().toString()}] {status}")
        
    def update_subtitle(self, original, translated):
        """更新字幕"""
        if self.overlay_window:
            self.overlay_window.update_subtitle(original, translated)
            
    def handle_error(self, error):
        """處理錯誤"""
        QMessageBox.critical(self, "錯誤", error)
        self.stop_translation()
        
    def select_font_color(self):
        """選擇字體顏色"""
        color = QColorDialog.getColor(self.font_color, self)
        if color.isValid():
            self.font_color = color
            self.update_overlay_style()
            
    def select_bg_color(self):
        """選擇背景顏色"""
        color = QColorDialog.getColor(self.bg_color, self)
        if color.isValid():
            self.bg_color = color
            self.update_overlay_style()
            
    def update_overlay_style(self):
        """更新疊層樣式"""
        if self.overlay_window:
            self.overlay_window.set_style(
                font_size=self.font_size_spin.value(),
                font_color=self.font_color,
                bg_color=self.bg_color,
                shadow_enabled=self.shadow_check.isChecked(),
                shadow_strength=self.shadow_slider.value()
            )
            
    def update_overlay_position(self):
        """更新疊層位置"""
        position = self.position_slider.value()
        self.position_label.setText(f"{position}%")
        if self.overlay_window:
            self.overlay_window.set_position(position)
            
    def closeEvent(self, event):
        """關閉事件處理"""
        self.stop_translation()
        event.accept()