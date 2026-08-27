"""Pruebas de gestion y aplicacion segura de promociones."""

# pylint: disable=duplicate-code

from datetime import timedelta
from decimal import Decimal
from typing import Any

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.clientes.models import Cliente, PerfilUsuario
from apps.pedidos.models import Pedido
from apps.productos.models import Categoria, Producto
from apps.promociones.models import ItemComboPromocion, Promocion
from apps.promociones.services import LineaPromocion, calcular_mejor_promocion


@pytest.fixture(name="api_client")
def fixture_api_client() -> APIClient:
    return APIClient()


@pytest.fixture(name="operator_user")
def fixture_operator_user() -> Any:
    usuario = get_user_model().objects.create_user(
        username="promociones@example.com",
        email="promociones@example.com",
        password="test-password",
    )
    PerfilUsuario.objects.create(
        usuario=usuario,
        rol=PerfilUsuario.Rol.OPERADOR,
    )
    return usuario


@pytest.fixture(name="customer_user")
def fixture_customer_user() -> Any:
    usuario = get_user_model().objects.create_user(
        username="cliente-promo@example.com",
        email="cliente-promo@example.com",
        password="test-password",
    )
    PerfilUsuario.objects.create(
        usuario=usuario,
        rol=PerfilUsuario.Rol.CLIENTE_MINORISTA,
    )
    return usuario


@pytest.fixture(name="categoria")
def fixture_categoria() -> Categoria:
    return Categoria.objects.create(nombre="Fiesta", slug="fiesta")


@pytest.fixture(name="producto")
def fixture_producto(categoria: Categoria) -> Producto:
    return Producto.objects.create(
        categoria=categoria,
        sku="FIE-001",
        nombre="Kit fiesta",
        slug="kit-fiesta",
        precio_minorista=Decimal("100.00"),
        precio_mayorista=Decimal("80.00"),
        cantidad_minima_mayorista=5,
        stock=100,
    )


def fechas_vigentes() -> tuple[Any, Any]:
    ahora = timezone.now()
    return ahora - timedelta(hours=1), ahora + timedelta(days=7)


def crear_promocion(
    *,
    nombre: str,
    slug: str,
    porcentaje: Decimal | None = None,
    monto: Decimal | None = None,
    tipo: str = Promocion.TipoPromocion.PORCENTAJE,
    canal: str = Promocion.CanalVenta.TODOS,
    compra_minima: Decimal | None = None,
) -> Promocion:
    inicio, fin = fechas_vigentes()
    return Promocion.objects.create(
        nombre=nombre,
        slug=slug,
        tipo_promocion=tipo,
        porcentaje_descuento=porcentaje,
        monto_descuento=monto,
        compra_minima=compra_minima,
        canal_venta=canal,
        fecha_inicio=inicio,
        fecha_fin=fin,
    )


def payload_checkout(producto: Producto, cantidad: int = 2) -> dict[str, Any]:
    return {
        "nombre_completo": "Cliente Promocion",
        "email": "checkout-promo@example.com",
        "whatsapp": "0981555000",
        "items": [{"producto_id": producto.pk, "cantidad": cantidad}],
    }


