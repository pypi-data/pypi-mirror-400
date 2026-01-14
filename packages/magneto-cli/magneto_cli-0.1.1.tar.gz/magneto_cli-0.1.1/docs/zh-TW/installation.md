# 安裝

Magneto 提供了多種安裝方式，您可以根據自己的需求選擇最適合的方法。

## 從 PyPI 安裝（推薦）

最簡單的方式是使用 pip 從 PyPI 安裝：

```bash
pip install magneto-cli
```

或使用 uv：

```bash
uv pip install magneto-cli
```

安裝完成後，您可以直接使用 `magneto` 命令：

```bash
magneto --help
```

## 從原始碼安裝

如果您想從原始碼安裝用於開發：

### 使用 pip

```bash
# 複製儲存庫
git clone https://github.com/mastaBriX/magneto.git
cd magneto

# 安裝專案（開發模式）
pip install -e .
```

### 使用 uv

`uv` 是一個快速的 Python 套件管理器，完全相容於 `pyproject.toml`。

#### 1. 安裝 uv

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. 同步依賴

在專案根目錄下執行：

```bash
# 複製儲存庫
git clone https://github.com/mastaBriX/magneto.git
cd magneto

# 同步依賴並安裝專案（開發模式）
uv sync

# 直接執行（無需安裝，uv 會自動管理環境）
uv run magneto file.torrent
uv run magneto folder/ -r -v

# 安裝開發依賴
uv sync --extra dev

# 查看專案資訊
uv tree
```

## 驗證安裝

安裝完成後，可以透過以下命令驗證：

```bash
# 查看版本
magneto --version

# 查看說明
magneto --help
```

如果看到版本資訊和說明文件，說明安裝成功！

## 依賴說明

### 必需依賴

- **bencode.py >= 4.0.0**: 用於解析種子檔案格式
- **colorama >= 0.4.0**: 用於 Windows 系統的彩色輸出支援（可選，但推薦）

### Python 版本要求

- Python 3.7 或更高版本
- 支援 Python 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13

## 開發環境設定

如果您想參與開發或執行測試：

```bash
# 使用 uv
uv sync --extra dev

# 或使用 pip
pip install -e ".[dev]"
```

開發依賴包括：
- `pytest >= 7.0.0` - 測試框架
- `pytest-cov >= 4.0.0` - 測試覆蓋率
- `black >= 23.0.0` - 程式碼格式化
- `ruff >= 0.1.0` - 程式碼檢查

## 執行測試

```bash
# 執行所有測試
pytest

# 執行測試並產生覆蓋率報告
pytest --cov=magneto --cov-report=html

# 執行特定測試檔案
pytest tests/test_core.py

# 詳細模式
pytest -v
```

## 故障排除

### 問題：找不到 magneto 命令

**解決方案：**
- 確保已正確安裝：`pip install -e .`
- 檢查 Python 環境：確保使用的 Python 版本正確
- 檢查 PATH 環境變數：確保 Python 的 Scripts 目錄在 PATH 中

### 問題：匯入錯誤（bencode 模組未找到）

**解決方案：**
```bash
pip install bencode.py
```

### 問題：Windows 上顏色不顯示

**解決方案：**
```bash
pip install colorama
```

### 問題：權限錯誤

**解決方案：**
- Linux/macOS: 使用 `sudo` 或虛擬環境
- Windows: 以管理員身份執行，或使用虛擬環境

## 下一步

安裝完成後，您可以：

- [快速開始](/zh-TW/getting-started) - 學習基本使用方法
- [使用指南](/zh-TW/usage) - 了解所有功能特性
