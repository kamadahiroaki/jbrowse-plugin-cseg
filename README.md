# JBrowse CSEG Plugin

JBrowse 2プラグインとPythonバックエンドを含むCSEGビジュアライゼーションツール。

## インストール方法

### 1. インストール

```bash
git clone git@github.com:kamadahiroaki/jbrowse-plugin-cseg.git
cd jbrowse-plugin-cseg
yarn install
yarn setup
pip install .
```

### 2. Pythonパッケージのインストール

```bash
pip install jbrowse-plugin-cseg
```

### 3. Docker Installation

To run the plugin using Docker:

1. Make sure you have Docker and Docker Compose installed on your system.

2. Build and start the container:
```bash
docker-compose up --build
```

3. The development server will be available at http://localhost:5000

To rebuild the plugin after making changes:
```bash
docker-compose exec jbrowse-plugin-cseg yarn build
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
