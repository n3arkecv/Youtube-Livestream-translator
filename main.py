"""
YouTube 直播即時翻譯器 - 主程式
"""
import sys
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QIcon

# 設定模組路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.main_window import MainWindow
from src.config import APP_NAME, LOG_LEVEL, LOG_FILE, ASSETS_DIR

# 設定日誌
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def setup_app():
    """設定應用程式屬性"""
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("YouTube Translator")
    
    # 設定應用程式圖示（如果存在）
    icon_path = ASSETS_DIR / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # 設定全域樣式
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QPushButton {
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        QLineEdit, QComboBox {
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
        }
        QLabel {
            font-size: 14px;
        }
    """)
    
    return app


def main():
    """主程式入口"""
    try:
        logger.info(f"啟動 {APP_NAME}...")
        
        # 創建應用程式
        app = setup_app()
        
        # 創建主視窗
        window = MainWindow()
        window.show()
        
        # 執行應用程式
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"應用程式發生錯誤: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 