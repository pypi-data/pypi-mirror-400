# 使用方法

このガイドでは、Magneto のすべての機能と使用方法について詳しく説明します。

## 基本的な使用方法

### 単一ファイルの変換

```bash
magneto file.torrent
```

### フォルダ内のすべてのファイルを変換

```bash
magneto folder/
```

### 出力ファイルの指定

```bash
magneto folder/ -o output.txt
```

## 出力形式

Magneto は3つの出力形式をサポートしています：

### 1. 完全形式（デフォルト）

```bash
magneto folder/ -f full
```

出力例：
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

### 2. リンクのみ形式

```bash
magneto folder/ -f links_only
```

出力例：
```
magnet:?xt=urn:btih:ABC123...&dn=Example
magnet:?xt=urn:btih:DEF456...&dn=Another
```

### 3. JSON形式

```bash
magneto folder/ -f json
```

出力例：
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

## 検索オプション

### 再帰検索

サブディレクトリ内のすべてのトーrentファイルを再帰的に検索：

```bash
magneto folder/ -r
```

### 大文字小文字を区別する検索

デフォルトでは、検索は大文字小文字を区別しません（`.torrent` と `.TORRENT` の両方が見つかります）。大文字小文字を区別する必要がある場合：

```bash
magneto folder/ --case-sensitive
```

## 変換オプション

### トラッカー情報を含める

デフォルトでは、生成されたマグネットリンクにはトラッカー情報が含まれません。含めるには：

```bash
magneto folder/ --include-trackers
```

生成されたマグネットリンクにはすべてのトラッカーアドレスが含まれます：
```
magnet:?xt=urn:btih:ABC123...&dn=Example&tr=http://tracker1.com&tr=http://tracker2.com
```

## 表示オプション

### 詳細出力モード

詳細な処理情報を表示：

```bash
magneto folder/ -v
```

出力には以下が含まれます：
- 各ファイルの Info Hash
- ファイル名
- トラッカーの数

### サイレントモード

エラーメッセージのみを表示：

```bash
magneto folder/ -q
```

### カラー出力を無効化

```bash
magneto folder/ --no-colors
```

## 出力方法

### ファイルに保存（デフォルト）

```bash
magneto folder/ -o output.txt
```

結果は指定されたファイルに保存されます。`-o` を指定しない場合、デフォルトで `magnet_links.txt` に保存されます。

### 標準出力に出力

```bash
magneto folder/ --stdout
```

結果はファイルに保存せず、端末に直接出力されます。

形式オプションと組み合わせて使用：

```bash
# リンクのみを端末に出力
magneto folder/ --stdout -f links_only

# JSONを端末に出力
magneto folder/ --stdout -f json
```

## 実用的な例

### 例1：一括変換してJSONとして保存

```bash
magneto downloads/ -r -f json -o results.json
```

### 例2：すべてのマグネットリンクをすばやく取得

```bash
magneto folder/ --stdout -f links_only -q
```

### 例3：トラッカーを含む詳細モード変換

```bash
magneto folder/ -v --include-trackers -o output.txt
```

### 例4：再帰検索してファイルに出力

```bash
magneto ~/Downloads/ -r -f full -o ~/magnets.txt
```

## コマンドライン引数リファレンス

### 位置引数

- `input` - 入力トーrentファイルまたはトーrentファイルを含むフォルダパス

### 出力オプション

- `-o, --output FILE` - 出力ファイルパスを指定（デフォルト：入力ディレクトリの `magnet_links.txt`）
- `-f, --format {full,links_only,json}` - 出力形式（デフォルト：full）
- `--stdout` - ファイルに保存せず、結果を標準出力に出力

### 検索オプション

- `-r, --recursive` - サブディレクトリ内のトーrentファイルを再帰的に検索
- `--case-sensitive` - ファイル拡張子の大文字小文字を区別する検索

### 変換オプション

- `--include-trackers` - マグネットリンクにトラッカー情報を含める

### 表示オプション

- `-v, --verbose` - 詳細な出力情報を表示
- `-q, --quiet` - サイレントモード、エラーメッセージのみを表示
- `--no-colors` - カラー出力を無効化

### その他のオプション

- `-h, --help` - ヘルプ情報を表示して終了
- `--version` - バージョン情報を表示して終了

## 使用のヒント

### 1. パイプ操作

出力を他のコマンドに渡す：

```bash
magneto folder/ --stdout -f links_only | grep "ABC123"
```

### 2. 大きなフォルダの一括処理

多くのファイルを含むフォルダの場合、サイレントモードを推奨：

```bash
magneto large_folder/ -r -q -f links_only -o results.txt
```

### 3. スクリプトでの使用

スクリプトではJSON形式を使用すると解析が容易：

```bash
magneto folder/ -f json -o results.json
# その後、Python/Node.jsなどでJSONを解析
```

## エラー処理

### 一般的なエラー

1. **ファイルが存在しない**
   ```
   Error: Path does not exist: /path/to/file
   ```

2. **ファイル形式エラー**
   ```
   ✗ example.torrent: Unable to parse torrent file
   ```

3. **権限エラー**
   ```
   Error: Unable to read file /path/to/file: Permission denied
   ```

### エラー統計

処理が完了すると、統計情報が表示されます：

```
================================================================================
Processing complete: 10 file(s) total
Success: 8
Failed: 2
================================================================================
```

## 次のステップ

- [API リファレンス](/ja/api-reference) - コードで Magneto を使用する方法を学ぶ
- [はじめに](/ja/getting-started) - 基本的な使用方法を確認
