# ESTELART Platform

Sistema comercial para gestión de catálogo, carrito, pedidos, promociones, stock, clientes y reportes operativos para ESTELART.

La plataforma está pensada para ordenar el flujo de venta de productos de cotillón, insumos creativos, kits, artículos para emprendedores y pedidos mayoristas.

## Objetivo del sistema

ESTELART Platform centraliza en una sola solución las operaciones principales del negocio:

- Publicación de productos.
- Organización por categorías.
- Visualización de precios minoristas y mayoristas.
- Control de stock.
- Promociones activas.
- Armado de carrito.
- Creación de pedidos desde frontend.
- Registro de clientes.
- Panel operativo de pedidos.
- Reportes comerciales básicos.
- Validación y procesamiento de imágenes.
- Controles básicos de seguridad para uso real.

El objetivo no es solamente tener una web de presentación, sino una herramienta operativa para mejorar la administración comercial y reducir trabajo manual.

## Problema que resuelve

Antes de una plataforma de este tipo, el flujo comercial suele depender de canales dispersos:

- Consultas por WhatsApp.
- Publicaciones en redes sociales.
- Catálogos no centralizados.
- Control manual de stock.
- Pedidos escritos a mano.
- Falta de trazabilidad.
- Dificultad para saber qué productos se venden más.
- Dificultad para separar clientes minoristas y mayoristas.
- Imágenes no optimizadas para web.

ESTELART Platform busca resolver ese circuito con una base tecnológica propia, escalable y mantenible.

## Módulos principales

### Catálogo comercial

Permite visualizar productos activos con:

- Nombre.
- Categoría.
- SKU.
- Descripción.
- Precio minorista.
- Precio mayorista.
- Cantidad mínima mayorista.
- Stock.
- Estado destacado.
- Imágenes optimizadas.
- Galería de imágenes.
- Zoom visual sobre productos.

### Filtros y búsqueda

El catálogo permite:

- Buscar productos por texto.
- Filtrar por categoría.
- Ver solamente destacados.
- Visualizar cantidad de resultados.

Esto facilita el uso comercial diario y mejora la experiencia de compra.

### Carrito

El usuario puede:

- Agregar productos al carrito.
- Incrementar cantidades.
- Disminuir cantidades.
- Quitar productos.
- Ver subtotal por ítem.
- Ver total estimado del pedido.

### Checkout

El sistema permite crear pedidos reales desde el frontend solicitando:

- Nombre completo.
- Email.
- WhatsApp.
- Notas del pedido.
- Productos seleccionados.

El frontend envía el pedido al backend mediante API.

### Pedidos

El backend crea:

- Cliente.
- Pedido.
- Detalle de pedido.
- Código único de pedido.
- Estado inicial pendiente.
- Estado de pago pendiente.
- Canal de venta web.

Los precios no son enviados como fuente de verdad desde el frontend. El backend calcula los importes usando los precios registrados en base de datos.

### Panel operativo

El panel de administración permite gestionar pedidos con:

- Filtros por estado.
- Filtros por estado de pago.
- Filtros por canal.
- Búsqueda por código, cliente, email o WhatsApp.
- Vista de detalle de productos del pedido.
- Cantidad de ítems.
- Cantidad de unidades.
- Total del pedido.
- Confirmación transaccional con reserva de stock.
- Reposición automática de stock al cancelar una confirmación.
- Transiciones controladas de pedido y de pago.
- Reembolso obligatorio antes de cancelar pedidos cobrados.
- Historial inmutable con usuario, fecha y comentario.

La API interna expone listados paginados con búsqueda y filtros, además de las
operaciones explícitas:

- `POST /api/v1/pedidos/{id}/cambiar-estado/`
- `POST /api/v1/pedidos/{id}/cambiar-estado-pago/`

Los estados no se editan directamente. La API y las acciones masivas de Django
Admin pasan por el mismo servicio transaccional para evitar sobreventa y cambios
sin trazabilidad.

### Reportes comerciales

El sistema incluye un endpoint interno protegido con métricas básicas:

- Total de pedidos.
- Pedidos pendientes.
- Total estimado vendido.
- Unidades pedidas.
- Productos activos.
- Productos con stock bajo.
- Categorías activas.
- Promociones activas.
- Pedidos por estado.
- Pedidos por canal.
- Top productos pedidos.
- Productos con stock bajo.

### Imágenes de producto

El sistema permite administrar imágenes de producto con:

- Validación de extensión.
- Validación de contenido real.
- Límite de tamaño.
- Límite de píxeles.
- Conversión a formato web optimizado.
- Generación de thumbnail.
- Marca de agua simple.
- Galería por producto.
- Fallback cuando no hay imagen disponible.

### Gestión interna del catálogo

Los operadores y administradores autenticados disponen de una API separada del
catálogo público:

- `GET|POST|PATCH /api/v1/gestion/categorias/`
- `GET|POST|PATCH /api/v1/gestion/productos/`
- `GET|POST|PATCH|DELETE /api/v1/gestion/imagenes-producto/`

Las listas internas están paginadas y permiten búsqueda, orden y filtros por
estado, categoría, disponibilidad de stock y productos destacados. Los slugs se
generan automáticamente, los SKU se normalizan y los precios respetan las
reglas minorista/mayorista. Productos y categorías se desactivan mediante
`PATCH` para preservar el historial comercial; las imágenes sí se pueden
eliminar junto con sus archivos derivados.

