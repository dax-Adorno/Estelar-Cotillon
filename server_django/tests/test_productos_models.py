"""Tests para modelos de productos."""

from decimal import Decimal

import pytest

from apps.productos.models import Categoria, Producto


@pytest.mark.django_db
def test_categoria_str_devuelve_nombre() -> None:
    categoria = Categoria.objects.create(
        nombre="Limpiapipas",
        slug="limpiapipas",
    )

    assert str(categoria) == "Limpiapipas"


@pytest.mark.django_db
def test_producto_str_devuelve_sku_y_nombre() -> None:
    categoria = Categoria.objects.create(
        nombre="Kits creativos",
        slug="kits-creativos",
    )

    producto = Producto.objects.create(
        categoria=categoria,
        sku="KIT-001",
        nombre="Kit slime inicial",
        slug="kit-slime-inicial",
        precio_minorista=Decimal("2500.00"),
        precio_mayorista=Decimal("2000.00"),
        cantidad_minima_mayorista=10,
        stock=25,
    )

    assert str(producto) == "KIT-001 - Kit slime inicial"


@pytest.mark.django_db
def test_producto_pertenece_a_una_categoria() -> None:
    categoria = Categoria.objects.create(
        nombre="Bijou",
        slug="bijou",
    )

    producto = Producto.objects.create(
        categoria=categoria,
        sku="BIJ-001",
        nombre="Mostacillas surtidas",
        slug="mostacillas-surtidas",
        precio_minorista=Decimal("1200.00"),
        precio_mayorista=Decimal("950.00"),
        stock=100,
    )

    assert producto.categoria == categoria
    assert categoria.productos.count() == 1
