# JBrowse CSEG Plugin

JBrowse 2プラグインとPythonバックエンドを含むCSEGビジュアライゼーションツール。

## インストール方法

### 0. nodeのインストール

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt-get install -y nodejs
sudo npm install -g yarn
```

### 1. インストール

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

# cseg-serverの起動（バックグラウンド実行）
docker-compose up -d
```

## 使用方法

### 1. CSEGデータベースの作成

VCFファイルからCSEGデータベースを作成：

```bash
# VCFファイルの変換
docker-compose run --rm vcf2cseg [入力VCFファイル] [出力CSEGファイル]

# データベースの作成
docker-compose run --rm create-db [入力CSEGファイル] [出力DBファイル]
```

### 2. サーバーの操作

```bash
# サーバーの起動
docker-compose up -d

# サーバーの停止
docker-compose down

# ログの確認
docker-compose logs -f
```

### 3. データの配置

データファイルは`./data`ディレクトリに配置することを推奨します：

```
./data/
  ├── vcf/      # 入力VCFファイル
  ├── cseg/     # 変換後のCSEGファイル
  └── db/       # 作成したデータベースファイル
```

## 開発環境

- Python 3.7以上
- Node.js
- C++17対応コンパイラ
- Docker & Docker Compose（周辺ツール用）

## ライセンス

MITライセンス
