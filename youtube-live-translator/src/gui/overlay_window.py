"""
字幕疊層視窗 - 顯示翻譯字幕
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont, QPalette, QColor, QPainter, QBrush, QPen
import sys

class OverlayWindow(QWidget):
    """透明疊層視窗，用於顯示字幕"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.subtitle_timer = QTimer()
        self.subtitle_timer.timeout.connect(self.clear_subtitle)
        self.fade_animation = None
        
    def init_ui(self):
        # 設定視窗屬性
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |  # 總是在最上層
            Qt.FramelessWindowHint |    # 無邊框
            Qt.Tool |                   # 工具視窗
            Qt.WindowTransparentForInput  # 滑鼠穿透
        )
        
        # 設定視窗透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # 設定視窗大小和位置（全螢幕）
        screen = self.screen()
        if screen:
            self.setGeometry(screen.geometry())
        
        # 創建字幕標籤
        self.subtitle_label = QLabel(self)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        
        # 設定預設樣式
        self.set_default_style()
        
        # 布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 0, 50, 100)  # 左右邊距50px，底部100px
        layout.addStretch()
        layout.addWidget(self.subtitle_label)
        
    def set_default_style(self):
        """設定預設字幕樣式"""
        self.font_size = 24
        self.font_color = QColor(255, 255, 255)
        self.bg_color = QColor(0, 0, 0, 180)
        self.shadow_enabled = True
        self.shadow_strength = 5
        self.apply_style()
        
    def set_style(self, font_size=None, font_color=None, bg_color=None, 
                  shadow_enabled=None, shadow_strength=None):
        """設定字幕樣式"""
        if font_size is not None:
            self.font_size = font_size
        if font_color is not None:
            self.font_color = font_color
        if bg_color is not None:
            self.bg_color = bg_color
        if shadow_enabled is not None:
            self.shadow_enabled = shadow_enabled
        if shadow_strength is not None:
            self.shadow_strength = shadow_strength
            
        self.apply_style()
        
    def apply_style(self):
        """應用樣式到字幕標籤"""
        # 設定字體
        font = QFont("Microsoft YaHei", self.font_size)
        font.setBold(True)
        self.subtitle_label.setFont(font)
        
        # 設定樣式表
        style = f"""
            QLabel {{
                color: rgb({self.font_color.red()}, {self.font_color.green()}, {self.font_color.blue()});
                background-color: rgba({self.bg_color.red()}, {self.bg_color.green()}, 
                                       {self.bg_color.blue()}, {self.bg_color.alpha()});
                padding: 10px 20px;
                border-radius: 10px;
            }}
        """
        self.subtitle_label.setStyleSheet(style)
        
        # 設定陰影效果
        if self.shadow_enabled:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(self.shadow_strength * 2)
            shadow.setColor(QColor(0, 0, 0, 200))
            shadow.setOffset(2, 2)
            self.subtitle_label.setGraphicsEffect(shadow)
        else:
            self.subtitle_label.setGraphicsEffect(None)
            
    def set_position(self, vertical_percent):
        """設定字幕垂直位置（0-100）"""
        screen = self.screen()
        if screen:
            screen_height = screen.geometry().height()
            margin_bottom = int(screen_height * (100 - vertical_percent) / 100)
            
            layout = self.layout()
            layout.setContentsMargins(50, 0, 50, margin_bottom)
            
    def update_subtitle(self, original_text, translated_text):
        """更新字幕內容"""
        # 組合原文和譯文
        subtitle_text = f"{translated_text}\n{original_text}"
        self.subtitle_label.setText(subtitle_text)
        
        # 重置計時器（5秒後自動清除）
        self.subtitle_timer.stop()
        self.subtitle_timer.start(5000)
        
        # 淡入效果
        self.fade_in()
        
    def clear_subtitle(self):
        """清除字幕"""
        self.fade_out()
        
    def fade_in(self):
        """淡入動畫"""
        self.subtitle_label.show()
        if self.fade_animation:
            self.fade_animation.stop()
            
        self.fade_animation = QPropertyAnimation(self.subtitle_label, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
        
    def fade_out(self):
        """淡出動畫"""
        if self.fade_animation:
            self.fade_animation.stop()
            
        self.fade_animation = QPropertyAnimation(self.subtitle_label, b"windowOpacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(lambda: self.subtitle_label.setText(""))
        self.fade_animation.start()
        
    def paintEvent(self, event):
        """繪製事件（用於除錯）"""
        # 如果需要顯示視窗邊界（除錯用）
        if False:  # 改為True以顯示邊界
            painter = QPainter(self)
            painter.setPen(QPen(QColor(255, 0, 0, 50), 2))
            painter.drawRect(self.rect())