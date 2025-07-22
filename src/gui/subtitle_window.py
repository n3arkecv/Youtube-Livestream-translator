"""
字幕顯示視窗 - 透明疊層視窗
"""
import logging
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, pyqtSignal
from PyQt5.QtGui import QPalette, QColor, QFont, QPainter, QPainterPath

logger = logging.getLogger(__name__)


class SubtitleLabel(QLabel):
    """自訂字幕標籤，支援陰影效果"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shadow_enabled = True
        self.shadow_color = QColor(0, 0, 0)
        self.shadow_offset = 2
        
    def set_shadow(self, enabled, color=None, offset=2):
        """設定陰影"""
        self.shadow_enabled = enabled
        if color:
            self.shadow_color = QColor(color)
        self.shadow_offset = offset
        self.update()
    
    def paintEvent(self, event):
        """繪製事件"""
        if not self.text() or not self.shadow_enabled:
            super().paintEvent(event)
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 繪製陰影
        painter.setPen(self.shadow_color)
        painter.setFont(self.font())
        shadow_rect = self.rect()
        shadow_rect.translate(self.shadow_offset, self.shadow_offset)
        painter.drawText(shadow_rect, self.alignment(), self.text())
        
        # 繪製文字
        painter.setPen(self.palette().color(QPalette.WindowText))
        painter.drawText(self.rect(), self.alignment(), self.text())


class SubtitleWindow(QWidget):
    """字幕顯示視窗"""
    
    closed = pyqtSignal()
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings.copy()
        self.is_dragging = False
        self.drag_position = None
        self.fade_timer = QTimer()
        self.fade_timer.timeout.connect(self.start_fade_out)
        
        self.init_ui()
        self.apply_settings()
    
    def init_ui(self):
        """初始化介面"""
        # 設定視窗屬性
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # 無邊框
            Qt.WindowStaysOnTopHint |  # 保持在最上層
            Qt.Tool |  # 工具視窗
            Qt.WindowTransparentForInput  # 初始設定為滑鼠穿透
        )
        
        # 設定透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # 布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 字幕標籤
        self.subtitle_label = SubtitleLabel()
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
        """)
        
        layout.addWidget(self.subtitle_label)
        
        # 設定初始大小和位置
        self.resize(800, 100)
        self.center_on_screen()
    
    def apply_settings(self):
        """套用設定"""
        # 字體設定
        font = QFont(self.settings.get("font_family", "Microsoft YaHei"))
        font.setPointSize(self.settings.get("font_size", 24))
        self.subtitle_label.setFont(font)
        
        # 顏色設定
        font_color = self.settings.get("font_color", "#FFFFFF")
        bg_color = self.settings.get("background_color", "#000000")
        bg_opacity = int(self.settings.get("background_opacity", 0.7) * 255)
        
        # 解析背景顏色
        bg_qcolor = QColor(bg_color)
        bg_rgba = f"rgba({bg_qcolor.red()}, {bg_qcolor.green()}, {bg_qcolor.blue()}, {bg_opacity})"
        
        self.subtitle_label.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_rgba};
                color: {font_color};
                padding: 10px 20px;
                border-radius: 5px;
            }}
        """)
        
        # 陰影設定
        if self.settings.get("shadow_enabled", True):
            shadow_color = self.settings.get("shadow_color", "#000000")
            shadow_offset = self.settings.get("shadow_offset", 2)
            self.subtitle_label.set_shadow(True, shadow_color, shadow_offset)
        else:
            self.subtitle_label.set_shadow(False)
        
        # 位置設定
        self.update_position()
        
        # 最大寬度設定
        screen_geometry = self.screen().geometry()
        max_width = int(screen_geometry.width() * self.settings.get("max_width", 0.8))
        self.setMaximumWidth(max_width)
    
    def center_on_screen(self):
        """將視窗置中於螢幕"""
        screen_geometry = self.screen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = int(screen_geometry.height() * 0.8)  # 預設在螢幕下方
        self.move(x, y)
    
    def update_position(self):
        """根據設定更新位置"""
        screen_geometry = self.screen().geometry()
        
        # 相對位置 (0-1)
        rel_x = self.settings.get("position_x", 0.5)
        rel_y = self.settings.get("position_y", 0.8)
        
        # 計算實際位置
        x = int((screen_geometry.width() - self.width()) * rel_x)
        y = int(screen_geometry.height() * rel_y)
        
        self.move(x, y)
    
    def update_text(self, text):
        """更新字幕文字"""
        self.subtitle_label.setText(text)
        
        # 調整視窗大小以適應文字
        self.adjustSize()
        
        # 確保不超過最大寬度
        if self.width() > self.maximumWidth():
            self.resize(self.maximumWidth(), self.height())
        
        # 重新定位（保持中心點不變）
        self.update_position()
        
        # 顯示視窗
        self.show()
        self.raise_()
        
        # 重置淡出計時器
        self.fade_timer.stop()
        self.setWindowOpacity(1.0)
        
        # 設定淡出延遲（例如 5 秒後開始淡出）
        self.fade_timer.start(5000)
    
    def start_fade_out(self):
        """開始淡出動畫"""
        self.fade_timer.stop()
        
        # 創建淡出動畫
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(1000)  # 1 秒淡出
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
    
    def update_settings(self, settings):
        """更新設定"""
        self.settings = settings.copy()
        self.apply_settings()
    
    def mousePressEvent(self, event):
        """滑鼠按下事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            
            # 暫時取消滑鼠穿透，允許拖曳
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowTransparentForInput
            )
            self.show()  # 重新顯示以應用新的視窗標誌
            
            event.accept()
    
    def mouseMoveEvent(self, event):
        """滑鼠移動事件"""
        if event.buttons() == Qt.LeftButton and self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
            
            # 更新相對位置設定
            screen_geometry = self.screen().geometry()
            self.settings["position_x"] = self.x() / (screen_geometry.width() - self.width())
            self.settings["position_y"] = self.y() / screen_geometry.height()
            
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """滑鼠釋放事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            
            # 恢復滑鼠穿透
            self.setWindowFlags(
                self.windowFlags() | Qt.WindowTransparentForInput
            )
            self.show()  # 重新顯示以應用新的視窗標誌
            
            event.accept()
    
    def enterEvent(self, event):
        """滑鼠進入事件"""
        # 滑鼠懸停時暫時取消穿透
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowTransparentForInput
        )
        self.show()
        
        # 停止淡出
        self.fade_timer.stop()
        self.setWindowOpacity(1.0)
    
    def leaveEvent(self, event):
        """滑鼠離開事件"""
        # 恢復滑鼠穿透
        if not self.is_dragging:
            self.setWindowFlags(
                self.windowFlags() | Qt.WindowTransparentForInput
            )
            self.show()
        
        # 重新開始淡出計時
        if self.subtitle_label.text():
            self.fade_timer.start(5000)
    
    def closeEvent(self, event):
        """關閉事件"""
        self.closed.emit()
        event.accept() 