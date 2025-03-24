![Integration](https://github.com/GMOD/jbrowse-plugin-template/workflows/Integration/badge.svg?branch=main)

# cseg

JBrowse 2のプラグインとして、VCFファイルから生成されたCSEGトラックを表示します。

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

## 初期セットアップ

Dockerコンテナのパーミッション問題を防ぐため、以下のいずれかの方法で`.env`ファイルを作成してください：

1. セットアップスクリプトを使用する場合（推奨）：
```bash
./setup.sh
```

2. 手動で作成する場合：
```bash
echo "UID=$(id -u)" > .env
echo "GID=$(id -g)" >> .env
```

この設定は各環境で一度だけ必要です。

## 基本的な使い方

### 1. データディレクトリの準備

全てのファイル操作は`data/`ディレクトリ内で行われます。
コマンド実行時は、このディレクトリがコンテナ内の`/data`にマウントされ、作業ディレクトリとして使用されます。

### 2. ビルド

```bash
docker-compose build
```

### 3. VCFファイルからCSEGファイルの生成

```bash
# VCFファイルをdata/ディレクトリに配置してから実行
docker-compose run --rm vcf2cseg input.vcf
#出力ファイル名はdata/input.cseg

#出力ファイル名を指定する場合
docker-compose run --rm vcf2cseg input.vcf -o output.cseg

# 標準入力を使用する場合（必要な場合のみ）
cat data/input.vcf | docker-compose run --rm vcf2cseg -T > data/output.cseg
```

### 4. データベースの作成

```bash
# CSEGファイルからデータベースを作成
docker-compose run --rm create-db input.cseg
#出力ファイル名はdata/input.db

#出力ファイル名を指定する場合
docker-compose run --rm create-db input.cseg -o output.db

# 標準入力を使用する場合（必要な場合のみ）
cat data/input.cseg | docker-compose run --rm create-db > data/output.db
```

注意：
- 入力ファイルは事前に`data/`ディレクトリに配置してください
- 出力ファイルは自動的に`data/`ディレクトリに生成されます
- コマンド実行時のファイル名指定では`data/`プレフィックスは不要です

### 5. Webサーバーの起動

```bash
# サーバーの起動（デフォルトポート：5000）
docker-compose up
```

サーバーは`http://localhost:5000`でアクセス可能です。
通常はJBrowseプラグインを通してアクセスします。

## JBrowseでの設定

### 1. トラックの設定

必要に応じて`jbrowse_config.json`を編集してください。
"uri": "http://localhost:5000?cseg=input"は`data/input.db`を表示します。

## 開発環境のセットアップ

### 必要な環境

- Node.js 20
- Python 3.11以上
- Docker & Docker Compose
- C++コンパイラ（gcc/g++ 12以上）