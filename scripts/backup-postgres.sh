#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_DIR=$(dirname -- "$SCRIPT_DIR")
ENV_FILE=${1:-"$PROJECT_DIR/.env.production"}
BACKUP_DIR=${2:-"$PROJECT_DIR/backups"}

if [ ! -f "$ENV_FILE" ]; then
    echo "No existe el archivo de entorno: $ENV_FILE" >&2
    exit 1
fi

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
BACKUP_FILE="$BACKUP_DIR/estelart-$TIMESTAMP.dump"
PARTIAL_FILE="$BACKUP_FILE.partial"

cleanup() {
    rm -f -- "$PARTIAL_FILE"
}
trap cleanup EXIT INT TERM

docker compose \
    --env-file "$ENV_FILE" \
    -f "$PROJECT_DIR/docker-compose.prod.yml" \
    exec -T db sh -c \
    'pg_dump --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --format custom --no-owner --no-privileges' \
    > "$PARTIAL_FILE"

if [ ! -s "$PARTIAL_FILE" ]; then
    echo "La copia quedó vacía; no se conservará." >&2
    exit 1
fi

mv -- "$PARTIAL_FILE" "$BACKUP_FILE"
chmod 600 "$BACKUP_FILE"
trap - EXIT INT TERM

docker compose \
    --env-file "$ENV_FILE" \
    -f "$PROJECT_DIR/docker-compose.prod.yml" \
    exec -T db pg_restore --list < "$BACKUP_FILE" > /dev/null

echo "Copia creada y verificada: $BACKUP_FILE"
