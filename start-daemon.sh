#!/bin/bash

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# PIDファイルの設定
PID_DIR="$SCRIPT_DIR/run"
mkdir -p "$PID_DIR"
PID_FILE="$PID_DIR/services.pid"

# ログディレクトリの作成
mkdir -p logs

# 既存のプロセスをチェック
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Services are already running (PID: $OLD_PID)"
        echo "To stop: ./stop-daemon.sh"
        exit 1
    else
        rm "$PID_FILE"
    fi
fi

# 現在の環境変数を保存
ENV_FILE="$PID_DIR/environment"
env | grep -E '^(CONFIG_FILE)=' > "$ENV_FILE"

# nohupで実行してバックグラウンドに移行
nohup bash -c '
    # 環境変数を復元
    if [ -f "'$ENV_FILE'" ]; then
        source "'$ENV_FILE'"
    fi

    # Docker Composeサービスの起動
    docker compose up > logs/docker.log 2>&1 &
    DOCKER_PID=$!

    # yarn browseの起動（少し待ってから）
    sleep 5
    yarn browse > logs/browse.log 2>&1 &
    YARN_BROWSE_PID=$!

    # yarn startの起動
    yarn start > logs/start.log 2>&1 &
    YARN_START_PID=$!

    # PIDの保存
    echo "$DOCKER_PID $YARN_BROWSE_PID $YARN_START_PID" > '"$PID_FILE"'

    # プロセスの監視
    wait $DOCKER_PID $YARN_BROWSE_PID $YARN_START_PID
' > logs/nohup.log 2>&1 &

echo "Services started in daemon mode"
echo "PID file: $PID_FILE"
echo "Logs directory: $SCRIPT_DIR/logs"
echo "To stop: ./stop-daemon.sh"
