#!/bin/bash
if [ ! -f .env ]; then
    echo "Creating .env file with current user's UID and GID..."
    echo "UID=$(id -u)" > .env
    echo "GID=$(id -g)" >> .env
    echo ".env file created successfully"
else
    echo ".env file already exists"
fi
