
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

Ejemplos:

```txt
feature/productos-base
feature/clientes-base
feature/pedidos-base
fix/healthcheck-response
docs/git-workflow
chore/update-ci
test/productos-api
```
