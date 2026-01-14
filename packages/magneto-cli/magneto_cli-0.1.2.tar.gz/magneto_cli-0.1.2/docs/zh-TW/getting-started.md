# 快速開始

本指南將幫助您快速開始使用 Magneto。只需幾分鐘，您就可以開始批次轉換種子檔案了。

## 前提條件

在開始之前，請確保您已經：

1. **安裝 Python 3.7+**
   ```bash
   python --version
   # 或
   python3 --version
   ```

2. **安裝 Magneto**
   ```bash
   pip install magneto-cli
   ```

## 最簡單的使用方式

### 1. 轉換單個檔案

```bash
magneto file.torrent
```

這將：
- 讀取 `file.torrent` 檔案
- 產生磁力連結
- 將結果儲存到 `magnet_links.txt`

### 2. 轉換資料夾中的所有檔案

```bash
magneto folder/
```

這將：
- 搜尋 `folder/` 目錄中的所有 `.torrent` 檔案
- 批次轉換它們
- 將結果儲存到 `folder/magnet_links.txt`

## 查看結果

轉換完成後，您可以：

1. **查看輸出檔案**
   - 預設情況下，結果儲存在 `magnet_links.txt` 檔案中
   - 檔案包含完整的轉換資訊

2. **使用標準輸出**
   ```bash
   magneto folder/ --stdout
   ```
   結果將直接列印到終端

3. **僅取得連結**
   ```bash
   magneto folder/ --stdout -f links_only
   ```
   只輸出磁力連結，方便複製使用

## 常用命令範例

### 遞迴搜尋子目錄

```bash
magneto folder/ -r
```

### 輸出 JSON 格式

```bash
magneto folder/ -f json
```

### 包含 Tracker 資訊

```bash
magneto folder/ --include-trackers
```

### 詳細輸出模式

```bash
magneto folder/ -v
```

## 下一步

- [安裝指南](/zh-TW/installation) - 了解詳細的安裝方法
- [使用指南](/zh-TW/usage) - 學習更多進階功能
- [API 參考](/zh-TW/api-reference) - 查看完整的 API 文件
