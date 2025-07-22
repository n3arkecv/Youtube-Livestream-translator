"""
打包腳本 - 使用 PyInstaller 創建獨立執行檔
"""
import os
import sys
import shutil
from pathlib import Path

def clean_build():
    """清理之前的建構檔案"""
    print("清理舊的建構檔案...")
    dirs_to_remove = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  已刪除 {dir_name}")
    
    # 刪除 .spec 檔案
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"  已刪除 {spec_file}")

def create_icon():
    """創建應用程式圖示"""
    icon_path = Path('assets/icon.ico')
    if not icon_path.exists():
        print("創建預設圖示...")
        icon_path.parent.mkdir(exist_ok=True)
        
        # 創建一個簡單的圖示 (實際上應該使用真正的圖示檔案)
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 創建圖片
            size = 256
            img = Image.new('RGBA', (size, size), (0, 162, 232, 255))
            draw = ImageDraw.Draw(img)
            
            # 繪製文字
            text = "YT"
            try:
                font = ImageFont.truetype("arial.ttf", 100)
            except:
                font = ImageFont.load_default()
            
            # 計算文字位置
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            draw.text((x, y), text, fill='white', font=font)
            
            # 儲存為 ICO
            img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"  圖示已創建: {icon_path}")
        except ImportError:
            print("  警告: 需要 Pillow 來創建圖示")
            return None
    
    return str(icon_path) if icon_path.exists() else None

def create_spec_file():
    """創建 PyInstaller spec 檔案"""
    print("創建 spec 檔案...")
    
    icon_path = create_icon()
    
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'yt_dlp',
        'pydub',
        'whisper',
        'transformers',
        'torch',
        'torchaudio',
        'sounddevice',
        'screeninfo',
        'webrtcvad',
        'ffmpeg',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'notebook',
        'ipython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YouTubeTranslator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不顯示控制台視窗
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {f'icon="{icon_path}",' if icon_path else ''}
    version='version_info.txt'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YouTubeTranslator',
)
"""
    
    with open('YouTubeTranslator.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("  spec 檔案已創建")

def create_version_info():
    """創建版本資訊檔案"""
    print("創建版本資訊...")
    
    version_info = """VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'YouTube Translator'),
        StringStruct(u'FileDescription', u'YouTube 直播即時翻譯器'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'YouTubeTranslator'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2024'),
        StringStruct(u'OriginalFilename', u'YouTubeTranslator.exe'),
        StringStruct(u'ProductName', u'YouTube 直播即時翻譯器'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print("  版本資訊已創建")

def build_exe():
    """執行打包"""
    print("\n開始打包...")
    
    # 確保在虛擬環境中
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("警告: 不在虛擬環境中，建議在虛擬環境中執行打包")
    
    # 執行 PyInstaller
    cmd = 'pyinstaller YouTubeTranslator.spec --clean'
    print(f"執行: {cmd}")
    
    result = os.system(cmd)
    
    if result == 0:
        print("\n打包成功！")
        print(f"執行檔位置: dist/YouTubeTranslator/YouTubeTranslator.exe")
        
        # 創建額外的檔案
        create_additional_files()
    else:
        print("\n打包失敗！")
        return False
    
    return True

def create_additional_files():
    """創建額外的檔案"""
    dist_dir = Path('dist/YouTubeTranslator')
    
    # 創建 README
    readme_content = """YouTube 直播即時翻譯器
====================

使用說明：
1. 執行 YouTubeTranslator.exe
2. 輸入 YouTube 直播網址
3. 選擇語言設定
4. 點擊「開始翻譯」

系統需求：
- Windows 10 或更高版本
- 需要網路連線
- 建議 8GB 以上記憶體

注意事項：
- 首次執行會下載必要的模型檔案
- 請確保已安裝 FFmpeg

如遇到問題，請查看 app.log 檔案
"""
    
    with open(dist_dir / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # 創建批次啟動檔
    batch_content = """@echo off
title YouTube 直播即時翻譯器
YouTubeTranslator.exe
if %errorlevel% neq 0 (
    echo.
    echo 程式發生錯誤，請查看 app.log
    pause
)
"""
    
    with open(dist_dir / '啟動翻譯器.bat', 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print("\n額外檔案已創建")

def create_installer():
    """創建安裝程式（使用 NSIS 或類似工具）"""
    print("\n創建安裝程式...")
    
    # 這裡可以整合 NSIS 或其他安裝程式製作工具
    # 目前只創建一個簡單的 zip 檔案
    
    try:
        import zipfile
        
        dist_dir = Path('dist/YouTubeTranslator')
        zip_path = Path('dist/YouTubeTranslator-v1.0.0-windows.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in dist_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(dist_dir.parent)
                    zipf.write(file_path, arcname)
        
        print(f"  安裝包已創建: {zip_path}")
        print(f"  大小: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")
        
    except ImportError:
        print("  跳過 ZIP 創建")

def main():
    """主函數"""
    print("========================================")
    print("  YouTube 直播即時翻譯器 - 打包程式")
    print("========================================")
    
    # 清理
    clean_build()
    
    # 創建必要檔案
    create_version_info()
    create_spec_file()
    
    # 執行打包
    if build_exe():
        create_installer()
        
        print("\n========================================")
        print("打包完成！")
        print("========================================")
        print("\n輸出檔案:")
        print("  - dist/YouTubeTranslator/YouTubeTranslator.exe")
        print("  - dist/YouTubeTranslator/啟動翻譯器.bat")
        print("  - dist/YouTubeTranslator-v1.0.0-windows.zip")
        print("\n您可以將 dist/YouTubeTranslator 資料夾分發給使用者")
    else:
        print("\n打包失敗，請檢查錯誤訊息")

if __name__ == "__main__":
    main()
    input("\n按 Enter 鍵結束...") 