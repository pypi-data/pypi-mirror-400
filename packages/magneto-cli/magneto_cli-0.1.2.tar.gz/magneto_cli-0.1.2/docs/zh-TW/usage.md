# 使用指南

本指南詳細介紹 Magneto 的所有功能和使用方法。

## 基本用法

### 轉換單個檔案

```bash
magneto file.torrent
```

### 轉換資料夾中的所有檔案

```bash
magneto folder/
```

### 指定輸出檔案

```bash
magneto folder/ -o output.txt
```

## 輸出格式

Magneto 支援三種輸出格式：

### 1. 完整格式（預設）

```bash
magneto folder/ -f full
```

輸出範例：
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

### 2. 僅連結格式

```bash
magneto folder/ -f links_only
```

輸出範例：
```
magnet:?xt=urn:btih:ABC123...&dn=Example
magnet:?xt=urn:btih:DEF456...&dn=Another
```

### 3. JSON 格式

```bash
magneto folder/ -f json
```

輸出範例：
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

## 搜尋選項

### 遞迴搜尋

遞迴搜尋子目錄中的所有種子檔案：

```bash
magneto folder/ -r
```

### 大小寫敏感搜尋

預設情況下，搜尋不區分大小寫（`.torrent` 和 `.TORRENT` 都會被找到）。如果需要區分大小寫：

```bash
magneto folder/ --case-sensitive
```

## 轉換選項

### 包含 Tracker 資訊

預設情況下，產生的磁力連結不包含 tracker 資訊。如果需要包含：

```bash
magneto folder/ --include-trackers
```

產生的磁力連結將包含所有 tracker 位址：
```
magnet:?xt=urn:btih:ABC123...&dn=Example&tr=http://tracker1.com&tr=http://tracker2.com
```

## 顯示選項

### 詳細輸出模式

顯示詳細的處理資訊：

```bash
magneto folder/ -v
```

輸出包括：
- 每個檔案的 Info Hash
- 檔案名稱
- Tracker 數量

### 安靜模式

只顯示錯誤資訊：

```bash
magneto folder/ -q
```

### 停用顏色輸出

```bash
magneto folder/ --no-colors
```

## 輸出方式

### 儲存到檔案（預設）

```bash
magneto folder/ -o output.txt
```

結果將儲存到指定的檔案。如果不指定 `-o`，預設儲存到 `magnet_links.txt`。

### 輸出到標準輸出

```bash
magneto folder/ --stdout
```

結果將直接列印到終端，不儲存到檔案。

結合格式選項使用：

```bash
# 只輸出連結到終端
magneto folder/ --stdout -f links_only

# 輸出 JSON 到終端
magneto folder/ --stdout -f json
```

## 實用範例

### 範例 1：批次轉換並儲存為 JSON

```bash
magneto downloads/ -r -f json -o results.json
```

### 範例 2：快速取得所有磁力連結

```bash
magneto folder/ --stdout -f links_only -q
```

### 範例 3：詳細模式轉換並包含 tracker

```bash
magneto folder/ -v --include-trackers -o output.txt
```

### 範例 4：遞迴搜尋並輸出到檔案

```bash
magneto ~/Downloads/ -r -f full -o ~/magnets.txt
```

## 在程式碼中嵌入使用

除了命令列工具，Magneto 還提供了 Python API，可以直接在程式碼中使用。

### 快速開始

使用 `torrent_to_magnet` 函數是最簡單的整合方式：

```python
from magneto import torrent_to_magnet

# 從檔案路徑轉換
magnet, info_hash, metadata = torrent_to_magnet("path/to/file.torrent")
print(f"磁力連結: {magnet}")
print(f"Info Hash: {info_hash}")
print(f"檔案名稱: {metadata['name']}")

# 從 URL 轉換
magnet, info_hash, metadata = torrent_to_magnet("https://example.com/file.torrent")

# 包含 tracker 資訊
magnet, info_hash, metadata = torrent_to_magnet(
    "file.torrent", 
    include_trackers=True
)
```

### 批次處理範例

