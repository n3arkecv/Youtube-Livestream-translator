"""
測試應用程式基本功能
"""
import sys
import os
from pathlib import Path

# 設定模組路徑
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """測試模組導入"""
    print("測試模組導入...")
    try:
        from src.config import APP_NAME, APP_VERSION
        print(f"✓ 設定模組: {APP_NAME} v{APP_VERSION}")
        
        from src.gui.main_window import MainWindow
        print("✓ GUI 主視窗模組")
        
        from src.gui.subtitle_window import SubtitleWindow
        print("✓ 字幕視窗模組")
        
        from src.core.youtube_handler import YouTubeHandler
        print("✓ YouTube 處理模組")
        
        from src.core.transcriber import Transcriber
        print("✓ 語音轉文字模組")
        
        from src.core.translator import Translator
        print("✓ 翻譯模組")
        
        return True
    except ImportError as e:
        print(f"✗ 導入錯誤: {e}")
        return False

def test_gui():
    """測試 GUI 啟動"""
    print("\n測試 GUI...")
    try:
        from PyQt5.QtWidgets import QApplication
        from src.gui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        window = MainWindow()
        
        print("✓ GUI 創建成功")
        print("  - 視窗標題:", window.windowTitle())
        print("  - 視窗大小:", window.size())
        
        # 不實際顯示視窗，只測試創建
        return True
    except Exception as e:
        print(f"✗ GUI 測試失敗: {e}")
        return False

def test_dependencies():
    """測試依賴項"""
    print("\n測試依賴項...")
    
    dependencies = {
        "PyQt5": "PyQt5.QtCore",
        "yt-dlp": "yt_dlp",
        "pydub": "pydub",
        "numpy": "numpy",
        "torch": "torch",
        "whisper": "whisper",
        "transformers": "transformers",
    }
    
    all_ok = True
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - 未安裝")
            all_ok = False
    
    return all_ok

def test_ffmpeg():
    """測試 FFmpeg"""
    print("\n測試 FFmpeg...")
    import subprocess
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print("✓ FFmpeg 已安裝")
            # 獲取版本資訊
            version_line = result.stdout.split('\n')[0]
            print(f"  版本: {version_line}")
            return True
        else:
            print("✗ FFmpeg 執行失敗")
            return False
    except FileNotFoundError:
        print("✗ FFmpeg 未安裝或不在 PATH 中")
        return False

def main():
    """主測試函數"""
    print("========================================")
    print("  YouTube 直播即時翻譯器 - 功能測試")
    print("========================================")
    
    tests = [
        ("模組導入", test_imports),
        ("依賴項", test_dependencies),
        ("FFmpeg", test_ffmpeg),
        ("GUI", test_gui),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n測試 {test_name} 時發生錯誤: {e}")
            results.append((test_name, False))
    
    # 總結
    print("\n========================================")
    print("測試總結:")
    print("========================================")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "通過" if result else "失敗"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    print(f"\n總計: {passed}/{total} 測試通過")
    
    if passed == total:
        print("\n所有測試通過！應用程式已準備就緒。")
    else:
        print("\n部分測試失敗，請檢查上述錯誤訊息。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    input("\n按 Enter 鍵結束...")
    sys.exit(0 if success else 1) 