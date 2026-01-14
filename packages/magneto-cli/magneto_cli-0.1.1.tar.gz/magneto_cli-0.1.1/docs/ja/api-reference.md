# API リファレンス

このドキュメントは、Magneto の Python API について説明しており、コードに Magneto 機能を統合する必要がある開発者向けです。

## コアモジュール

### TorrentConverter

`magneto.core.TorrentConverter` は、トーrentファイルをマグネットリンクに変換する責任を持つコア変換クラスです。

#### 初期化

```python
from magneto.core import TorrentConverter

converter = TorrentConverter()
```

#### メソッド

##### `read_torrent_file(torrent_path: Path) -> bytes`

トーrentファイルの内容を読み取ります。

**パラメータ：**
- `torrent_path` (Path): トーrentファイルへのパス

**戻り値：**
- `bytes`: ファイルのバイナリ内容

**例外：**
- `IOError`: ファイル読み取り失敗

**例：**
```python
from pathlib import Path

data = converter.read_torrent_file(Path("example.torrent"))
```

##### `parse_torrent(torrent_data: bytes) -> Dict`

トーrentファイルデータを解析します。

**パラメータ：**
- `torrent_data` (bytes): トーrentファイルのバイナリデータ

**戻り値：**
- `Dict`: 解析されたトーrentデータ辞書

**例外：**
- `ValueError`: トーrentファイル形式エラー

**例：**
```python
torrent_data = converter.parse_torrent(data)
```

##### `get_info_hash(torrent_data: Dict) -> str`

トーrentデータから Info Hash を抽出します。

**パラメータ：**
- `torrent_data` (Dict): 解析されたトーrentデータ辞書

**戻り値：**
- `str`: 16進数文字列としての Info Hash（大文字）

**例外：**
- `ValueError`: トーrentデータに info フィールドが欠けている

**例：**
```python
info_hash = converter.get_info_hash(torrent_data)
# 出力: "ABC123DEF456..."
```

##### `get_torrent_name(torrent_data: Dict) -> Optional[str]`

トーrentデータからファイル名を抽出します。

**パラメータ：**
- `torrent_data` (Dict): 解析されたトーrentデータ辞書

**戻り値：**
- `Optional[str]`: ファイル名、存在しない場合は None

**例：**
```python
name = converter.get_torrent_name(torrent_data)
# 出力: "Example File"
```

##### `get_trackers(torrent_data: Dict) -> list`

トーrentデータからトラッカーリストを抽出します。

**パラメータ：**
- `torrent_data` (Dict): 解析されたトーrentデータ辞書

**戻り値：**
- `list`: トラッカー URL のリスト

**例：**
```python
trackers = converter.get_trackers(torrent_data)
# 出力: ["http://tracker1.example.com", "http://tracker2.example.com"]
```

##### `generate_magnet_link(info_hash: str, name: Optional[str] = None, trackers: Optional[list] = None) -> str`

マグネットリンクを生成します。

**パラメータ：**
- `info_hash` (str): Info Hash 文字列
- `name` (Optional[str]): ファイル名（オプション）
- `trackers` (Optional[list]): トラッカーリスト（オプション）

**戻り値：**
- `str`: 完全なマグネットリンク

**例：**
```python
magnet = converter.generate_magnet_link(
    info_hash="ABC123...",
    name="Example",
    trackers=["http://tracker.example.com"]
)
# 出力: "magnet:?xt=urn:btih:ABC123...&dn=Example&tr=http://tracker.example.com"
```

##### `convert(torrent_path: Path, include_trackers: bool = False) -> Tuple[str, str, Dict]`

単一のトーrentファイルをマグネットリンクに変換します。

**パラメータ：**
- `torrent_path` (Path): トーrentファイルへのパス
- `include_trackers` (bool): マグネットリンクにトラッカーを含めるかどうか

**戻り値：**
- `Tuple[str, str, Dict]`: (magnet_link, info_hash, metadata)
  - `magnet_link`: マグネットリンク
  - `info_hash`: Info Hash
  - `metadata`: メタデータ辞書、以下を含む：
    - `name`: ファイル名
    - `trackers`: トラッカーリスト
    - `info_hash`: Info Hash
    - `file_size`: ファイルサイズ

**例外：**
- `IOError`: ファイル読み取り失敗
- `ValueError`: トーrentファイル形式エラー

**例：**
```python
from pathlib import Path

magnet_link, info_hash, metadata = converter.convert(
    Path("example.torrent"),
    include_trackers=True
)

print(f"Magnet: {magnet_link}")
print(f"Info Hash: {info_hash}")
print(f"Name: {metadata['name']}")
print(f"Trackers: {metadata['trackers']}")
```

## ユーティリティ関数

### `collect_torrent_files`

`magneto.utils.collect_torrent_files` - トーrentファイルを収集します。

```python
from magneto.utils import collect_torrent_files
from pathlib import Path

# 現在のディレクトリのトーrentファイルを収集
files = collect_torrent_files(Path("folder/"))

# 再帰検索
files = collect_torrent_files(Path("folder/"), recursive=True)

# 大文字小文字を区別する検索
files = collect_torrent_files(Path("folder/"), case_sensitive=True)
```

