# 快速开始

本指南将帮助您快速开始使用 Magneto。只需几分钟，您就可以开始批量转换种子文件了。

## 前提条件

在开始之前，请确保您已经：

1. **安装 Python 3.7+**
   ```bash
   python --version
   # 或
   python3 --version
   ```

2. **安装 Magneto**
   ```bash
   pip install magneto-cli
   ```

## 最简单的使用方式

### 1. 转换单个文件

```bash
magneto file.torrent
```

这将：
- 读取 `file.torrent` 文件
- 生成磁力链接
- 将结果保存到 `magnet_links.txt`

### 2. 转换文件夹中的所有文件

```bash
magneto folder/
```

这将：
- 搜索 `folder/` 目录中的所有 `.torrent` 文件
- 批量转换它们
- 将结果保存到 `folder/magnet_links.txt`

## 查看结果

转换完成后，您可以：

1. **查看输出文件**
   - 默认情况下，结果保存在 `magnet_links.txt` 文件中
   - 文件包含完整的转换信息

2. **使用标准输出**
   ```bash
   magneto folder/ --stdout
   ```
   结果将直接打印到终端

3. **仅获取链接**
   ```bash
   magneto folder/ --stdout -f links_only
   ```
   只输出磁力链接，方便复制使用

## 常用命令示例

### 递归搜索子目录

```bash
magneto folder/ -r
```

### 输出 JSON 格式

```bash
magneto folder/ -f json
```

### 包含 Tracker 信息

```bash
magneto folder/ --include-trackers
```

### 详细输出模式

```bash
magneto folder/ -v
```

## 下一步

- [安装指南](/zh/installation) - 了解详细的安装方法
- [使用指南](/zh/usage) - 学习更多高级功能
- [API 参考](/zh/api-reference) - 查看完整的 API 文档

