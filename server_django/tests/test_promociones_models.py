"""Tests para modelos de promociones."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.promociones.models import Promocion
from apps.productos.models import Categoria, Producto


@pytest.fixture(name="categoria")
def fixture_categoria() -> Categoria:
    """Categoria base para promociones."""

    return Categoria.objects.create(
        nombre="Limpiapipas",
        slug="limpiapipas",
    )


@pytest.fixture(name="producto")
def fixture_producto(categoria: Categoria) -> Producto:
    """Producto base para promociones."""

    return Producto.objects.create(
        categoria=categoria,
        sku="LIM-001",
        nombre="Limpiapipas surtidos",
        slug="limpiapipas-surtidos",
        precio_minorista=Decimal("1500.00"),
        precio_mayorista=Decimal("1200.00"),
        stock=50,
    )


@pytest.mark.django_db
def test_promocion_str_devuelve_nombre() -> None:
    ahora = timezone.now()

    promocion = Promocion.objects.create(
        nombre="Promo Primavera",
        slug="promo-primavera",
        tipo_promocion=Promocion.TipoPromocion.PORCENTAJE,
        porcentaje_descuento=Decimal("15.00"),
        fecha_inicio=ahora - timedelta(days=1),
        fecha_fin=ahora + timedelta(days=7),
    )

    assert str(promocion) == "Promo Primavera"


@pytest.mark.django_db
def test_promocion_vigente_devuelve_true_si_esta_activa_y_en_fecha() -> None:
    ahora = timezone.now()

    promocion = Promocion.objects.create(
        nombre="Promo vigente",
        slug="promo-vigente",
        tipo_promocion=Promocion.TipoPromocion.PORCENTAJE,
        porcentaje_descuento=Decimal("10.00"),
        fecha_inicio=ahora - timedelta(days=1),
        fecha_fin=ahora + timedelta(days=1),
        activa=True,
    )

    assert promocion.esta_vigente() is True


@pytest.mark.django_db
def test_promocion_vigente_devuelve_false_si_esta_inactiva() -> None:
    ahora = timezone.now()

    promocion = Promocion.objects.create(
        nombre="Promo inactiva",
        slug="promo-inactiva",
        tipo_promocion=Promocion.TipoPromocion.PORCENTAJE,
        porcentaje_descuento=Decimal("10.00"),
        fecha_inicio=ahora - timedelta(days=1),
        fecha_fin=ahora + timedelta(days=1),
        activa=False,
    )

    assert promocion.esta_vigente() is False


@pytest.mark.django_db
def test_promocion_puede_relacionarse_con_producto_y_categoria(
    categoria: Categoria,
    producto: Producto,
) -> None:
    ahora = timezone.now()

    promocion = Promocion.objects.create(
        nombre="Promo limpiapipas",
        slug="promo-limpiapipas",
        tipo_promocion=Promocion.TipoPromocion.MONTO_FIJO,
        monto_descuento=Decimal("500.00"),
        fecha_inicio=ahora - timedelta(days=1),
        fecha_fin=ahora + timedelta(days=3),
    )

    promocion.productos.add(producto)
    promocion.categorias.add(categoria)

    assert promocion.productos.count() == 1
    assert promocion.categorias.count() == 1
    assert producto.promociones.count() == 1
    assert categoria.promociones.count() == 1
