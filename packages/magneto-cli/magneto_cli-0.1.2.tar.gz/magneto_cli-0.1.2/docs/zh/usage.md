# 使用指南

本指南详细介绍 Magneto 的所有功能和使用方法。

## 基本用法

### 转换单个文件

```bash
magneto file.torrent
```

### 转换文件夹中的所有文件

```bash
magneto folder/
```

### 指定输出文件

```bash
magneto folder/ -o output.txt
```

## 输出格式

Magneto 支持三种输出格式：

### 1. 完整格式（默认）

```bash
magneto folder/ -f full
```

输出示例：
```
================================================================================
Torrent to Magnet Link Conversion Results
================================================================================

File: example.torrent
Magnet Link: magnet:?xt=urn:btih:ABC123...&dn=Example
Info Hash: ABC123...
Name: Example
Trackers: 3 found
--------------------------------------------------------------------------------

================================================================================
Magnet Link List (Links Only)
================================================================================

magnet:?xt=urn:btih:ABC123...&dn=Example
```

### 2. 仅链接格式

```bash
magneto folder/ -f links_only
```

输出示例：
```
magnet:?xt=urn:btih:ABC123...&dn=Example
magnet:?xt=urn:btih:DEF456...&dn=Another
```

### 3. JSON 格式

```bash
magneto folder/ -f json
```

输出示例：
```json
[
  {
    "file": "example.torrent",
    "magnet": "magnet:?xt=urn:btih:ABC123...&dn=Example",
    "info_hash": "ABC123...",
    "name": "Example",
    "trackers": [
      "http://tracker1.example.com",
      "http://tracker2.example.com"
    ]
  }
]
```

## 搜索选项

### 递归搜索

递归搜索子目录中的所有种子文件：

```bash
magneto folder/ -r
```

### 大小写敏感搜索

默认情况下，搜索不区分大小写（`.torrent` 和 `.TORRENT` 都会被找到）。如果需要区分大小写：

```bash
magneto folder/ --case-sensitive
```

## 转换选项

### 包含 Tracker 信息

默认情况下，生成的磁力链接不包含 tracker 信息。如果需要包含：

```bash
magneto folder/ --include-trackers
```

生成的磁力链接将包含所有 tracker 地址：
```
magnet:?xt=urn:btih:ABC123...&dn=Example&tr=http://tracker1.com&tr=http://tracker2.com
```

## 显示选项

### 详细输出模式

显示详细的处理信息：

```bash
magneto folder/ -v
```

输出包括：
- 每个文件的 Info Hash
- 文件名
- Tracker 数量

### 安静模式

只显示错误信息：

```bash
magneto folder/ -q
```

### 禁用颜色输出

```bash
magneto folder/ --no-colors
```

## 输出方式

### 保存到文件（默认）

```bash
magneto folder/ -o output.txt
```

结果将保存到指定的文件。如果不指定 `-o`，默认保存到 `magnet_links.txt`。

### 输出到标准输出

```bash
magneto folder/ --stdout
```

结果将直接打印到终端，不保存到文件。

结合格式选项使用：

```bash
# 只输出链接到终端
magneto folder/ --stdout -f links_only

# 输出 JSON 到终端
magneto folder/ --stdout -f json
```

## 实用示例

### 示例 1：批量转换并保存为 JSON

```bash
magneto downloads/ -r -f json -o results.json
```

### 示例 2：快速获取所有磁力链接

```bash
magneto folder/ --stdout -f links_only -q
```

### 示例 3：详细模式转换并包含 tracker

```bash
magneto folder/ -v --include-trackers -o output.txt
```

### 示例 4：递归搜索并输出到文件

```bash
magneto ~/Downloads/ -r -f full -o ~/magnets.txt
```

## 在代码中嵌入使用

除了命令行工具，Magneto 还提供了 Python API，可以直接在代码中使用。

### 快速开始

使用 `torrent_to_magnet` 函数是最简单的集成方式：

```python
from magneto import torrent_to_magnet

# 从文件路径转换
magnet, info_hash, metadata = torrent_to_magnet("path/to/file.torrent")
print(f"磁力链接: {magnet}")
print(f"Info Hash: {info_hash}")
print(f"文件名: {metadata['name']}")

# 从 URL 转换
magnet, info_hash, metadata = torrent_to_magnet("https://example.com/file.torrent")

# 包含 tracker 信息
magnet, info_hash, metadata = torrent_to_magnet(
    "file.torrent", 
    include_trackers=True
)
```

