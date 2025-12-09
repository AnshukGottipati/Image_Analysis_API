#!/usr/bin/env bash
set -e

APP_NAME="image-analysis-api"
IMAGE_NAME="image-analysis-api:latest"
APP_PORT=8000        # host port
CONTAINER_PORT=8000  # container port (matches Dockerfile)

echo "=== [1/4] Installing Docker if needed ==="
if ! command -v docker >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y docker.io
else
  echo "Docker already installed, skipping."
fi

echo "=== [2/4] Building Docker image ==="
sudo docker build -t "${IMAGE_NAME}" .

echo "=== [3/4] Stopping/removing old container (if any) ==="
sudo docker rm -f "${APP_NAME}" >/dev/null 2>&1 || true

echo "=== [4/4] Running new container ==="

ENV_FILE_ARG=""
if [ -f ".env" ]; then
  echo "Using .env file for environment variables."
  ENV_FILE_ARG="--env-file .env"
else
  echo "WARNING: .env not found. Make sure AZURE_ENDPOINT and AZURE_KEY are set some other way."
fi

sudo docker run -d \
  --name "${APP_NAME}" \
  -p ${APP_PORT}:${CONTAINER_PORT} \
  ${ENV_FILE_ARG} \
  "${IMAGE_NAME}"

echo "----------------------------------------------------"
echo "Container '${APP_NAME}' is running."
echo "API should be reachable at: http://YOUR_DROPLET_IP:${APP_PORT}/docs"
echo
echo "Useful commands:"
echo "  sudo docker ps"
echo "  sudo docker logs -f ${APP_NAME}"
echo "  sudo docker restart ${APP_NAME}"
echo "  sudo docker rm -f ${APP_NAME}"
echo "----------------------------------------------------"
