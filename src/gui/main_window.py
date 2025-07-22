"""
主視窗介面
"""
import sys
import logging
import time
import gc
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QGroupBox, QTextEdit,
    QSlider, QCheckBox, QColorDialog, QProgressBar, QSystemTrayIcon,
    QMenu, QMessageBox, QAction
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor

from ..core.youtube_handler import YouTubeHandler
from ..core.transcriber import Transcriber
from ..core.translator import GemmaTranslator
from ..config import APP_NAME, SUPPORTED_LANGUAGES, DEFAULT_SUBTITLE_SETTINGS
from .subtitle_window import SubtitleWindow
from .settings_dialog import SettingsDialog


logger = logging.getLogger(__name__)


class ProcessingThread(QThread):
    """處理執行緒"""
    status_update = pyqtSignal(str)
    subtitle_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, url, source_lang, target_lang):
        super().__init__()
        self.url = url
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.is_running = False
        
        self.youtube_handler = YouTubeHandler()
        self.transcriber = Transcriber()
        self.translator = GemmaTranslator()  # 使用 Gemma 最佳化版本
    
    def run(self):
        """執行處理"""
        try:
            self.is_running = True
            self.status_update.emit("正在連接 YouTube 直播...")
            
            # 連接到 YouTube 直播
            if not self.youtube_handler.connect(self.url):
                self.error_occurred.emit("無法連接到 YouTube 直播")
                return
            
            self.status_update.emit("正在初始化語音識別...")
            self.transcriber.initialize()
            
            self.status_update.emit("正在初始化翻譯引擎...")
            self.translator.initialize()
            
            self.status_update.emit("開始處理直播內容...")
            
            # 主處理迴圈
            audio_buffer = []
            last_process_time = time.time()
            
            while self.is_running:
                try:
                    # 獲取音訊
                    audio_chunk = self.youtube_handler.get_audio_chunk()
                    if audio_chunk is None:
                        time.sleep(0.1)  # 避免 CPU 100% 使用率
                        continue
                    
                    # 累積音訊塊到緩衝區
                    audio_buffer.extend(audio_chunk)
                    
                    # 每 3 秒處理一次（避免過於頻繁的處理）
                    current_time = time.time()
                    if current_time - last_process_time < 3.0:
                        continue
                    
                    if len(audio_buffer) == 0:
                        continue
                    
                    # 處理累積的音訊
                    try:
                        # 語音轉文字
                        text = self.transcriber.transcribe(audio_buffer, self.source_lang)
                        
                        # 清理音訊緩衝區釋放記憶體
                        audio_buffer.clear()
                        last_process_time = current_time
                        
                        if not text or not text.strip():
                            continue
                        
                        # 翻譯
                        translated = self.translator.translate(text, self.target_lang)
                        if translated and translated.strip():
                            self.subtitle_update.emit(translated)
                            
                    except Exception as e:
                        logger.error(f"處理音訊時出錯: {e}")
                        audio_buffer.clear()  # 清理緩衝區
                        continue
                    
                    # 強制垃圾回收
                    if current_time - last_process_time > 10:
                        gc.collect()
                        
                except Exception as e:
                    logger.error(f"主循環錯誤: {e}")
                    time.sleep(1)  # 出錯時暫停 1 秒
                    continue
            
        except Exception as e:
            logger.error(f"處理執行緒錯誤: {e}", exc_info=True)
            self.error_occurred.emit(str(e))
        finally:
            self.cleanup()
    
    def stop(self):
        """停止處理"""
        self.is_running = False
    
    def cleanup(self):
        """清理資源"""
        self.youtube_handler.disconnect()
        self.status_update.emit("已停止")


