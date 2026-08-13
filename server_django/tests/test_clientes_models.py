"""Tests para modelos de clientes."""

import pytest

from apps.clientes.models import Cliente


@pytest.mark.django_db
def test_cliente_str_devuelve_nombre_y_apellido() -> None:
    cliente = Cliente.objects.create(
        nombre="Ana",
        apellido="Gomez",
    )

    assert str(cliente) == "Ana Gomez"


@pytest.mark.django_db
def test_cliente_str_devuelve_razon_social_si_existe() -> None:
    cliente = Cliente.objects.create(
        nombre="Laura",
        apellido="Perez",
        razon_social="Creaciones Laura SRL",
    )

    assert str(cliente) == "Creaciones Laura SRL"


@pytest.mark.django_db
def test_cliente_se_crea_como_minorista_por_defecto() -> None:
    cliente = Cliente.objects.create(
        nombre="Sofia",
        apellido="Martinez",
    )

    assert cliente.tipo_cliente == Cliente.TipoCliente.MINORISTA
    assert cliente.activo is True


@pytest.mark.django_db
def test_cliente_puede_ser_mayorista() -> None:
    cliente = Cliente.objects.create(
        nombre="Carolina",
        apellido="Lopez",
        tipo_cliente=Cliente.TipoCliente.MAYORISTA,
        whatsapp="3764000000",
    )

    assert cliente.tipo_cliente == Cliente.TipoCliente.MAYORISTA
    assert cliente.whatsapp == "3764000000"
