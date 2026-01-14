# 安装

Magneto 提供了多种安装方式，您可以根据自己的需求选择最适合的方法。

## 从 PyPI 安装（推荐）

最简单的方式是使用 pip 从 PyPI 安装：

```bash
pip install magneto-cli
```

或使用 uv：

```bash
uv pip install magneto-cli
```

安装完成后，您可以直接使用 `magneto` 命令：

```bash
magneto --help
```

## 从源码安装

如果您想从源码安装用于开发：

### 使用 pip

```bash
# 克隆仓库
git clone https://github.com/mastaBriX/magneto.git
cd magneto

# 安装项目（开发模式）
pip install -e .
```

### 使用 uv

`uv` 是一个快速的 Python 包管理器，完全兼容 `pyproject.toml`。

#### 1. 安装 uv

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. 同步依赖

在项目根目录下运行：

```bash
# 克隆仓库
git clone https://github.com/mastaBriX/magneto.git
cd magneto

# 同步依赖并安装项目（开发模式）
uv sync

# 直接运行（无需安装，uv 会自动管理环境）
uv run magneto file.torrent
uv run magneto folder/ -r -v

# 安装开发依赖
uv sync --extra dev

# 查看项目信息
uv tree
```

## 验证安装

安装完成后，可以通过以下命令验证：

```bash
# 查看版本
magneto --version

# 查看帮助
magneto --help
```

如果看到版本信息和帮助文档，说明安装成功！

## 依赖说明

### 必需依赖

- **bencode.py >= 4.0.0**: 用于解析种子文件格式
- **colorama >= 0.4.0**: 用于 Windows 系统的彩色输出支持（可选，但推荐）

### Python 版本要求

- Python 3.7 或更高版本
- 支持 Python 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13

## 开发环境设置

如果您想参与开发或运行测试：

```bash
# 使用 uv
uv sync --extra dev

# 或使用 pip
pip install -e ".[dev]"
```

开发依赖包括：
- `pytest >= 7.0.0` - 测试框架
- `pytest-cov >= 4.0.0` - 测试覆盖率
- `black >= 23.0.0` - 代码格式化
- `ruff >= 0.1.0` - 代码检查

## 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=magneto --cov-report=html

# 运行特定测试文件
pytest tests/test_core.py

# 详细模式
pytest -v
```

## 故障排除

### 问题：找不到 magneto 命令

**解决方案：**
- 确保已正确安装：`pip install -e .`
- 检查 Python 环境：确保使用的 Python 版本正确
- 检查 PATH 环境变量：确保 Python 的 Scripts 目录在 PATH 中

### 问题：导入错误（bencode 模块未找到）

**解决方案：**
```bash
pip install bencode.py
```

### 问题：Windows 上颜色不显示

**解决方案：**
```bash
pip install colorama
```

### 问题：权限错误

**解决方案：**
- Linux/macOS: 使用 `sudo` 或虚拟环境
- Windows: 以管理员身份运行，或使用虚拟环境

## 下一步

安装完成后，您可以：

- [快速开始](/zh/getting-started) - 学习基本使用方法
- [使用指南](/zh/usage) - 了解所有功能特性