@pytest.mark.django_db
@pytest.mark.parametrize("autenticado", (False, True))
def test_gestion_promociones_exige_rol_interno(
    api_client: APIClient,
    customer_user: Any,
    autenticado: bool,
) -> None:
    if autenticado:
        api_client.force_authenticate(user=customer_user)

    response = api_client.get(reverse("gestion-promociones-list"))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_operador_crea_promocion_con_slug_automatico(
    api_client: APIClient,
    operator_user: Any,
    producto: Producto,
) -> None:
    inicio, fin = fechas_vigentes()
    api_client.force_authenticate(user=operator_user)

    response = api_client.post(
        reverse("gestion-promociones-list"),
        {
            "nombre": "  Semana de la fiesta  ",
            "tipo_promocion": Promocion.TipoPromocion.PORCENTAJE,
            "porcentaje_descuento": "15.00",
            "monto_descuento": None,
            "canal_venta": Promocion.CanalVenta.WEB,
            "productos": [producto.pk],
            "fecha_inicio": inicio,
            "fecha_fin": fin,
            "activa": True,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["nombre"] == "Semana de la fiesta"
    assert response.data["slug"] == "semana-de-la-fiesta"
    assert response.data["productos"] == [producto.pk]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "reemplazos,campo_error",
    (
        (
            {"porcentaje_descuento": "10.00", "monto_descuento": "50.00"},
            "porcentaje_descuento",
        ),
        (
            {"porcentaje_descuento": None, "monto_descuento": None},
            "porcentaje_descuento",
        ),
    ),
)
def test_gestion_rechaza_valores_de_descuento_ambiguos(
    api_client: APIClient,
    operator_user: Any,
    reemplazos: dict[str, Any],
    campo_error: str,
) -> None:
    inicio, fin = fechas_vigentes()
    payload = {
        "nombre": "Promo invalida",
        "tipo_promocion": Promocion.TipoPromocion.PORCENTAJE,
        "porcentaje_descuento": "10.00",
        "fecha_inicio": inicio,
        "fecha_fin": fin,
    }
    payload.update(reemplazos)
    api_client.force_authenticate(user=operator_user)

    response = api_client.post(
        reverse("gestion-promociones-list"),
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert campo_error in response.data


@pytest.mark.django_db
def test_gestion_rechaza_rango_de_fechas_invalido(
    api_client: APIClient,
    operator_user: Any,
) -> None:
    ahora = timezone.now()
    api_client.force_authenticate(user=operator_user)

    response = api_client.post(
        reverse("gestion-promociones-list"),
        {
            "nombre": "Fechas invalidas",
            "tipo_promocion": Promocion.TipoPromocion.PORCENTAJE,
            "porcentaje_descuento": "10.00",
            "fecha_inicio": ahora,
            "fecha_fin": ahora - timedelta(days=1),
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "fecha_fin" in response.data


@pytest.mark.django_db
def test_operador_crea_combo_con_cantidades(
    api_client: APIClient,
    operator_user: Any,
    producto: Producto,
) -> None:
    inicio, fin = fechas_vigentes()
    api_client.force_authenticate(user=operator_user)

    response = api_client.post(
        reverse("gestion-promociones-list"),
        {
            "nombre": "Combo doble",
            "tipo_promocion": Promocion.TipoPromocion.COMBO,
            "monto_descuento": "20.00",
            "fecha_inicio": inicio,
            "fecha_fin": fin,
            "items_combo": [{"producto": producto.pk, "cantidad": 2}],
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    promocion = Promocion.objects.get(pk=response.data["id"])
    item = promocion.items_combo.get()
    assert item.producto == producto
    assert item.cantidad == 2
    assert list(promocion.productos.all()) == [producto]

    cambio = api_client.patch(
        reverse("gestion-promociones-detail", kwargs={"pk": promocion.pk}),
        {
            "tipo_promocion": Promocion.TipoPromocion.PORCENTAJE,
            "porcentaje_descuento": "10.00",
            "monto_descuento": None,
        },
        format="json",
    )
    assert cambio.status_code == status.HTTP_200_OK
    assert promocion.items_combo.exists() is False


@pytest.mark.django_db
def test_combo_exige_items_sin_duplicados(
    api_client: APIClient,
    operator_user: Any,
    producto: Producto,
) -> None:
    inicio, fin = fechas_vigentes()
    api_client.force_authenticate(user=operator_user)
    base = {
        "nombre": "Combo invalido",
        "tipo_promocion": Promocion.TipoPromocion.COMBO,
        "monto_descuento": "20.00",
        "fecha_inicio": inicio,
        "fecha_fin": fin,
    }

    sin_items = api_client.post(
        reverse("gestion-promociones-list"),
        base,
        format="json",
    )
    duplicados = api_client.post(
        reverse("gestion-promociones-list"),
        {
            **base,
            "items_combo": [
                {"producto": producto.pk, "cantidad": 1},
                {"producto": producto.pk, "cantidad": 2},
            ],
        },
        format="json",
    )

    assert sin_items.status_code == status.HTTP_400_BAD_REQUEST
    assert duplicados.status_code == status.HTTP_400_BAD_REQUEST
    assert "items_combo" in sin_items.data
    assert "items_combo" in duplicados.data


@pytest.mark.django_db
def test_gestion_lista_y_filtra_promociones_no_vigentes(
    api_client: APIClient,
    operator_user: Any,
) -> None:
    inicio, fin = fechas_vigentes()
    Promocion.objects.create(
        nombre="Archivada",
        slug="archivada",
        tipo_promocion=Promocion.TipoPromocion.PORCENTAJE,
        porcentaje_descuento=Decimal("10.00"),
        fecha_inicio=inicio,
        fecha_fin=fin,
        activa=False,
    )
    api_client.force_authenticate(user=operator_user)

    response = api_client.get(
        reverse("gestion-promociones-list"),
        {"activa": "false", "vigente": "false"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["nombre"] == "Archivada"


@pytest.mark.django_db
def test_api_publica_excluye_promociones_vencidas(api_client: APIClient) -> None:
    ahora = timezone.now()
    Promocion.objects.create(
        nombre="Vencida",
        slug="vencida",
        tipo_promocion=Promocion.TipoPromocion.PORCENTAJE,
        porcentaje_descuento=Decimal("10.00"),
        fecha_inicio=ahora - timedelta(days=5),
        fecha_fin=ahora - timedelta(days=1),
    )

    response = api_client.get(reverse("promociones-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_motor_aplica_porcentaje_solo_al_alcance(
    producto: Producto,
    categoria: Categoria,
) -> None:
    otro = Producto.objects.create(
        categoria=categoria,
        sku="FIE-002",
        nombre="Otro kit",
        slug="otro-kit",
        precio_minorista=Decimal("200.00"),
        precio_mayorista=Decimal("160.00"),
        stock=20,
    )
    promocion = crear_promocion(
        nombre="Diez por ciento",
        slug="diez-por-ciento",
        porcentaje=Decimal("10.00"),
    )
    promocion.productos.add(producto)

    resultado = calcular_mejor_promocion(
        lineas=[
            LineaPromocion(producto, 2, Decimal("100.00")),
            LineaPromocion(otro, 1, Decimal("200.00")),
        ],
        subtotal=Decimal("400.00"),
        canal_venta=Promocion.CanalVenta.WEB,
        mayorista_aprobado=False,
    )

    assert resultado is not None
    assert resultado.descuento == Decimal("20.00")


@pytest.mark.django_db
def test_motor_elige_un_solo_mejor_descuento(producto: Producto) -> None:
    crear_promocion(
        nombre="Diez por ciento",
        slug="promo-diez",
        porcentaje=Decimal("10.00"),
    )
    mejor = crear_promocion(
        nombre="Treinta fijo",
        slug="promo-treinta",
        monto=Decimal("30.00"),
        tipo=Promocion.TipoPromocion.MONTO_FIJO,
    )

    resultado = calcular_mejor_promocion(
        lineas=[LineaPromocion(producto, 2, Decimal("100.00"))],
        subtotal=Decimal("200.00"),
        canal_venta=Promocion.CanalVenta.WEB,
        mayorista_aprobado=False,
    )

    assert resultado is not None
    assert resultado.promocion == mejor
    assert resultado.descuento == Decimal("30.00")


@pytest.mark.django_db
def test_motor_combo_respeta_cantidades_y_repeticiones(producto: Producto) -> None:
    combo = crear_promocion(
        nombre="Combo de dos",
        slug="combo-de-dos",
        monto=Decimal("15.00"),
        tipo=Promocion.TipoPromocion.COMBO,
    )
    ItemComboPromocion.objects.create(
        promocion=combo,
        producto=producto,
        cantidad=2,
    )

    sin_combo = calcular_mejor_promocion(
        lineas=[LineaPromocion(producto, 1, Decimal("100.00"))],
        subtotal=Decimal("100.00"),
        canal_venta=Promocion.CanalVenta.WEB,
        mayorista_aprobado=False,
    )
    dos_combos = calcular_mejor_promocion(
        lineas=[LineaPromocion(producto, 5, Decimal("100.00"))],
        subtotal=Decimal("500.00"),
        canal_venta=Promocion.CanalVenta.WEB,
        mayorista_aprobado=False,
    )

    assert sin_combo is None
    assert dos_combos is not None
    assert dos_combos.descuento == Decimal("30.00")


@pytest.mark.django_db
def test_motor_respeta_compra_minima_y_canal(producto: Producto) -> None:
    crear_promocion(
        nombre="Solo web con minimo",
        slug="solo-web-minimo",
        monto=Decimal("50.00"),
        tipo=Promocion.TipoPromocion.MONTO_FIJO,
        canal=Promocion.CanalVenta.WEB,
        compra_minima=Decimal("300.00"),
    )
    linea = LineaPromocion(producto, 3, Decimal("100.00"))

    canal_invalido = calcular_mejor_promocion(
        lineas=[linea],
        subtotal=Decimal("300.00"),
        canal_venta=Promocion.CanalVenta.WHATSAPP,
        mayorista_aprobado=False,
    )
    minimo_invalido = calcular_mejor_promocion(
        lineas=[LineaPromocion(producto, 2, Decimal("100.00"))],
        subtotal=Decimal("200.00"),
        canal_venta=Promocion.CanalVenta.WEB,
        mayorista_aprobado=False,
    )
    aplicable = calcular_mejor_promocion(
        lineas=[linea],
        subtotal=Decimal("300.00"),
        canal_venta=Promocion.CanalVenta.WEB,
        mayorista_aprobado=False,
    )

    assert canal_invalido is None
    assert minimo_invalido is None
    assert aplicable is not None
    assert aplicable.descuento == Decimal("50.00")


@pytest.mark.django_db
def test_checkout_guarda_promocion_y_total_calculado(
    api_client: APIClient,
    producto: Producto,
) -> None:
    promocion = crear_promocion(
        nombre="Beneficio web",
        slug="beneficio-web",
        porcentaje=Decimal("10.00"),
        canal=Promocion.CanalVenta.WEB,
    )
    promocion.productos.add(producto)

    response = api_client.post(
        "/api/v1/pedidos-publicos/",
        payload_checkout(producto),
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    pedido = Pedido.objects.get()
    assert pedido.subtotal == Decimal("200.00")
    assert pedido.descuento == Decimal("20.00")
    assert pedido.total == Decimal("180.00")
    assert pedido.promocion_aplicada == promocion
    assert pedido.promocion_nombre == "Beneficio web"
    assert response.data["promocion_nombre"] == "Beneficio web"


@pytest.mark.django_db
def test_promocion_mayorista_exige_cuenta_aprobada(
    api_client: APIClient,
    producto: Producto,
) -> None:
    crear_promocion(
        nombre="Mayorista aprobado",
        slug="mayorista-aprobado",
        porcentaje=Decimal("10.00"),
        tipo=Promocion.TipoPromocion.MAYORISTA,
    )

    anonimo = api_client.post(
        "/api/v1/pedidos-publicos/",
        payload_checkout(producto),
        format="json",
    )
    assert anonimo.status_code == status.HTTP_201_CREATED
    assert anonimo.data["descuento"] == "0.00"

    cliente = Cliente.objects.create(
        nombre="Mayorista",
        email="mayorista-aprobado@example.com",
        tipo_cliente=Cliente.TipoCliente.MAYORISTA,
    )
    usuario = get_user_model().objects.create_user(
        username=cliente.email,
        email=cliente.email,
        password="test-password",
    )
    PerfilUsuario.objects.create(
        usuario=usuario,
        cliente=cliente,
        rol=PerfilUsuario.Rol.CLIENTE_MAYORISTA,
        mayorista_aprobado=True,
    )
    api_client.force_authenticate(user=usuario)
    payload = payload_checkout(producto)
    payload["email"] = cliente.email

    aprobado = api_client.post(
        "/api/v1/pedidos-publicos/",
        payload,
        format="json",
    )

    assert aprobado.status_code == status.HTTP_201_CREATED
    assert aprobado.data["descuento"] == "20.00"


@pytest.mark.django_db
def test_checkout_anonimo_no_sobrescribe_cliente_existente(
    api_client: APIClient,
    producto: Producto,
) -> None:
    cliente = Cliente.objects.create(
        nombre="Nombre protegido",
        email="checkout-promo@example.com",
        whatsapp="0981999999",
    )
    payload = payload_checkout(producto)
    payload["nombre_completo"] = "Nombre atacante"
    payload["whatsapp"] = "000000"

    response = api_client.post(
        "/api/v1/pedidos-publicos/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    cliente.refresh_from_db()
    assert cliente.nombre == "Nombre protegido"
    assert cliente.whatsapp == "0981999999"


@pytest.mark.django_db
def test_checkout_autenticado_exige_email_de_su_cuenta(
    api_client: APIClient,
    producto: Producto,
) -> None:
    cliente = Cliente.objects.create(
        nombre="Cuenta protegida",
        email="cuenta-protegida@example.com",
    )
    usuario = get_user_model().objects.create_user(
        username=cliente.email,
        email=cliente.email,
        password="test-password",
    )
    PerfilUsuario.objects.create(
        usuario=usuario,
        cliente=cliente,
        rol=PerfilUsuario.Rol.CLIENTE_MINORISTA,
    )
    api_client.force_authenticate(user=usuario)

    response = api_client.post(
        "/api/v1/pedidos-publicos/",
        payload_checkout(producto),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data
    assert Pedido.objects.exists() is False
