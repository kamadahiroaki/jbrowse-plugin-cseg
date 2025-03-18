![Integration](https://github.com/GMOD/jbrowse-plugin-template/workflows/Integration/badge.svg?branch=main)

# cseg

JBrowse 2のプラグインとして、VCFファイルから生成されたCSEGファイルを表示します。

## インストール方法

### 0. nodeのインストール

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt-get install -y nodejs
sudo npm install -g yarn
```

### 1. プラグインのインストール

```bash
# リポジトリのクローン
git clone https://github.com/kamadahiroaki/jbrowse-plugin-cseg.git
cd jbrowse-plugin-cseg

# プラグインのインストールとビルド
yarn install

# JBrowseのセットアップと起動
yarn setup
```

これにより：
- JBrowseがport:8999で起動
- プラグインがport:9000で動作
- localhost:8999でプラグイン込のJBrowseにアクセス可能

### 2. 周辺ツール環境のセットアップ（Docker）

VCFファイルの変換やデータベース作成などの周辺ツールはDockerで提供されています：

```bash
# Dockerイメージのビルド
docker-compose build
```

## データディレクトリ構造

CSEGプラグインは以下のディレクトリ構造でデータを管理します：

```
/data/
├── vcf/    # VCFファイルの保存場所
├── cseg/   # CSEGファイルの保存場所
└── db/     # データベースファイルの保存場所
```

これらのディレクトリは自動的に作成されます。デフォルトのデータルートディレクトリは`/data`ですが、環境変数`CSEG_DATA_ROOT`で変更できます。

## 基本的な使い方

### 1. データディレクトリの初期化

```bash
# デフォルトの場所（/data/）に初期化
docker-compose run --rm cseg-tools cseg-init

# カスタムデータディレクトリの指定
docker-compose run --rm cseg-tools cseg-init --data-root /path/to/data
```

### 2. VCFファイルからCSEGファイルの生成

```bash
# ファイルからの変換
docker-compose run --rm vcf2cseg input.vcf

# 標準入力からの変換
cat input.vcf | docker-compose run --rm vcf2cseg

# 出力ファイルの指定
docker-compose run --rm vcf2cseg input.vcf -o output.cseg

# カスタムデータディレクトリの使用
docker-compose run --rm vcf2cseg input.vcf --data-root /path/to/data
```

生成されたCSEGファイルは、デフォルトで`/data/cseg/`ディレクトリに保存されます。

### 3. データベースの作成

```bash
# デフォルトのデータベースファイル（/data/db/cseg.db）を作成
docker-compose run --rm create-db /data/cseg/input.cseg

# カスタムデータベースファイルの指定
docker-compose run --rm create-db /data/cseg/input.cseg --db /path/to/output.db

# カスタムデータディレクトリの使用
docker-compose run --rm create-db /data/cseg/input.cseg --data-root /path/to/data
```

### 4. Webサーバーの起動

```bash
# サーバーの起動（デフォルトポート：5000）
docker-compose up
```

サーバーは`http://localhost:5000`でアクセス可能です。
通常はJBrowseプラグインを通してアクセスします。

## JBrowseでの設定

### 1. プラグインの追加

既存のJBrowseインスタンスにプラグインを追加する場合：

```bash
jbrowse add-plugin @kamadahiroaki/jbrowse-plugin-cseg
```

または、`jbrowse.conf.json`に直接追加：

```json
{
  "plugins": [
    {
      "name": "@kamadahiroaki/jbrowse-plugin-cseg",
      "url": "https://unpkg.com/@kamadahiroaki/jbrowse-plugin-cseg/dist/jbrowse-plugin-cseg.umd.production.min.js"
    }
  ]
}
```

### 2. トラックの設定

CSEGトラックを表示するには、以下の設定を`tracks.conf`に追加します：

```json
{
  "type": "CSEGTrack",
  "name": "CSEG Data",
  "trackId": "cseg_track",
  "adapter": {
    "type": "CSEGAdapter",
    "csegEndpoint": "http://localhost:5000"
  }
}
```

## 環境変数

以下の環境変数で設定をカスタマイズできます：

- `CSEG_DATA_ROOT`: データディレクトリのルート（デフォルト：`/data`）
- `CSEG_VCF_DIR`: VCFファイルのディレクトリ名（デフォルト：`vcf`）
- `CSEG_CSEG_DIR`: CSEGファイルのディレクトリ名（デフォルト：`cseg`）
- `CSEG_DB_DIR`: データベースファイルのディレクトリ名（デフォルト：`db`）
- `CSEG_DB_NAME`: データベースファイル名（デフォルト：`cseg.db`）

## 開発環境のセットアップ

### 必要な環境

- Node.js 18以上
- Python 3.11以上
- Docker & Docker Compose
- C++コンパイラ（gcc/g++ 12以上）

### 開発サーバーの起動

```bash
# フロントエンド開発サーバー
yarn start

# バックエンドサーバー
docker-compose up
```

## トラブルシューティング

### データディレクトリのパーミッション

Dockerコンテナ内でデータディレクトリにアクセスできない場合は、以下のコマンドでパーミッションを設定してください：

```bash
sudo chown -R 1000:1000 /data
```

### ポート5000が使用中の場合

`docker-compose.yml`の`ports`セクションを編集して、別のポートを使用してください：

```yaml
ports:
  - "8000:5000"  # ホストの8000番ポートをコンテナの5000番ポートにマッピング
```

## ライセンス

MITライセンス
