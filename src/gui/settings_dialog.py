"""
進階設定對話框
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QSlider, QSpinBox, QDoubleSpinBox,
    QPushButton, QColorDialog, QFontComboBox,
    QDialogButtonBox, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class SettingsDialog(QDialog):
    """進階設定對話框"""
    
    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.settings = current_settings.copy()
        self.init_ui()
        
    def init_ui(self):
        """初始化介面"""
        self.setWindowTitle("進階字幕設定")
        self.setModal(True)
        self.resize(500, 600)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 字體設定群組
        font_group = QGroupBox("字體設定")
        font_layout = QGridLayout(font_group)
        
        # 字體選擇
        font_layout.addWidget(QLabel("字體:"), 0, 0)
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont(self.settings.get("font_family", "Microsoft YaHei")))
        font_layout.addWidget(self.font_combo, 0, 1)
        
        # 字體大小
        font_layout.addWidget(QLabel("大小:"), 1, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(12, 72)
        self.font_size_spin.setValue(self.settings.get("font_size", 24))
        self.font_size_spin.setSuffix(" px")
        font_layout.addWidget(self.font_size_spin, 1, 1)
        
        main_layout.addWidget(font_group)
        
        # 顏色設定群組
        color_group = QGroupBox("顏色設定")
        color_layout = QGridLayout(color_group)
        
        # 字體顏色
        color_layout.addWidget(QLabel("字體顏色:"), 0, 0)
        self.font_color_btn = QPushButton()
        self.font_color_btn.setStyleSheet(
            f"background-color: {self.settings.get('font_color', '#FFFFFF')}; "
            "border: 1px solid #000; min-height: 30px;"
        )
        self.font_color_btn.clicked.connect(self.choose_font_color)
        color_layout.addWidget(self.font_color_btn, 0, 1)
        
        # 背景顏色
        color_layout.addWidget(QLabel("背景顏色:"), 1, 0)
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setStyleSheet(
            f"background-color: {self.settings.get('background_color', '#000000')}; "
            "border: 1px solid #000; min-height: 30px;"
        )
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        color_layout.addWidget(self.bg_color_btn, 1, 1)
        
        # 背景透明度
        color_layout.addWidget(QLabel("背景透明度:"), 2, 0)
        self.bg_opacity_slider = QSlider(Qt.Horizontal)
        self.bg_opacity_slider.setRange(0, 100)
        self.bg_opacity_slider.setValue(int(self.settings.get("background_opacity", 0.7) * 100))
        self.bg_opacity_slider.valueChanged.connect(self.update_opacity_label)
        color_layout.addWidget(self.bg_opacity_slider, 2, 1)
        
        self.opacity_label = QLabel(f"{self.bg_opacity_slider.value()}%")
        color_layout.addWidget(self.opacity_label, 2, 2)
        
        main_layout.addWidget(color_group)
        
        # 陰影設定群組
        shadow_group = QGroupBox("陰影設定")
        shadow_layout = QGridLayout(shadow_group)
        
        # 陰影顏色
        shadow_layout.addWidget(QLabel("陰影顏色:"), 0, 0)
        self.shadow_color_btn = QPushButton()
        self.shadow_color_btn.setStyleSheet(
            f"background-color: {self.settings.get('shadow_color', '#000000')}; "
            "border: 1px solid #000; min-height: 30px;"
        )
        self.shadow_color_btn.clicked.connect(self.choose_shadow_color)
        shadow_layout.addWidget(self.shadow_color_btn, 0, 1)
        
        # 陰影偏移
        shadow_layout.addWidget(QLabel("陰影偏移:"), 1, 0)
        self.shadow_offset_spin = QSpinBox()
        self.shadow_offset_spin.setRange(0, 10)
        self.shadow_offset_spin.setValue(self.settings.get("shadow_offset", 2))
        self.shadow_offset_spin.setSuffix(" px")
        shadow_layout.addWidget(self.shadow_offset_spin, 1, 1)
        
        main_layout.addWidget(shadow_group)
        
        # 位置設定群組
        position_group = QGroupBox("位置設定")
        position_layout = QGridLayout(position_group)
        
        # 水平位置
        position_layout.addWidget(QLabel("水平位置:"), 0, 0)
        self.pos_x_slider = QSlider(Qt.Horizontal)
        self.pos_x_slider.setRange(0, 100)
        self.pos_x_slider.setValue(int(self.settings.get("position_x", 0.5) * 100))
        self.pos_x_slider.valueChanged.connect(self.update_pos_x_label)
        position_layout.addWidget(self.pos_x_slider, 0, 1)
        
        self.pos_x_label = QLabel(f"{self.pos_x_slider.value()}%")
        position_layout.addWidget(self.pos_x_label, 0, 2)
        
        # 垂直位置
        position_layout.addWidget(QLabel("垂直位置:"), 1, 0)
        self.pos_y_slider = QSlider(Qt.Horizontal)
        self.pos_y_slider.setRange(0, 100)
        self.pos_y_slider.setValue(int(self.settings.get("position_y", 0.8) * 100))
        self.pos_y_slider.valueChanged.connect(self.update_pos_y_label)
        position_layout.addWidget(self.pos_y_slider, 1, 1)
        
        self.pos_y_label = QLabel(f"{self.pos_y_slider.value()}%")
        position_layout.addWidget(self.pos_y_label, 1, 2)
        
        # 最大寬度
        position_layout.addWidget(QLabel("最大寬度:"), 2, 0)
        self.max_width_slider = QSlider(Qt.Horizontal)
        self.max_width_slider.setRange(20, 100)
        self.max_width_slider.setValue(int(self.settings.get("max_width", 0.8) * 100))
        self.max_width_slider.valueChanged.connect(self.update_max_width_label)
        position_layout.addWidget(self.max_width_slider, 2, 1)
        
        self.max_width_label = QLabel(f"{self.max_width_slider.value()}%")
        position_layout.addWidget(self.max_width_label, 2, 2)
        
        main_layout.addWidget(position_group)
        
        # 按鈕
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        # 恢復預設值按鈕
        restore_btn = buttons.button(QDialogButtonBox.RestoreDefaults)
        restore_btn.setText("恢復預設值")
        restore_btn.clicked.connect(self.restore_defaults)
        
        main_layout.addWidget(buttons)
    
    def choose_font_color(self):
        """選擇字體顏色"""
        color = QColorDialog.getColor(Qt.white, self, "選擇字體顏色")
        if color.isValid():
            self.settings["font_color"] = color.name()
            self.font_color_btn.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #000; min-height: 30px;"
            )
    
    def choose_bg_color(self):
        """選擇背景顏色"""
        color = QColorDialog.getColor(Qt.black, self, "選擇背景顏色")
        if color.isValid():
            self.settings["background_color"] = color.name()
            self.bg_color_btn.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #000; min-height: 30px;"
            )
    
    def choose_shadow_color(self):
        """選擇陰影顏色"""
        color = QColorDialog.getColor(Qt.black, self, "選擇陰影顏色")
        if color.isValid():
            self.settings["shadow_color"] = color.name()
            self.shadow_color_btn.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #000; min-height: 30px;"
            )
    
    def update_opacity_label(self, value):
        """更新透明度標籤"""
        self.opacity_label.setText(f"{value}%")
    
    def update_pos_x_label(self, value):
        """更新水平位置標籤"""
        self.pos_x_label.setText(f"{value}%")
    
    def update_pos_y_label(self, value):
        """更新垂直位置標籤"""
        self.pos_y_label.setText(f"{value}%")
    
    def update_max_width_label(self, value):
        """更新最大寬度標籤"""
        self.max_width_label.setText(f"{value}%")
    
    def restore_defaults(self):
        """恢復預設值"""
        from ..config import DEFAULT_SUBTITLE_SETTINGS
        
        # 更新所有控件為預設值
        self.font_combo.setCurrentFont(QFont(DEFAULT_SUBTITLE_SETTINGS["font_family"]))
        self.font_size_spin.setValue(DEFAULT_SUBTITLE_SETTINGS["font_size"])
        
        self.font_color_btn.setStyleSheet(
            f"background-color: {DEFAULT_SUBTITLE_SETTINGS['font_color']}; "
            "border: 1px solid #000; min-height: 30px;"
        )
        self.bg_color_btn.setStyleSheet(
            f"background-color: {DEFAULT_SUBTITLE_SETTINGS['background_color']}; "
            "border: 1px solid #000; min-height: 30px;"
        )
        self.shadow_color_btn.setStyleSheet(
            f"background-color: {DEFAULT_SUBTITLE_SETTINGS['shadow_color']}; "
            "border: 1px solid #000; min-height: 30px;"
        )
        
        self.bg_opacity_slider.setValue(int(DEFAULT_SUBTITLE_SETTINGS["background_opacity"] * 100))
        self.shadow_offset_spin.setValue(DEFAULT_SUBTITLE_SETTINGS["shadow_offset"])
        
        self.pos_x_slider.setValue(int(DEFAULT_SUBTITLE_SETTINGS["position_x"] * 100))
        self.pos_y_slider.setValue(int(DEFAULT_SUBTITLE_SETTINGS["position_y"] * 100))
        self.max_width_slider.setValue(int(DEFAULT_SUBTITLE_SETTINGS["max_width"] * 100))
        
        # 更新設定字典
        self.settings = DEFAULT_SUBTITLE_SETTINGS.copy()
    
    def get_settings(self):
        """獲取設定"""
        # 更新設定值
        self.settings["font_family"] = self.font_combo.currentFont().family()
        self.settings["font_size"] = self.font_size_spin.value()
        self.settings["background_opacity"] = self.bg_opacity_slider.value() / 100.0
        self.settings["shadow_offset"] = self.shadow_offset_spin.value()
        self.settings["position_x"] = self.pos_x_slider.value() / 100.0
        self.settings["position_y"] = self.pos_y_slider.value() / 100.0
        self.settings["max_width"] = self.max_width_slider.value() / 100.0
        
        return self.settings 