# インストール

Magneto は複数のインストール方法を提供しています。ニーズに最適な方法を選択できます。

## PyPI からインストール（推奨）

最も簡単な方法は、pip を使用して PyPI からインストールすることです：

```bash
pip install magneto-cli
```

または uv を使用：

```bash
uv pip install magneto-cli
```

インストール後、`magneto` コマンドを直接使用できます：

```bash
magneto --help
```

## ソースからインストール

開発のためにソースからインストールする場合：

### pip を使用

```bash
# リポジトリをクローン
git clone https://github.com/mastaBriX/magneto.git
cd magneto

# 開発モードでインストール
pip install -e .
```

### uv を使用

`uv` は `pyproject.toml` と完全に互換性のある高速な Python パッケージマネージャーです。

#### 1. uv のインストール

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. 依存関係の同期

プロジェクトのルートディレクトリで実行：

```bash
# リポジトリをクローン
git clone https://github.com/mastaBriX/magneto.git
cd magneto

# 依存関係を同期し、プロジェクトをインストール（開発モード）
uv sync

# 直接実行（インストール不要、uv が環境を自動管理）
uv run magneto file.torrent
uv run magneto folder/ -r -v

# 開発依存関係をインストール
uv sync --extra dev

# プロジェクト情報を表示
uv tree
```

## インストールの確認

インストール後、次のコマンドで確認：

```bash
# バージョンを表示
magneto --version

# ヘルプを表示
magneto --help
```

バージョン情報とヘルプドキュメントが表示されれば、インストール成功です！

## 依存関係

### 必須依存関係

- **bencode.py >= 4.0.0**: トーrentファイル形式の解析に使用
- **colorama >= 0.4.0**: Windows のカラー出力サポートに使用（オプションですが推奨）

### Python バージョン要件

- Python 3.7 以上
- Python 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13 をサポート

## 開発環境のセットアップ

開発に貢献したり、テストを実行したい場合：

```bash
# uv を使用
uv sync --extra dev

# または pip を使用
pip install -e ".[dev]"
```

開発依存関係には以下が含まれます：
- `pytest >= 7.0.0` - テストフレームワーク
- `pytest-cov >= 4.0.0` - テストカバレッジ
- `black >= 23.0.0` - コードフォーマッティング
- `ruff >= 0.1.0` - コードリンティング

## テストの実行

```bash
# すべてのテストを実行
pytest

# テストを実行し、カバレッジレポートを生成
pytest --cov=magneto --cov-report=html

# 特定のテストファイルを実行
pytest tests/test_core.py

# 詳細モード
pytest -v
```

## トラブルシューティング

### 問題：コマンド 'magneto' が見つからない

**解決策：**
- 適切にインストールされていることを確認：`pip install -e .`
- Python 環境を確認：正しい Python バージョンを使用していることを確認
- PATH 環境変数を確認：Python の Scripts ディレクトリが PATH にあることを確認

### 問題：インポートエラー（bencode モジュールが見つからない）

**解決策：**
```bash
pip install bencode.py
```

### 問題：Windows で色が表示されない

**解決策：**
```bash
pip install colorama
```

### 問題：権限エラー

**解決策：**
- Linux/macOS: `sudo` を使用するか、仮想環境を使用
- Windows: 管理者として実行するか、仮想環境を使用

## 次のステップ

インストール後、以下を実行できます：

- [はじめに](/ja/getting-started) - 基本的な使用方法を学ぶ
- [使用ガイド](/ja/usage) - すべての機能を学ぶ
