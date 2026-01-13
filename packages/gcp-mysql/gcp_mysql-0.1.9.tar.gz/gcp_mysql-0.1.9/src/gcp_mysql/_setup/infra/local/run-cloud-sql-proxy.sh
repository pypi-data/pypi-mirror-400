#!/usr/bin/env bash
set -euo pipefail

#############################################
# OPTIONAL HARDCODED DEFAULTS (lowest priority)
#############################################
DEFAULT_PROJECT_ID=""
DEFAULT_REGION=""
DEFAULT_INSTANCE_NAME=""
DEFAULT_PORT="3306"
DEFAULT_BUILD_ENVIRONMENT="cli"
DEFAULT_DETACH="false"

#############################################
# USAGE
#############################################
usage() {
  cat <<EOF
Usage:
  $0 [options]

Options:
  --build-environment <cli|docker>   (default: cli)

  --project-id <project>
  --region <region>
  --instance-name <instance>
  --port <port>                      (default: 3306)

  --cloud-sql-instance <project:region:instance>
  --config <path-to-json>

Examples:
  $0 --project-id my-proj --region us-central1 --instance-name my-db
  $0 --cloud-sql-instance my-proj:us-central1:my-db
  $0 --config cloud-sql.json
  $0 --build-environment docker --config cloud-sql.json
EOF
  exit 1
}

#############################################
# DEPENDENCY CHECKS (conditional)
#############################################
require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "❌ Required command not found: $1"
    exit 1
  fi
}

#############################################
# ARG PARSING
#############################################
PROJECT_ID="$DEFAULT_PROJECT_ID"
REGION="$DEFAULT_REGION"
INSTANCE_NAME="$DEFAULT_INSTANCE_NAME"
PORT="$DEFAULT_PORT"
CLOUD_SQL_INSTANCE=""
CONFIG_FILE=""
BUILD_ENVIRONMENT="$DEFAULT_BUILD_ENVIRONMENT"
DETACH="$DEFAULT_DETACH"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --build-environment) BUILD_ENVIRONMENT="$2"; shift 2 ;;
    --project-id) PROJECT_ID="$2"; shift 2 ;;
    --region) REGION="$2"; shift 2 ;;
    --instance-name) INSTANCE_NAME="$2"; shift 2 ;;
    --port) PORT="$2"; shift 2 ;;
    --cloud-sql-instance) CLOUD_SQL_INSTANCE="$2"; shift 2 ;;
    --config) CONFIG_FILE="$2"; shift 2 ;;
    --detach) DETACH="true"; shift ;;
    -h|--help) usage ;;
    *) echo "Unknown arg: $1"; usage ;;
  esac
done

#############################################
# VALIDATE BUILD ENVIRONMENT
#############################################
if [[ "$BUILD_ENVIRONMENT" != "cli" && "$BUILD_ENVIRONMENT" != "docker" ]]; then
  echo "❌ Invalid --build-environment: $BUILD_ENVIRONMENT"
  echo "   Must be one of: cli, docker"
  exit 1
fi

#############################################
# CONFIG FILE (highest priority)
#############################################
if [[ -n "$CONFIG_FILE" ]]; then
  require_command jq

  if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
  fi

  PROJECT_ID=$(jq -r '.project_id' "$CONFIG_FILE")
  REGION=$(jq -r '.region' "$CONFIG_FILE")
  INSTANCE_NAME=$(jq -r '.instance_name' "$CONFIG_FILE")
  PORT=$(jq -r '.port // "3306"' "$CONFIG_FILE")
fi

#############################################
# CLOUD SQL INSTANCE STRING
#############################################
if [[ -n "$CLOUD_SQL_INSTANCE" ]]; then
  INSTANCE_CONN="$CLOUD_SQL_INSTANCE"
else
  if [[ -z "$PROJECT_ID" || -z "$REGION" || -z "$INSTANCE_NAME" ]]; then
    echo "❌ Missing required Cloud SQL identifiers."
    usage
  fi
  INSTANCE_CONN="${PROJECT_ID}:${REGION}:${INSTANCE_NAME}"
fi

#############################################
# AUTHENTICATION (shared)
#############################################
require_command gcloud

echo "🔐 Checking Application Default Credentials (ADC)..."

if gcloud auth application-default print-access-token >/dev/null 2>&1; then
  echo "✅ ADC already present — skipping browser login"
else
  echo "🔑 No valid ADC found — launching browser login"
  gcloud auth application-default login
fi

#############################################
# BUILD ENVIRONMENT EXECUTION
#############################################
echo
echo "🧱 Build environment: $BUILD_ENVIRONMENT"
echo "🗄️  Instance: $INSTANCE_CONN"
echo "🔌 Port:     $PORT"
echo

if [[ "$BUILD_ENVIRONMENT" == "cli" ]]; then
  require_command cloud-sql-proxy

  echo "🚀 Starting Cloud SQL Proxy (CLI)"
  echo "Connect using:"
  echo "  host=127.0.0.1 port=$PORT"
  echo
  echo "Press Ctrl+C to stop."
  echo

  cloud-sql-proxy "$INSTANCE_CONN" --port "$PORT"

else
  require_command docker

  if ! docker compose version >/dev/null 2>&1; then
    echo "❌ Docker Compose v2 not available."
    echo "   Please ensure Docker Desktop is installed and running."
    exit 1
  fi

  export CLOUD_SQL_INSTANCE="$INSTANCE_CONN"
  export CLOUD_SQL_PORT="$PORT"

  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  DOCKER_DIR="$SCRIPT_DIR/docker"

  if [[ ! -f "$DOCKER_DIR/docker-compose.yml" ]]; then
    echo "❌ docker-compose.yml not found in:"
    echo "   $DOCKER_DIR"
    exit 1
  fi

  echo "🐳 Starting Cloud SQL Proxy via Docker Compose"
  echo "📂 Directory: $DOCKER_DIR"
  echo

    (
    cd "$DOCKER_DIR"

    if [[ "$DETACH" == "true" ]]; then
        echo "🐳 Starting Cloud SQL Proxy via Docker Compose (detached)"
        docker compose up -d
        echo
        echo "✅ Cloud SQL Proxy running in background"
        echo "🔍 View logs:   docker compose logs -f"
        echo "🛑 Stop proxy: docker compose down"
    else
        echo "🐳 Starting Cloud SQL Proxy via Docker Compose (foreground)"
        docker compose up
    fi
    )
fi