**パラメータ：**
- `input_path` (Path): 入力パス（ファイルまたはディレクトリ）
- `recursive` (bool): サブディレクトリを再帰的に検索するかどうか（デフォルト：False）
- `case_sensitive` (bool): 大文字小文字を区別するかどうか（デフォルト：False）

**戻り値：**
- `List[Path]`: トーrentファイルパスのリスト

### `get_output_path`

`magneto.utils.get_output_path` - 出力ファイルパスを決定します。

```python
from magneto.utils import get_output_path
from pathlib import Path

# 出力パスを自動決定
output = get_output_path(Path("folder/"))

# 出力パスを指定
output = get_output_path(Path("folder/"), Path("custom_output.txt"))
```

**パラメータ：**
- `input_path` (Path): 入力パス
- `output_path` (Optional[Path]): ユーザー指定の出力パス（オプション）
- `default_name` (str): デフォルトの出力ファイル名（デフォルト："magnet_links.txt"）

**戻り値：**
- `Path`: 出力ファイルパス

## UI モジュール

### UI

`magneto.ui.UI` - ユーザーインターフェースハンドラー。

```python
from magneto.ui import UI

# UI を初期化
ui = UI(verbose=True, quiet=False, use_colors=True)

# メッセージを出力
ui.print_success("変換成功")
ui.print_error("変換失敗")
ui.print_warning("警告メッセージ")
ui.print_info("情報メッセージ")
ui.print_verbose("詳細メッセージ")

# 結果を保存
results = [
    ("file.torrent", "magnet:...", "ABC123...", {"name": "Example"})
]
ui.save_results(results, Path("output.txt"), format_type="full")

# 結果を標準出力に出力
ui.print_results(results, format_type="json")

# サマリーを出力
ui.print_summary()
```

**初期化パラメータ：**
- `verbose` (bool): 詳細情報を表示するかどうか（デフォルト：False）
- `quiet` (bool): サイレントモードを使用するかどうか（デフォルト：False）
- `use_colors` (bool): カラー出力を使用するかどうか（デフォルト：True）

## 完全な例

### 例1：ファイルの一括変換

```python
from pathlib import Path
from magneto.core import TorrentConverter
from magneto.utils import collect_torrent_files

converter = TorrentConverter()
torrent_files = collect_torrent_files(Path("folder/"), recursive=True)

results = []
for torrent_file in torrent_files:
    try:
        magnet_link, info_hash, metadata = converter.convert(
            torrent_file,
            include_trackers=True
        )
        results.append((str(torrent_file), magnet_link, info_hash, metadata))
        print(f"✓ {torrent_file.name}: {magnet_link}")
    except Exception as e:
        print(f"✗ {torrent_file.name}: {e}")
```

### 例2：カスタム出力形式

```python
import json
from pathlib import Path
from magneto.core import TorrentConverter

converter = TorrentConverter()
torrent_file = Path("example.torrent")

magnet_link, info_hash, metadata = converter.convert(torrent_file)

output = {
    "file": str(torrent_file),
    "magnet": magnet_link,
    "info_hash": info_hash,
    "name": metadata.get("name"),
    "trackers": metadata.get("trackers", [])
}

with open("output.json", "w", encoding="utf-8") as f:
    json.dump([output], f, ensure_ascii=False, indent=2)
```

### 例3：スクリプトへの統合

```python
#!/usr/bin/env python3
"""カスタム変換スクリプト"""
from pathlib import Path
from magneto.core import TorrentConverter
from magneto.utils import collect_torrent_files

def convert_folder(folder_path: str, output_file: str):
    converter = TorrentConverter()
    torrent_files = collect_torrent_files(Path(folder_path), recursive=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        for torrent_file in torrent_files:
            try:
                magnet_link, _, _ = converter.convert(torrent_file)
                f.write(f"{magnet_link}\n")
                print(f"✓ {torrent_file.name}")
            except Exception as e:
                print(f"✗ {torrent_file.name}: {e}")

if __name__ == "__main__":
    convert_folder("downloads/", "magnets.txt")
```

## 例外処理

### 一般的な例外

- `IOError`: ファイル読み取り失敗
- `ValueError`: トーrentファイル形式エラーまたは必須フィールドの欠落
- `ImportError`: 必須依存関係の欠落（例：bencode）

### 例外処理の例

```python
from magneto.core import TorrentConverter
from pathlib import Path

converter = TorrentConverter()

try:
    magnet_link, info_hash, metadata = converter.convert(Path("file.torrent"))
except IOError as e:
    print(f"ファイル読み取りエラー: {e}")
except ValueError as e:
    print(f"ファイル形式エラー: {e}")
except Exception as e:
    print(f"不明なエラー: {e}")
```

## 型ヒント

すべての関数とクラスには、IDE の自動補完と型チェックのための完全な型ヒントが含まれています。

```python
from typing import Dict, Optional, Tuple, List
from pathlib import Path
```

## 次のステップ

- [使用ガイド](/ja/usage) - コマンドラインの使用方法を学ぶ
- [はじめに](/ja/getting-started) - 基本的な使用方法を学ぶ
