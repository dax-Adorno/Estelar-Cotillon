# Flujo de trabajo Git - ESTELART Cotillón

Este proyecto utiliza un flujo profesional basado en ramas cortas, validaciones locales y CI/CD.

## Rama principal

La rama `main` representa el estado estable del proyecto.

No se debe trabajar directamente sobre `main`.

## Ramas de trabajo

Cada cambio debe realizarse en una rama específica:

- `feature/nombre-funcionalidad`
- `fix/nombre-del-arreglo`
- `docs/nombre-documentacion`
- `chore/nombre-tarea-tecnica`
- `test/nombre-tests`

## Flujo recomendado

1. Actualizar `main`.
2. Crear una rama nueva.
3. Trabajar y validar localmente.
4. Confirmar cambios.
5. Subir la rama.
6. Crear Pull Request.
7. Esperar que pase CI/CD.
8. Integrar a `main`.

## Validaciones locales

Antes de cada `push`, el proyecto ejecuta automáticamente el hook `pre-push`.

Este hook valida backend, frontend y Docker Compose.

## CI/CD

GitHub Actions valida automáticamente:

- Backend quality checks
- Frontend quality checks
- Docker compose validation

## Regla principal

No se integra código a `main` si las validaciones locales o el CI/CD fallan.