## Seguridad aplicada

El sistema incluye controles básicos de seguridad para uso profesional:

- Uso de Django ORM para evitar SQL crudo.
- Serializers de Django REST Framework para validación de entrada.
- Endpoint público de pedidos con validaciones.
- El backend no confía en precios enviados desde frontend.
- Rate limit para creación pública de pedidos.
- Endpoints administrativos protegidos.
- Reportes protegidos para usuarios administradores.
- Validación defensiva de imágenes.
- Argon2 como hasher principal de contraseñas Django.
- Variables sensibles fuera del código fuente.
- Archivo SECURITY.md con revisión de seguridad.
- Script automatizado de seguridad.
- Auditoría de dependencias backend y frontend.

## Auditoría de seguridad

El proyecto incluye:

```powershell
.\scripts\security-check.ps1

Este script ejecuta:

Búsqueda de SQL crudo en código propio.
manage.py check --deploy.
pip-audit para dependencias Python.
pnpm audit para dependencias frontend.

Resultado esperado en desarrollo local:

Sin SQL crudo detectado.
Sin vulnerabilidades conocidas en dependencias.
Warnings esperados de Django por configuración local: DEBUG activo, HTTPS desactivado, cookies secure desactivadas y SECRET_KEY de desarrollo.

Los warnings de producción deben resolverse con variables de entorno reales en despliegue.

Stack técnico
Backend
Python
Django
Django REST Framework
PostgreSQL
Pillow
Pytest
Pylint
Mypy
Black
Frontend
React
TypeScript
Vite
Tailwind CSS
Vitest
React Testing Library
ESLint
Infraestructura
Docker
Docker Compose
GitHub Actions
PostgreSQL en contenedor
Scripts de validación local
Hooks pre-push
Estructura general
client/
  src/
    features/
      carrito/
      catalogo/
      pedidos/


server_django/
  apps/
    clientes/
    core/
    pedidos/
    productos/
    promociones/
  config/
  tests/


scripts/
  check-local.ps1
  security-check.ps1


.github/
  workflows/
    ci.yml
Ejecución local
Backend
cd server_django


.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_catalogo
.\.venv\Scripts\python.exe manage.py runserver

API local:

http://localhost:8000/api/v1/

Admin local:

http://localhost:8000/admin/
Frontend
cd client


pnpm install
pnpm dev

Frontend local:

http://localhost:5173/
Docker Compose
docker compose up --build

Servicios:

Frontend: http://localhost:5173/
Backend:  http://localhost:8000/
Admin:    http://localhost:8000/admin/
Postgres: localhost:5432
Validaciones locales

Antes de integrar cambios:

.\scripts\check-local.ps1

Este script ejecuta:

Black.
Pylint.
Mypy.
Pytest con coverage.
ESLint.
Vitest.
Build frontend.
Validación de Docker Compose.

Auditoría de seguridad:

.\scripts\security-check.ps1

## Despliegue de producción

La composición de producción usa Nginx para servir el frontend compilado y
actuar como proxy de la API, Gunicorn para Django y PostgreSQL como base de
datos. Los secretos no se incluyen en la imagen ni en el repositorio.

1. Copiar `.env.production.example` a `.env.production`.
2. Reemplazar el dominio, la clave de Django y la contraseña de PostgreSQL.
3. Terminar TLS/HTTPS en el balanceador o proxy externo antes de habilitar
   HSTS.
4. Iniciar el stack:

```powershell
docker compose --env-file .env.production -f docker-compose.prod.yml up --build -d
```

5. Verificar `https://<dominio>/api/v1/health/` y revisar los logs:

```powershell
docker compose --env-file .env.production -f docker-compose.prod.yml ps
docker compose --env-file .env.production -f docker-compose.prod.yml logs --tail 100
```

Los archivos multimedia continúan en un volumen Docker. Antes de escalar a
múltiples instancias se debe migrar ese almacenamiento a un servicio compatible
con S3 y configurar copias de seguridad de PostgreSQL.
## Estado actual del sistema

El sistema cuenta con:

- Backend funcional.
- Frontend funcional.
- Catálogo conectado a API.
- Carrito operativo.
- Checkout conectado al backend.
- Creación real de pedidos.
- Panel administrativo de pedidos.
- Reportes internos.
- Seguridad básica aplicada.
- Branding visual ESTELART.
- Validaciones locales completas.
- Pipeline CI/CD configurado.
- Autenticación, perfiles e historial de pedidos de clientes.
- Gestión interna de categorías, productos, precios, stock e imágenes.

## Próximas mejoras posibles

- Integración con WhatsApp.
- Exportación de pedidos a Excel.
- Dashboard visual de reportes.
- Segmentación de clientes.
- Descuentos automáticos por volumen.
- Integración con medios de pago.
- Publicación o sincronización con canales externos.
- Despliegue productivo con dominio real, HTTPS y storage externo.

## Valor comercial

ESTELART Platform transforma una operación comercial dispersa en un sistema centralizado, medible y escalable.

No es solamente una página web. Es una base tecnológica para ordenar ventas, reducir trabajo manual, mejorar seguimiento de pedidos y preparar el negocio para futuras automatizaciones.
