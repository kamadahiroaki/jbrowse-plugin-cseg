#!/bin/bash

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PID_FILE="$SCRIPT_DIR/run/services.pid"

# 使用中のポートを解放する関数
kill_port_process() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo "Killing process using port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null
    fi
}

echo "Stopping services..."

# PIDファイルからプロセスを終了
if [ -f "$PID_FILE" ]; then
    read -r DOCKER_PID YARN_BROWSE_PID YARN_START_PID < "$PID_FILE"
    
    # プロセスの終了
    kill $DOCKER_PID 2>/dev/null
    kill $YARN_BROWSE_PID 2>/dev/null
    kill $YARN_START_PID 2>/dev/null
    
    # PIDファイルの削除
    rm "$PID_FILE"
fi

# 使用中のポートを確認して解放
echo "Checking for remaining processes..."
kill_port_process 8999  # yarn browse用ポート
kill_port_process 9000  # yarn start用ポート
kill_port_process 5000  # Docker Compose用ポート

# Docker Composeのコンテナを停止
echo "Stopping Docker containers..."
cd "$SCRIPT_DIR"
docker compose down 2>/dev/null

echo "Services stopped"
