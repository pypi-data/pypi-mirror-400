# はじめに

このガイドは、Magneto をすぐに使い始めるのに役立ちます。わずか数分で、トーrentファイルの一括変換を開始できます。

## 前提条件

始める前に、以下を確認してください：

1. **Python 3.7+ がインストールされている**
   ```bash
   python --version
   # または
   python3 --version
   ```

2. **Magneto がインストールされている**
   ```bash
   pip install magneto-cli
   ```

## 最も簡単な使用方法

### 1. 単一ファイルの変換

```bash
magneto file.torrent
```

これにより：
- `file.torrent` ファイルを読み取る
- マグネットリンクを生成
- 結果を `magnet_links.txt` に保存

### 2. フォルダ内のすべてのファイルを変換

```bash
magneto folder/
```

これにより：
- `folder/` ディレクトリ内のすべての `.torrent` ファイルを検索
- それらを一括変換
- 結果を `folder/magnet_links.txt` に保存

## 結果の確認

変換後、以下を実行できます：

1. **出力ファイルを確認**
   - デフォルトでは、結果は `magnet_links.txt` ファイルに保存されます
   - ファイルには完全な変換情報が含まれます

2. **標準出力を使用**
   ```bash
   magneto folder/ --stdout
   ```
   結果が端末に直接出力されます

3. **リンクのみを取得**
   ```bash
   magneto folder/ --stdout -f links_only
   ```
   マグネットリンクのみを出力し、コピーに便利

## 一般的なコマンド例

### 再帰検索

```bash
magneto folder/ -r
```

### JSON形式で出力

```bash
magneto folder/ -f json
```

### トラッカー情報を含める

```bash
magneto folder/ --include-trackers
```

### 詳細出力モード

```bash
magneto folder/ -v
```

## 次のステップ

- [インストールガイド](/ja/installation) - 詳細なインストール方法を学ぶ
- [使用ガイド](/ja/usage) - より高度な機能を学ぶ
- [API リファレンス](/ja/api-reference) - 完全な API ドキュメントを表示
