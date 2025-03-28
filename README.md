![Integration](https://github.com/GMOD/jbrowse-plugin-template/workflows/Integration/badge.svg?branch=main)

# cseg

JBrowse 2のプラグインとして、VCFファイルから生成されたCSEGトラックを表示します。

## インストール方法

### 0. node,dockerのインストール

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt-get install -y nodejs
sudo npm install -g yarn
```

```bash
sudo curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo newgrp docker
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
docker compose build
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

### 1. データの準備

全てのファイル操作は`data/`ディレクトリ内で行われます。
コマンド実行時は、このディレクトリがコンテナ内の`/data`にマウントされ、作業ディレクトリとして使用されます。
```bash
yarn setup
```
で作成された`.jbrowse`ディレクトリに.faおよび.fa.faiファイルを配置してください。
医科研スパコンの/home/kamada/shared/にシャジクモのデータOPERA_SAMBA.faとOPERA_SAMBA.fa.faiがあります。
.vcfファイルは`data/`ディレクトリに配置してください。
merge1.02.GT.84.vcfが異常なSNPと個体を除外したデータです。
merge1.02.GT.84.correct6.vcfはさらに同じジェノタイプの連続回数が6回未満の箇所を欠損値扱いにしたデータで、シークエンスエラーと狭い範囲のミスアセンブリが修正されています。


### 2. ビルド

```bash
docker compose build
```

### 3. VCFファイルからCSEGファイルの生成

```bash
# VCFファイルをdata/ディレクトリに配置してから実行
docker compose run --rm vcf2cseg input.vcf
#出力ファイル名はdata/input.cseg

#出力ファイル名を指定する場合
docker compose run --rm vcf2cseg input.vcf -o output.cseg

# 標準入力を使用する場合（必要な場合のみ）
cat data/input.vcf | docker compose run --rm vcf2cseg -T > data/output.cseg
```

### 4. データベースの作成

```bash
# CSEGファイルからデータベースを作成
docker compose run --rm create-db input.cseg
#出力ファイル名はdata/input.db

#出力ファイル名を指定する場合
docker compose run --rm create-db input.cseg -o output.db

# 標準入力を使用する場合（必要な場合のみ）
cat data/input.cseg | docker compose run --rm create-db > data/output.db
```

注意：
- 入力ファイルは事前に`data/`ディレクトリに配置してください
- 出力ファイルは自動的に`data/`ディレクトリに生成されます
- コマンド実行時のファイル名指定では`data/`プレフィックスは不要です

### 5. Webサーバーの起動

```bash
# サーバーの起動（デフォルトポート：5000）
docker compose up
```

サーバーは`http://localhost:5000`でアクセス可能です。
通常はJBrowseプラグインを通してアクセスします。

### 6. JBrowseの起動

#### オプション1: デーモンモードで実行（推奨）

```bash
# サービスをバックグラウンドで起動
./start-daemon.sh

# サービスの停止
./stop-daemon.sh
```

サービスはバックグラウンドで実行され、ログは`logs/`ディレクトリに保存されます。
ログアウトしても実行は継続されます。

#### オプション2: フォアグラウンドで実行

```bash
# すべてのサービスを起動し、ログをリアルタイム表示
./start-all.sh
```

このスクリプトは、Docker Composeサービス、yarn browse、およびyarn startをすべて同時に起動します。
すべてのログは`logs/`ディレクトリに保存されます。Ctrl+Cを押してすべてのサービスを停止します。

#### オプション3: 手動でサービスを管理する

```bash
# Dockerサービスを起動
docker compose up

# 別の端末で
yarn browse

# 別の端末で
yarn start
```

## JBrowseでの設定

### カスタム設定ファイルの使用

異なる設定ファイルを使用する場合は、`CONFIG_FILE`環境変数を指定します：

```bash
# カスタム設定ファイルを使用
CONFIG_FILE=custom_config.json yarn browse

# デーモンモードで実行する場合
CONFIG_FILE=custom_config.json ./start-daemon.sh
```

### 1. トラックの設定

必要に応じて`jbrowse_config.json`を編集してください。
"uri": "http://localhost:5000?cseg=input"は`data/input.db`を表示します。
デフォルトではReference sequence (OPERA_SAMBA)とOriginal (merge1.02.GT.84)とCorrect6 (merge1.02.GT.84.correct6)の3つのトラックが設定されており、チェックを入れたものが表示されます。csegトラックの画像生成には時間がかかるため両方にチェックを入れると遅くなります。

## 開発環境のセットアップ

### 必要な環境

- Node.js 20
- Python 3.11以上
- Docker & Docker Compose
- C++コンパイラ（gcc/g++ 12以上）