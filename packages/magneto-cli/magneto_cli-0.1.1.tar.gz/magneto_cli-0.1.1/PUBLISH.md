# 发布到 PyPI 指南

本指南说明如何使用 `uv` 将项目发布到 PyPI。

## 前置准备

### 1. 注册 PyPI 账号

- 访问 https://pypi.org/account/register/ 注册账号
- 如果已有账号，直接登录

### 2. 创建 API Token

1. 登录 PyPI 后，访问：https://pypi.org/manage/account/token/
2. 点击 "Add API token"
3. 输入 Token 名称（例如：`magneto-publish`）
4. 选择作用域：
   - **Entire account**：适用于所有项目（推荐用于个人项目）
   - **Project specific**：仅限特定项目
5. 点击 "Add token"
6. **重要**：复制生成的 token（格式类似 `pypi-...`），它只会显示一次！

### 3. 检查项目配置

确保 `pyproject.toml` 中的以下信息正确：
- `name`：包名（必须是唯一的，如果已被占用需要改名）
- `version`：版本号
- `description`：项目描述
- `authors`：作者信息
- `license`：许可证
- `readme`：README 文件路径

## 发布步骤

### 方法一：使用环境变量（推荐）

```powershell
# Windows PowerShell
$env:UV_PUBLISH_TOKEN = "pypi-你的token"
uv publish

# 或者一次性设置并发布
$env:UV_PUBLISH_TOKEN = "pypi-你的token"; uv publish
```

```bash
# Linux/Mac
export UV_PUBLISH_TOKEN="pypi-你的token"
uv publish
```

### 方法二：使用命令行参数

```powershell
# Windows PowerShell
uv publish --token "pypi-你的token"
```

```bash
# Linux/Mac
uv publish --token "pypi-你的token"
```

### 方法三：使用用户名和密码（不推荐，已弃用）

```powershell
uv publish --username "你的用户名" --password "你的密码"
```

## 发布流程

### 1. 构建分发包

```powershell
uv build
```

这会生成以下文件到 `dist/` 目录：
- `magneto_cli-0.1.0.tar.gz`（源码分发包）
- `magneto_cli-0.1.0-py3-none-any.whl`（wheel 分发包）

### 2. 检查构建产物（可选）

```powershell
# 查看生成的文件
ls dist/

# 测试安装（可选）
pip install dist/magneto_cli-0.1.0-py3-none-any.whl
```

### 3. 发布到 PyPI

```powershell
# 使用 token（推荐）
$env:UV_PUBLISH_TOKEN = "pypi-你的token"
uv publish
```

### 4. 验证发布

发布成功后，访问：https://pypi.org/project/magneto-cli/

安装测试：
```bash
pip install magneto-cli
```

**注意**：安装后命令行工具名称仍然是 `magneto`，因为包名和命令名可以不同。

## 发布到 TestPyPI（测试发布）

在正式发布前，建议先发布到 TestPyPI 进行测试：

### 1. 注册 TestPyPI 账号

访问 https://test.pypi.org/account/register/ 注册（可以与 PyPI 使用相同用户名）

### 2. 创建 TestPyPI Token

访问 https://test.pypi.org/manage/account/token/ 创建 token

### 3. 发布到 TestPyPI

```powershell
# 指定 TestPyPI 的上传 URL
$env:UV_PUBLISH_TOKEN = "pypi-你的testpypi-token"
uv publish --publish-url "https://test.pypi.org/legacy/"
```

### 4. 从 TestPyPI 安装测试

```bash
pip install -i https://test.pypi.org/simple/ magneto-cli
```

## 更新版本

每次发布新版本时：

1. **更新版本号**：
   - 在 `pyproject.toml` 中更新 `version`
   - 在 `magneto/__init__.py` 中更新 `__version__`

2. **构建并发布**：
   ```powershell
   uv build
   $env:UV_PUBLISH_TOKEN = "pypi-你的token"
   uv publish
   ```

## 常见问题

### 1. 包名已被占用

**注意**：原包名 `magneto` 在 PyPI 上已被占用，已改为 `magneto-cli`。

如果包名被占用，需要：
- 在 `pyproject.toml` 中修改 `name` 字段
- 确保新名称在 PyPI 上可用
- 重新构建分发包（`uv build`）

### 2. 版本号已存在

如果该版本已发布，需要：
- 更新 `version` 号（遵循语义化版本：主版本号.次版本号.修订号）
- 重新构建和发布

### 3. 发布失败

检查：
- Token 是否正确
- 网络连接是否正常
- 包名和版本号是否唯一
- `pyproject.toml` 配置是否正确

### 4. 使用 dry-run 测试

在正式发布前，可以使用 `--dry-run` 测试：

```powershell
uv publish --token "pypi-你的token" --dry-run
```

## 安全建议

1. **不要将 token 提交到 Git**：确保 `.gitignore` 包含环境变量文件
2. **使用项目级 token**：如果可能，使用项目特定的 token 而不是账户级 token
3. **定期轮换 token**：定期更新 API token
4. **使用环境变量**：优先使用环境变量而不是命令行参数，避免 token 出现在命令历史中

## 参考链接

- [PyPI 官方文档](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/)
- [uv 文档](https://docs.astral.sh/uv/)
- [TestPyPI](https://test.pypi.org/)