class MainWindow(QMainWindow):
    """主視窗"""
    
    def __init__(self):
        super().__init__()
        self.processing_thread = None
        self.subtitle_window = None
        self.subtitle_settings = DEFAULT_SUBTITLE_SETTINGS.copy()
        
        self.init_ui()
        self.setup_tray_icon()
    
    def init_ui(self):
        """初始化使用者介面"""
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(800, 600)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 標題
        title_label = QLabel(APP_NAME)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # URL 輸入區
        url_group = QGroupBox("YouTube 直播網址")
        url_layout = QHBoxLayout(url_group)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("請輸入 YouTube 直播網址...")
        url_layout.addWidget(self.url_input)
        
        self.validate_btn = QPushButton("驗證")
        self.validate_btn.clicked.connect(self.validate_url)
        url_layout.addWidget(self.validate_btn)
        
        main_layout.addWidget(url_group)
        
        # 語言設定區
        lang_group = QGroupBox("語言設定")
        lang_layout = QHBoxLayout(lang_group)
        
        lang_layout.addWidget(QLabel("來源語言:"))
        self.source_lang_combo = QComboBox()
        self.source_lang_combo.addItems([f"{name}" for code, name in SUPPORTED_LANGUAGES.items()])
        self.source_lang_combo.setCurrentIndex(0)  # 預設自動偵測
        lang_layout.addWidget(self.source_lang_combo)
        
        lang_layout.addWidget(QLabel("目標語言:"))
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems([f"{name}" for code, name in SUPPORTED_LANGUAGES.items() if code != "auto"])
        self.target_lang_combo.setCurrentText("中文")
        lang_layout.addWidget(self.target_lang_combo)
        
        main_layout.addWidget(lang_group)
        
        # 字幕設定區
        subtitle_group = QGroupBox("字幕設定")
        subtitle_layout = QVBoxLayout(subtitle_group)
        
        # 字體設定
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("字體大小:"))
        
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(12, 72)
        self.font_size_slider.setValue(self.subtitle_settings["font_size"])
        self.font_size_slider.valueChanged.connect(self.update_font_size)
        font_layout.addWidget(self.font_size_slider)
        
        self.font_size_label = QLabel(str(self.subtitle_settings["font_size"]))
        font_layout.addWidget(self.font_size_label)
        
        subtitle_layout.addLayout(font_layout)
        
        # 顏色設定
        color_layout = QHBoxLayout()
        
        self.font_color_btn = QPushButton("字體顏色")
        self.font_color_btn.clicked.connect(self.choose_font_color)
        self.font_color_btn.setStyleSheet(f"background-color: {self.subtitle_settings['font_color']}")
        color_layout.addWidget(self.font_color_btn)
        
        self.bg_color_btn = QPushButton("背景顏色")
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        self.bg_color_btn.setStyleSheet(f"background-color: {self.subtitle_settings['background_color']}")
        color_layout.addWidget(self.bg_color_btn)
        
        self.shadow_check = QCheckBox("啟用陰影")
        self.shadow_check.setChecked(self.subtitle_settings["shadow_enabled"])
        self.shadow_check.stateChanged.connect(self.toggle_shadow)
        color_layout.addWidget(self.shadow_check)
        
        subtitle_layout.addLayout(color_layout)
        
        # 進階設定按鈕
        self.advanced_settings_btn = QPushButton("進階字幕設定")
        self.advanced_settings_btn.clicked.connect(self.show_settings_dialog)
        subtitle_layout.addWidget(self.advanced_settings_btn)
        
        main_layout.addWidget(subtitle_group)
        
        # 控制按鈕區
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("開始翻譯")
        self.start_btn.clicked.connect(self.start_translation)
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        control_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("暫停")
        self.pause_btn.clicked.connect(self.pause_translation)
        self.pause_btn.setEnabled(False)
        control_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_translation)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("QPushButton:enabled { background-color: #f44336; color: white; }")
        control_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(control_layout)
        
        # 狀態列
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就緒")
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # 日誌區域
        log_group = QGroupBox("執行日誌")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        main_layout.addWidget(log_group)
    
    def setup_tray_icon(self):
        """設定系統托盤圖示"""
        self.tray_icon = QSystemTrayIcon(self)
        # 如果有圖示檔案的話可以設定
        # self.tray_icon.setIcon(QIcon("assets/icon.ico"))
        
        # 托盤選單
        tray_menu = QMenu()
        
        show_action = QAction("顯示主視窗", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("結束", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        """托盤圖示被點擊"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
    
    def validate_url(self):
        """驗證 YouTube URL"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "警告", "請輸入 YouTube 網址")
            return
        
        # 簡單的 URL 驗證
        if "youtube.com" in url or "youtu.be" in url:
            self.log_message("URL 驗證成功")
            QMessageBox.information(self, "成功", "URL 格式正確")
        else:
            QMessageBox.warning(self, "錯誤", "請輸入有效的 YouTube 網址")
    
    def update_font_size(self, value):
        """更新字體大小"""
        self.font_size_label.setText(str(value))
        self.subtitle_settings["font_size"] = value
        if self.subtitle_window:
            self.subtitle_window.update_settings(self.subtitle_settings)
    
    def choose_font_color(self):
        """選擇字體顏色"""
        color = QColorDialog.getColor(Qt.white, self, "選擇字體顏色")
        if color.isValid():
            self.subtitle_settings["font_color"] = color.name()
            self.font_color_btn.setStyleSheet(f"background-color: {color.name()}")
            if self.subtitle_window:
                self.subtitle_window.update_settings(self.subtitle_settings)
    
    def choose_bg_color(self):
        """選擇背景顏色"""
        color = QColorDialog.getColor(Qt.black, self, "選擇背景顏色")
        if color.isValid():
            self.subtitle_settings["background_color"] = color.name()
            self.bg_color_btn.setStyleSheet(f"background-color: {color.name()}")
            if self.subtitle_window:
                self.subtitle_window.update_settings(self.subtitle_settings)
    
    def toggle_shadow(self, state):
        """切換陰影"""
        self.subtitle_settings["shadow_enabled"] = state == Qt.Checked
        if self.subtitle_window:
            self.subtitle_window.update_settings(self.subtitle_settings)
    
    def show_settings_dialog(self):
        """顯示進階設定對話框"""
        dialog = SettingsDialog(self.subtitle_settings, self)
        if dialog.exec_():
            self.subtitle_settings = dialog.get_settings()
            if self.subtitle_window:
                self.subtitle_window.update_settings(self.subtitle_settings)
    
    def start_translation(self):
        """開始翻譯"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "警告", "請輸入 YouTube 網址")
            return
        
        # 獲取選擇的語言
        source_lang_index = self.source_lang_combo.currentIndex()
        source_lang = list(SUPPORTED_LANGUAGES.keys())[source_lang_index]
        
        target_lang_text = self.target_lang_combo.currentText()
        target_lang = next(code for code, name in SUPPORTED_LANGUAGES.items() if name == target_lang_text)
        
        # 創建字幕視窗
        if not self.subtitle_window:
            self.subtitle_window = SubtitleWindow(self.subtitle_settings)
            self.subtitle_window.show()
        
        # 創建並啟動處理執行緒
        self.processing_thread = ProcessingThread(url, source_lang, target_lang)
        self.processing_thread.status_update.connect(self.update_status)
        self.processing_thread.subtitle_update.connect(self.update_subtitle)
        self.processing_thread.error_occurred.connect(self.handle_error)
        self.processing_thread.start()
        
        # 更新 UI 狀態
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.url_input.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 無限進度
        
        self.log_message("開始翻譯...")
    
    def pause_translation(self):
        """暫停翻譯"""
        # TODO: 實作暫停功能
        self.log_message("暫停功能尚未實作")
    
    def stop_translation(self):
        """停止翻譯"""
        if self.processing_thread:
            self.processing_thread.stop()
            self.processing_thread.wait()
            self.processing_thread = None
        
        if self.subtitle_window:
            self.subtitle_window.close()
            self.subtitle_window = None
        
        # 更新 UI 狀態
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.url_input.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self.log_message("已停止翻譯")
    
    def update_status(self, message):
        """更新狀態"""
        self.status_bar.showMessage(message)
        self.log_message(message)
    
    def update_subtitle(self, text):
        """更新字幕"""
        if self.subtitle_window:
            self.subtitle_window.update_text(text)
    
    def handle_error(self, error_msg):
        """處理錯誤"""
        self.log_message(f"錯誤: {error_msg}")
        QMessageBox.critical(self, "錯誤", error_msg)
        self.stop_translation()
    
    def log_message(self, message):
        """記錄訊息到日誌區"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def closeEvent(self, event):
        """關閉事件"""
        if self.processing_thread and self.processing_thread.isRunning():
            reply = QMessageBox.question(
                self, '確認', '翻譯正在進行中，確定要退出嗎？',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.stop_translation()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept() 