### 批量处理示例

```python
from pathlib import Path
from magneto import torrent_to_magnet

def batch_convert(folder_path: str):
    """批量转换文件夹中的所有种子文件"""
    folder = Path(folder_path)
    results = []
    
    for torrent_file in folder.glob("*.torrent"):
        try:
            magnet, info_hash, metadata = torrent_to_magnet(torrent_file)
            results.append({
                "file": str(torrent_file),
                "magnet": magnet,
                "info_hash": info_hash,
                "name": metadata["name"]
            })
            print(f"✓ {torrent_file.name}")
        except Exception as e:
            print(f"✗ {torrent_file.name}: {e}")
    
    return results

# 使用示例
results = batch_convert("downloads/")
```

### 处理 URL 示例

```python
from magneto import torrent_to_magnet

def convert_from_url(url: str):
    """从 URL 下载并转换种子文件"""
    try:
        magnet, info_hash, metadata = torrent_to_magnet(url, include_trackers=True)
        print(f"磁力链接: {magnet}")
        print(f"来源: {metadata.get('source_url', 'N/A')}")
        return magnet
    except IOError as e:
        print(f"下载失败: {e}")
    except ValueError as e:
        print(f"文件格式错误: {e}")

# 使用示例
convert_from_url("https://example.com/torrent.torrent")
```

### 错误处理

```python
from magneto import torrent_to_magnet

try:
    magnet, info_hash, metadata = torrent_to_magnet("file.torrent")
except IOError as e:
    print(f"文件读取错误: {e}")
except ValueError as e:
    print(f"文件格式错误: {e}")
except ImportError as e:
    print(f"依赖缺失: {e}")
```

### 返回值说明

`torrent_to_magnet` 函数返回一个三元组：

1. **magnet_link** (str): 生成的磁力链接
2. **info_hash** (str): 种子的 Info Hash（十六进制字符串，大写）
3. **metadata** (Dict): 元数据字典，包含：
   - `name`: 文件名
   - `trackers`: Tracker 列表（即使 `include_trackers=False` 也会包含）
   - `info_hash`: Info Hash
   - `file_size`: 文件大小（字节）
   - `source_url`: 如果输入是 URL，则包含源 URL

### 更多 API 用法

如需更高级的功能（如自定义输出格式、批量处理等），请参考 [API 参考文档](/zh/api-reference)。

## 命令行参数参考

### 位置参数

- `input` - 输入的种子文件或包含种子文件的文件夹路径

### 输出选项

- `-o, --output FILE` - 指定输出文件路径（默认：输入目录下的 `magnet_links.txt`）
- `-f, --format {full,links_only,json}` - 输出格式（默认：full）
- `--stdout` - 将结果打印到标准输出而不是保存到文件

### 搜索选项

- `-r, --recursive` - 递归搜索子目录中的种子文件
- `--case-sensitive` - 大小写敏感的扩展名搜索

### 转换选项

- `--include-trackers` - 在磁力链接中包含 tracker 信息

### 显示选项

- `-v, --verbose` - 显示详细输出信息
- `-q, --quiet` - 安静模式，只显示错误消息
- `--no-colors` - 禁用彩色输出

### 其他选项

- `-h, --help` - 显示帮助信息并退出
- `--version` - 显示版本信息并退出

## 使用技巧

### 1. 管道操作

将输出传递给其他命令：

```bash
magneto folder/ --stdout -f links_only | grep "ABC123"
```

### 2. 批量处理大文件夹

对于包含大量文件的文件夹，建议使用安静模式：

```bash
magneto large_folder/ -r -q -f links_only -o results.txt
```

### 3. 结合脚本使用

在脚本中使用 JSON 格式便于解析：

```bash
magneto folder/ -f json -o results.json
# 然后使用 Python/Node.js 等解析 JSON
```

## 错误处理

### 常见错误

1. **文件不存在**
   ```
   Error: Path does not exist: /path/to/file
   ```

2. **文件格式错误**
   ```
   ✗ example.torrent: Unable to parse torrent file
   ```

3. **权限错误**
   ```
   Error: Unable to read file /path/to/file: Permission denied
   ```

### 错误统计

处理完成后，会显示统计信息：

```
================================================================================
Processing complete: 10 file(s) total
Success: 8
Failed: 2
================================================================================
```

## 下一步

- [API 参考](/zh/api-reference) - 了解如何在代码中使用 Magneto
- [快速开始](/zh/getting-started) - 回顾基本用法

