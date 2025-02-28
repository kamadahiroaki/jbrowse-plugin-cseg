# JBrowse CSEG Plugin

JBrowse 2プラグインとPythonバックエンドを含むCSEGビジュアライゼーションツール。

## インストール方法

### 1. npmパッケージのインストール

```bash
npm install @jbrowse/plugin-cseg
```

### 2. Pythonパッケージのインストール

```bash
pip install jbrowse-plugin-cseg
```

## 使用方法

### 1. CSEGデータベースの作成

```bash
cseg-create-db input.cseg
```

これにより`input.db`が作成されます。

### 2. サーバーの起動

```bash
cseg-server
```

サーバーがlocalhost:5000で起動します。

### 3. JBrowseの設定

JBrowseの設定ファイルに以下を追加：

```json
{
  "plugins": [
    {
      "name": "CSEG",
      "url": "http://localhost:5000"
    }
  ]
}
```

## 要件

- Python >= 3.7
- C++11対応コンパイラ
- Node.js >= 14

## ライセンス

MITライセンス
