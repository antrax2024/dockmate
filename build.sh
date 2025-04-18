#!/usr/bin/env bash

export DOCKER_HOST=ssh://antrax@192.168.1.16

docker compose up -d --build

echo "Removendo Imagens não utilizadas..."
docker image prune -a -f
echo "[OK]"
echo "Removendo Containers não utilizados..."
docker system prune -a -f
echo "[OK]"
