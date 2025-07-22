# Gemma 3n 模型設定說明

## 概述

您的應用程式現已升級為使用最新的 **Google Gemma 3n-E2B-it** 模型，這是一個專為指令調整的多模態模型，具有以下優勢：

- 🚀 **更好的翻譯品質**：經過改進的指令理解能力
- 💪 **更小的記憶體佔用**：有效 2B 參數，實際佔用更少資源
- ⚡ **更快的推理速度**：最佳化的架構設計
- 🌍 **更廣泛的語言支援**：支援 140+ 種語言

## 自動下載（推薦）

### 方式一：程式自動下載（預設）

當您第一次運行應用程式時，它會**自動下載** Gemma 3n 模型到本地：

1. 確保網路連線正常
2. 運行 `run.bat` 啟動應用程式
3. 程式會自動從 Hugging Face 下載模型（約 3-6 GB）
4. 模型將儲存在 `models/` 資料夾中，之後無需重新下載

**注意**：首次下載可能需要 10-30 分鐘，取決於網路速度。

### 方式二：使用 Hugging Face CLI

如果您希望手動管理模型下載：

```bash
# 安裝 huggingface-hub
pip install huggingface-hub

# 下載模型
huggingface-cli download google/gemma-3n-E2B-it --local-dir models/google/gemma-3n-E2B-it
```

## Hugging Face 授權

### 重要：需要接受 Gemma 使用條款

1. **建立 Hugging Face 帳戶**：
   - 前往 [https://huggingface.co/join](https://huggingface.co/join)
   - 註冊免費帳戶

2. **接受模型授權**：
   - 前往 [https://huggingface.co/google/gemma-3n-E2B-it](https://huggingface.co/google/gemma-3n-E2B-it)
   - 點擊 "Access repository" 
   - 閱讀並同意 Google Gemma 使用條款

3. **設定存取權杖（可選）**：
   - 如果需要私人存取，在 [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 建立存取權杖
   - 在系統環境變數中設定 `HF_TOKEN=your_token_here`

### 如果無法存取模型

如果您遇到存取權限問題，可以暫時使用較舊的模型：

1. 編輯 `src/config.py`
2. 將 `GEMMA_MODEL_NAME = "google/gemma-3n-E2B-it"` 改為 `"google/gemma-2-2b-it"`

## 系統需求更新

### 硬體需求

| 配置 | 記憶體 | 顯存 | 效能 |
|------|--------|------|------|
| 最低配置 | 8GB RAM | 4GB VRAM | 基本翻譯 |
| 推薦配置 | 16GB RAM | 8GB VRAM | 流暢翻譯 |
| 最佳配置 | 32GB RAM | 12GB+ VRAM | 極速翻譯 |

### 軟體更新

程式已自動更新以下依賴：

- `transformers >= 4.53.0` - 支援 Gemma 3n
- `accelerate >= 0.26.0` - 模型加速
- `sentencepiece >= 0.1.99` - 新版分詞器

## 升級步驟

### 1. 更新依賴

```bash
# 升級現有套件
pip install --upgrade -r requirements.txt

# 或強制重裝
pip install --force-reinstall -r requirements.txt
```

### 2. 清理舊模型（可選）

如果您想節省硬碟空間：

```bash
# 刪除舊模型快取
rmdir /s models\google\gemma-2b-it
```

### 3. 重新啟動應用程式

```bash
run.bat
```

## 效能優化

### GPU 使用

Gemma 3n 支援：
- **CUDA**：NVIDIA 顯卡加速
- **4-bit 量化**：減少記憶體使用
- **動態量化**：平衡速度與品質

### CPU 使用

如果沒有 GPU：
- 程式會自動使用 CPU 模式
- 推薦至少 16GB RAM
- 翻譯速度會較慢但仍可正常工作

## 常見問題

### Q: 為什麼首次啟動很慢？
A: 正在下載 Gemma 3n 模型（約 3-6GB），這是一次性過程。

### Q: 下載失敗怎麼辦？
A: 檢查網路連線，或手動使用 `huggingface-cli` 下載。

### Q: 記憶體不足怎麼辦？
A: 在 `src/config.py` 中設定 `GEMMA_QUANTIZATION = "int8"` 或 `"int4"`。

### Q: 翻譯品質變差了？
A: Gemma 3n 通常品質更好，如有問題請檢查是否正確下載完整模型。

### Q: 能否離線使用？
A: 是的，模型下載後即可完全離線使用。

## 疑難排除

### 1. 模型下載錯誤

```python
# 檢查下載狀態
import os
model_path = "models/google/gemma-3n-E2B-it"
if os.path.exists(model_path):
    print("模型已下載")
else:
    print("需要重新下載模型")
```

### 2. 記憶體不足

修改 `src/config.py`：
```python
# 降低量化等級
GEMMA_QUANTIZATION = "int8"  # 或 "int4"

# 減少最大長度
GEMMA_MAX_LENGTH = 256
```

### 3. CUDA 錯誤

```bash
# 檢查 CUDA 安裝
nvidia-smi

# 重裝 PyTorch with CUDA
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 聯絡支援

如果遇到問題：
1. 檢查網路連線
2. 確認 Hugging Face 授權狀態
3. 查看 `app.log` 檔案中的錯誤訊息
4. 嘗試使用較舊的模型版本作為後備方案

---

✅ **設定完成後，您將享受到更快、更準確的即時翻譯體驗！** 