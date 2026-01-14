# API 參考

本文件介紹 Magneto 的 Python API，適用於需要在程式碼中整合 Magneto 功能的開發者。

## 核心模組

### TorrentConverter

`magneto.core.TorrentConverter` 是核心轉換類別，負責將種子檔案轉換為磁力連結。

#### 初始化

```python
from magneto.core import TorrentConverter

converter = TorrentConverter()
```

#### 方法

##### `read_torrent_file(torrent_path: Path) -> bytes`

讀取種子檔案內容。

**參數：**
- `torrent_path` (Path): 種子檔案路徑

**返回：**
- `bytes`: 檔案的二進位內容

**異常：**
- `IOError`: 檔案讀取失敗

**範例：**
```python
from pathlib import Path

data = converter.read_torrent_file(Path("example.torrent"))
```

##### `parse_torrent(torrent_data: bytes) -> Dict`

解析種子檔案資料。

**參數：**
- `torrent_data` (bytes): 種子檔案的二進位資料

**返回：**
- `Dict`: 解析後的種子資料字典

**異常：**
- `ValueError`: 種子檔案格式錯誤

**範例：**
```python
torrent_data = converter.parse_torrent(data)
```

##### `get_info_hash(torrent_data: Dict) -> str`

從種子資料中提取 Info Hash。

**參數：**
- `torrent_data` (Dict): 解析後的種子資料字典

**返回：**
- `str`: Info Hash 十六進位字串（大寫）

**異常：**
- `ValueError`: 種子資料缺少 info 欄位

**範例：**
```python
info_hash = converter.get_info_hash(torrent_data)
# 輸出: "ABC123DEF456..."
```

##### `get_torrent_name(torrent_data: Dict) -> Optional[str]`

從種子資料中提取檔案名稱。

**參數：**
- `torrent_data` (Dict): 解析後的種子資料字典

**返回：**
- `Optional[str]`: 檔案名稱，如果不存在則返回 None

**範例：**
```python
name = converter.get_torrent_name(torrent_data)
# 輸出: "Example File"
```

##### `get_trackers(torrent_data: Dict) -> list`

從種子資料中提取 tracker 列表。

**參數：**
- `torrent_data` (Dict): 解析後的種子資料字典

**返回：**
- `list`: Tracker URL 列表

**範例：**
```python
trackers = converter.get_trackers(torrent_data)
# 輸出: ["http://tracker1.example.com", "http://tracker2.example.com"]
```

##### `generate_magnet_link(info_hash: str, name: Optional[str] = None, trackers: Optional[list] = None) -> str`

產生磁力連結。

**參數：**
- `info_hash` (str): Info Hash 字串
- `name` (Optional[str]): 檔案名稱（可選）
- `trackers` (Optional[list]): Tracker 列表（可選）

**返回：**
- `str`: 完整的磁力連結

**範例：**
```python
magnet = converter.generate_magnet_link(
    info_hash="ABC123...",
    name="Example",
    trackers=["http://tracker.example.com"]
)
# 輸出: "magnet:?xt=urn:btih:ABC123...&dn=Example&tr=http://tracker.example.com"
```

##### `convert(torrent_path: Path, include_trackers: bool = False) -> Tuple[str, str, Dict]`

將單個種子檔案轉換為磁力連結。

**參數：**
- `torrent_path` (Path): 種子檔案路徑
- `include_trackers` (bool): 是否在磁力連結中包含 tracker 資訊

**返回：**
- `Tuple[str, str, Dict]`: (magnet_link, info_hash, metadata)
  - `magnet_link`: 磁力連結
  - `info_hash`: Info Hash
  - `metadata`: 元資料字典，包含：
    - `name`: 檔案名稱
    - `trackers`: Tracker 列表
    - `info_hash`: Info Hash
    - `file_size`: 檔案大小

**異常：**
- `IOError`: 檔案讀取失敗
- `ValueError`: 種子檔案格式錯誤

**範例：**
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

## 工具函數

### `collect_torrent_files`

`magneto.utils.collect_torrent_files` - 收集種子檔案。

```python
from magneto.utils import collect_torrent_files
from pathlib import Path

# 收集當前目錄的種子檔案
files = collect_torrent_files(Path("folder/"))

# 遞迴搜尋
files = collect_torrent_files(Path("folder/"), recursive=True)

# 大小寫敏感搜尋
files = collect_torrent_files(Path("folder/"), case_sensitive=True)
```

**參數：**
- `input_path` (Path): 輸入路徑（檔案或目錄）
- `recursive` (bool): 是否遞迴搜尋子目錄（預設：False）
- `case_sensitive` (bool): 是否大小寫敏感（預設：False）

**返回：**
- `List[Path]`: 種子檔案路徑列表

### `get_output_path`

`magneto.utils.get_output_path` - 確定輸出檔案路徑。

```python
from magneto.utils import get_output_path
from pathlib import Path

# 自動確定輸出路徑
output = get_output_path(Path("folder/"))

# 指定輸出路徑
output = get_output_path(Path("folder/"), Path("custom_output.txt"))
```

**參數：**
- `input_path` (Path): 輸入路徑
- `output_path` (Optional[Path]): 使用者指定的輸出路徑（可選）
- `default_name` (str): 預設輸出檔案名稱（預設："magnet_links.txt"）

**返回：**
- `Path`: 輸出檔案路徑

## UI 模組

### UI

`magneto.ui.UI` - 使用者介面處理器。

```python
from magneto.ui import UI

# 初始化 UI
ui = UI(verbose=True, quiet=False, use_colors=True)

# 列印訊息
ui.print_success("轉換成功")
ui.print_error("轉換失敗")
ui.print_warning("警告訊息")
ui.print_info("資訊提示")
ui.print_verbose("詳細資訊")

# 儲存結果
results = [
    ("file.torrent", "magnet:...", "ABC123...", {"name": "Example"})
]
ui.save_results(results, Path("output.txt"), format_type="full")

# 列印結果到標準輸出
ui.print_results(results, format_type="json")

# 列印摘要
ui.print_summary()
```

**初始化參數：**
- `verbose` (bool): 是否顯示詳細資訊（預設：False）
- `quiet` (bool): 是否使用安靜模式（預設：False）
- `use_colors` (bool): 是否使用彩色輸出（預設：True）

## 完整範例

### 範例 1：批次轉換檔案

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

### 範例 2：自訂輸出格式

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

### 範例 3：整合到腳本中

```python
#!/usr/bin/env python3
"""自訂轉換腳本"""
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

## 異常處理

### 常見異常

- `IOError`: 檔案讀取失敗
- `ValueError`: 種子檔案格式錯誤或缺少必要欄位
- `ImportError`: 缺少必要的依賴套件（如 bencode）

### 異常處理範例

```python
from magneto.core import TorrentConverter
from pathlib import Path

converter = TorrentConverter()

try:
    magnet_link, info_hash, metadata = converter.convert(Path("file.torrent"))
except IOError as e:
    print(f"檔案讀取錯誤: {e}")
except ValueError as e:
    print(f"檔案格式錯誤: {e}")
except Exception as e:
    print(f"未知錯誤: {e}")
```

## 型別提示

所有函數和類別都包含完整的型別提示，便於 IDE 自動補全和型別檢查。

```python
from typing import Dict, Optional, Tuple, List
from pathlib import Path
```

## 下一步

- [使用指南](/zh-TW/usage) - 了解命令列使用方法
- [快速開始](/zh-TW/getting-started) - 學習基本用法