```python
from pathlib import Path
from magneto import torrent_to_magnet

def batch_convert(folder_path: str):
    """批次轉換資料夾中的所有種子檔案"""
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

# 使用範例
results = batch_convert("downloads/")
```

### 處理 URL 範例

```python
from magneto import torrent_to_magnet

def convert_from_url(url: str):
    """從 URL 下載並轉換種子檔案"""
    try:
        magnet, info_hash, metadata = torrent_to_magnet(url, include_trackers=True)
        print(f"磁力連結: {magnet}")
        print(f"來源: {metadata.get('source_url', 'N/A')}")
        return magnet
    except IOError as e:
        print(f"下載失敗: {e}")
    except ValueError as e:
        print(f"檔案格式錯誤: {e}")

# 使用範例
convert_from_url("https://example.com/torrent.torrent")
```

### 錯誤處理

```python
from magneto import torrent_to_magnet

try:
    magnet, info_hash, metadata = torrent_to_magnet("file.torrent")
except IOError as e:
    print(f"檔案讀取錯誤: {e}")
except ValueError as e:
    print(f"檔案格式錯誤: {e}")
except ImportError as e:
    print(f"依賴缺失: {e}")
```

### 返回值說明

`torrent_to_magnet` 函數返回一個三元組：

1. **magnet_link** (str): 產生的磁力連結
2. **info_hash** (str): 種子的 Info Hash（十六進位字串，大寫）
3. **metadata** (Dict): 元資料字典，包含：
   - `name`: 檔案名稱
   - `trackers`: Tracker 列表（即使 `include_trackers=False` 也會包含）
   - `info_hash`: Info Hash
   - `file_size`: 檔案大小（位元組）
   - `source_url`: 如果輸入是 URL，則包含來源 URL

### 更多 API 用法

如需更高級的功能（如自訂輸出格式、批次處理等），請參考 [API 參考文件](/zh-TW/api-reference)。

## 命令列參數參考

### 位置參數

- `input` - 輸入的種子檔案或包含種子檔案的資料夾路徑

### 輸出選項

- `-o, --output FILE` - 指定輸出檔案路徑（預設：輸入目錄下的 `magnet_links.txt`）
- `-f, --format {full,links_only,json}` - 輸出格式（預設：full）
- `--stdout` - 將結果列印到標準輸出而不是儲存到檔案

### 搜尋選項

- `-r, --recursive` - 遞迴搜尋子目錄中的種子檔案
- `--case-sensitive` - 大小寫敏感的副檔名搜尋

### 轉換選項

- `--include-trackers` - 在磁力連結中包含 tracker 資訊

### 顯示選項

- `-v, --verbose` - 顯示詳細輸出資訊
- `-q, --quiet` - 安靜模式，只顯示錯誤訊息
- `--no-colors` - 停用彩色輸出

### 其他選項

- `-h, --help` - 顯示說明資訊並結束
- `--version` - 顯示版本資訊並結束

## 使用技巧

### 1. 管道操作

將輸出傳遞給其他命令：

```bash
magneto folder/ --stdout -f links_only | grep "ABC123"
```

### 2. 批次處理大資料夾

對於包含大量檔案的資料夾，建議使用安靜模式：

```bash
magneto large_folder/ -r -q -f links_only -o results.txt
```

### 3. 結合腳本使用

在腳本中使用 JSON 格式便於解析：

```bash
magneto folder/ -f json -o results.json
# 然後使用 Python/Node.js 等解析 JSON
```

## 錯誤處理

### 常見錯誤

1. **檔案不存在**
   ```
   Error: Path does not exist: /path/to/file
   ```

2. **檔案格式錯誤**
   ```
   ✗ example.torrent: Unable to parse torrent file
   ```

3. **權限錯誤**
   ```
   Error: Unable to read file /path/to/file: Permission denied
   ```

### 錯誤統計

處理完成後，會顯示統計資訊：

```
================================================================================
Processing complete: 10 file(s) total
Success: 8
Failed: 2
================================================================================
```

## 下一步

- [API 參考](/zh-TW/api-reference) - 了解如何在程式碼中使用 Magneto
- [快速開始](/zh-TW/getting-started) - 回顧基本用法
