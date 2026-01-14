# API 参考

本文档介绍 Magneto 的 Python API，适用于需要在代码中集成 Magneto 功能的开发者。

## 核心模块

### TorrentConverter

`magneto.core.TorrentConverter` 是核心转换类，负责将种子文件转换为磁力链接。

#### 初始化

```python
from magneto.core import TorrentConverter

converter = TorrentConverter()
```

#### 方法

##### `read_torrent_file(torrent_path: Path) -> bytes`

读取种子文件内容。

**参数：**
- `torrent_path` (Path): 种子文件路径

**返回：**
- `bytes`: 文件的二进制内容

**异常：**
- `IOError`: 文件读取失败

**示例：**
```python
from pathlib import Path

data = converter.read_torrent_file(Path("example.torrent"))
```

##### `parse_torrent(torrent_data: bytes) -> Dict`

解析种子文件数据。

**参数：**
- `torrent_data` (bytes): 种子文件的二进制数据

**返回：**
- `Dict`: 解析后的种子数据字典

**异常：**
- `ValueError`: 种子文件格式错误

**示例：**
```python
torrent_data = converter.parse_torrent(data)
```

##### `get_info_hash(torrent_data: Dict) -> str`

从种子数据中提取 Info Hash。

**参数：**
- `torrent_data` (Dict): 解析后的种子数据字典

**返回：**
- `str`: Info Hash 十六进制字符串（大写）

**异常：**
- `ValueError`: 种子数据缺少 info 字段

**示例：**
```python
info_hash = converter.get_info_hash(torrent_data)
# 输出: "ABC123DEF456..."
```

##### `get_torrent_name(torrent_data: Dict) -> Optional[str]`

从种子数据中提取文件名。

**参数：**
- `torrent_data` (Dict): 解析后的种子数据字典

**返回：**
- `Optional[str]`: 文件名，如果不存在则返回 None

**示例：**
```python
name = converter.get_torrent_name(torrent_data)
# 输出: "Example File"
```

##### `get_trackers(torrent_data: Dict) -> list`

从种子数据中提取 tracker 列表。

**参数：**
- `torrent_data` (Dict): 解析后的种子数据字典

**返回：**
- `list`: Tracker URL 列表

**示例：**
```python
trackers = converter.get_trackers(torrent_data)
# 输出: ["http://tracker1.example.com", "http://tracker2.example.com"]
```

##### `generate_magnet_link(info_hash: str, name: Optional[str] = None, trackers: Optional[list] = None) -> str`

生成磁力链接。

**参数：**
- `info_hash` (str): Info Hash 字符串
- `name` (Optional[str]): 文件名（可选）
- `trackers` (Optional[list]): Tracker 列表（可选）

**返回：**
- `str`: 完整的磁力链接

**示例：**
```python
magnet = converter.generate_magnet_link(
    info_hash="ABC123...",
    name="Example",
    trackers=["http://tracker.example.com"]
)
# 输出: "magnet:?xt=urn:btih:ABC123...&dn=Example&tr=http://tracker.example.com"
```

##### `convert(torrent_path: Path, include_trackers: bool = False) -> Tuple[str, str, Dict]`

将单个种子文件转换为磁力链接。

**参数：**
- `torrent_path` (Path): 种子文件路径
- `include_trackers` (bool): 是否在磁力链接中包含 tracker 信息

**返回：**
- `Tuple[str, str, Dict]`: (magnet_link, info_hash, metadata)
  - `magnet_link`: 磁力链接
  - `info_hash`: Info Hash
  - `metadata`: 元数据字典，包含：
    - `name`: 文件名
    - `trackers`: Tracker 列表
    - `info_hash`: Info Hash
    - `file_size`: 文件大小

**异常：**
- `IOError`: 文件读取失败
- `ValueError`: 种子文件格式错误

**示例：**
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

## 工具函数

### `collect_torrent_files`

`magneto.utils.collect_torrent_files` - 收集种子文件。

```python
from magneto.utils import collect_torrent_files
from pathlib import Path

# 收集当前目录的种子文件
files = collect_torrent_files(Path("folder/"))

# 递归搜索
files = collect_torrent_files(Path("folder/"), recursive=True)

# 大小写敏感搜索
files = collect_torrent_files(Path("folder/"), case_sensitive=True)
```

**参数：**
- `input_path` (Path): 输入路径（文件或目录）
- `recursive` (bool): 是否递归搜索子目录（默认：False）
- `case_sensitive` (bool): 是否大小写敏感（默认：False）

**返回：**
- `List[Path]`: 种子文件路径列表

### `get_output_path`

`magneto.utils.get_output_path` - 确定输出文件路径。

```python
from magneto.utils import get_output_path
from pathlib import Path

# 自动确定输出路径
output = get_output_path(Path("folder/"))

# 指定输出路径
output = get_output_path(Path("folder/"), Path("custom_output.txt"))
```

**参数：**
- `input_path` (Path): 输入路径
- `output_path` (Optional[Path]): 用户指定的输出路径（可选）
- `default_name` (str): 默认输出文件名（默认："magnet_links.txt"）

**返回：**
- `Path`: 输出文件路径

## UI 模块

### UI

`magneto.ui.UI` - 用户界面处理器。

```python
from magneto.ui import UI

# 初始化 UI
ui = UI(verbose=True, quiet=False, use_colors=True)

# 打印消息
ui.print_success("转换成功")
ui.print_error("转换失败")
ui.print_warning("警告信息")
ui.print_info("信息提示")
ui.print_verbose("详细信息")

# 保存结果
results = [
    ("file.torrent", "magnet:...", "ABC123...", {"name": "Example"})
]
ui.save_results(results, Path("output.txt"), format_type="full")

# 打印结果到标准输出
ui.print_results(results, format_type="json")

# 打印摘要
ui.print_summary()
```

**初始化参数：**
- `verbose` (bool): 是否显示详细信息（默认：False）
- `quiet` (bool): 是否使用安静模式（默认：False）
- `use_colors` (bool): 是否使用彩色输出（默认：True）

## 完整示例

### 示例 1：批量转换文件

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

### 示例 2：自定义输出格式

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

### 示例 3：集成到脚本中

```python
#!/usr/bin/env python3
"""自定义转换脚本"""
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

## 异常处理

### 常见异常

- `IOError`: 文件读取失败
- `ValueError`: 种子文件格式错误或缺少必要字段
- `ImportError`: 缺少必要的依赖包（如 bencode）

### 异常处理示例

```python
from magneto.core import TorrentConverter
from pathlib import Path

converter = TorrentConverter()

try:
    magnet_link, info_hash, metadata = converter.convert(Path("file.torrent"))
except IOError as e:
    print(f"文件读取错误: {e}")
except ValueError as e:
    print(f"文件格式错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 类型提示

所有函数和类都包含完整的类型提示，便于 IDE 自动补全和类型检查。

```python
from typing import Dict, Optional, Tuple, List
from pathlib import Path
```

## 下一步

- [使用指南](/zh/usage) - 了解命令行使用方法
- [快速开始](/zh/getting-started) - 学习基本用法

