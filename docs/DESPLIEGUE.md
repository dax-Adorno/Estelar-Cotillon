# Operación y despliegue de ESTELART

Esta guía cubre un despliegue productivo de una sola instancia con Docker
Compose. La arquitectura separa Nginx, Django/Gunicorn y PostgreSQL, conserva
los datos en volúmenes y no publica PostgreSQL ni Gunicorn directamente.

## Requisitos

- Servidor Linux con Docker Engine y Docker Compose v2.
- Dominio apuntando al servidor.
- Proxy o balanceador con certificado TLS válido delante del puerto de la app.
- Almacenamiento externo para guardar copias fuera del propio servidor.

## Preparación

1. Copiar `.env.production.example` como `.env.production`.
2. Sustituir todos los valores `replace-with-*` y el dominio de ejemplo.
3. Generar `DJANGO_SECRET_KEY` con al menos 50 caracteres aleatorios.
4. Restringir el firewall a SSH, HTTP y HTTPS. PostgreSQL no debe exponerse.
5. Validar la configuración antes de iniciar:

```sh
docker compose --env-file .env.production -f docker-compose.prod.yml config --quiet
```

## Inicio y verificación

```sh
docker compose --env-file .env.production -f docker-compose.prod.yml up --build -d
docker compose --env-file .env.production -f docker-compose.prod.yml ps
docker compose --env-file .env.production -f docker-compose.prod.yml logs --tail 100
```

La comprobación `/api/v1/health/` confirma que el proceso responde. La ruta
`/api/v1/health/ready/` también comprueba la conexión con PostgreSQL y es la
que utiliza Docker para decidir si Django puede recibir tráfico.

Validación externa:

```sh
curl --fail https://tienda.example.com/api/v1/health/
curl --fail https://tienda.example.com/api/v1/health/ready/
```

## Copias de seguridad

El script genera un dump en formato PostgreSQL custom, comprueba que puede
leerse y asigna permisos exclusivos al operador:

```sh
sh scripts/backup-postgres.sh .env.production backups
```

Copiar el archivo resultante a un destino externo cifrado y aplicar allí una
política de retención. Una copia que permanece únicamente en el servidor no
protege frente a la pérdida de esa máquina.

Antes de una restauración, detener escrituras y ensayar el archivo en un
entorno separado. La siguiente operación reemplaza objetos de la base elegida:

```sh
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T db \
  sh -c 'pg_restore --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --clean --if-exists' \
  < backups/estelart-FECHA.dump
```

## Actualización segura

1. Crear y verificar una copia de PostgreSQL.
2. Descargar la versión aprobada del repositorio.
3. Construir las imágenes y ejecutar migraciones mediante el arranque normal.
4. Esperar a que los tres servicios aparezcan `healthy`.
5. Probar login, catálogo, carrito, checkout y panel interno.
6. Conservar la versión anterior hasta terminar la verificación.

## Límite de escalabilidad

El volumen `estelart_media` es adecuado para una sola instancia. Antes de usar
varias réplicas de Django/Nginx, las imágenes deben migrarse a almacenamiento
de objetos compatible con S3. PostgreSQL debe pasar a un servicio administrado
o a una arquitectura con copias automáticas, monitoreo y recuperación probada.
