"""Pruebas de la API interna de gestion del catalogo."""

# pylint: disable=duplicate-code

from decimal import Decimal
from io import BytesIO
from typing import Any

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from apps.clientes.models import PerfilUsuario
from apps.productos.models import Categoria, ImagenProducto, Producto


@pytest.fixture(name="api_client")
def fixture_api_client() -> APIClient:
    return APIClient()


@pytest.fixture(name="operator_user")
def fixture_operator_user() -> Any:
    usuario = get_user_model().objects.create_user(
        username="catalogo@example.com",
        email="catalogo@example.com",
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
        username="cliente-catalogo@example.com",
        email="cliente-catalogo@example.com",
        password="test-password",
    )
    PerfilUsuario.objects.create(
        usuario=usuario,
        rol=PerfilUsuario.Rol.CLIENTE_MINORISTA,
    )
    return usuario


@pytest.fixture(name="categoria")
def fixture_categoria() -> Categoria:
    return Categoria.objects.create(
        nombre="Cotillon",
        slug="cotillon",
    )


@pytest.fixture(name="producto")
def fixture_producto(categoria: Categoria) -> Producto:
    return Producto.objects.create(
        categoria=categoria,
        sku="COT-001",
        nombre="Kit de fiesta",
        slug="kit-de-fiesta",
        precio_minorista=Decimal("15000.00"),
        precio_mayorista=Decimal("12000.00"),
        cantidad_minima_mayorista=5,
        stock=20,
    )


def crear_archivo_imagen(nombre: str) -> SimpleUploadedFile:
    """Genera una imagen JPEG pequena y valida en memoria."""
    buffer = BytesIO()
    Image.new("RGB", (800, 600), "white").save(buffer, format="JPEG")
    return SimpleUploadedFile(
        nombre,
        buffer.getvalue(),
        content_type="image/jpeg",
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "nombre_ruta",
    (
        "gestion-categorias-list",
        "gestion-productos-list",
        "gestion-imagenes-producto-list",
    ),
)
def test_gestion_catalogo_exige_rol_interno(
    api_client: APIClient,
    customer_user: Any,
    nombre_ruta: str,
) -> None:
    ruta = reverse(nombre_ruta)

    assert api_client.get(ruta).status_code == status.HTTP_403_FORBIDDEN

    api_client.force_authenticate(user=customer_user)
    assert api_client.get(ruta).status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_operador_crea_categoria_con_slug_automatico(
    api_client: APIClient,
    operator_user: Any,
) -> None:
    api_client.force_authenticate(user=operator_user)

    response = api_client.post(
        reverse("gestion-categorias-list"),
        {
            "nombre": "  Globos metalizados  ",
            "descripcion": "Globos para eventos",
            "activa": True,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["nombre"] == "Globos metalizados"
    assert response.data["slug"] == "globos-metalizados"


@pytest.mark.django_db
def test_gestion_categorias_incluye_inactivas_y_pagina(
    api_client: APIClient,
    operator_user: Any,
) -> None:
    Categoria.objects.create(nombre="Activa", slug="activa", activa=True)
    Categoria.objects.create(nombre="Archivada", slug="archivada", activa=False)
    api_client.force_authenticate(user=operator_user)

    response = api_client.get(
        reverse("gestion-categorias-list"),
        {"activa": "false"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["nombre"] == "Archivada"


@pytest.mark.django_db
def test_operador_crea_producto_y_normaliza_datos(
    api_client: APIClient,
    operator_user: Any,
    categoria: Categoria,
) -> None:
    api_client.force_authenticate(user=operator_user)

    response = api_client.post(
        reverse("gestion-productos-list"),
        {
            "categoria": categoria.pk,
            "sku": "  glo-010  ",
            "nombre": "  Globo estrella  ",
            "descripcion": "Globo metalizado",
            "precio_minorista": "9000.00",
            "precio_mayorista": "7500.00",
            "cantidad_minima_mayorista": 10,
            "stock": 80,
            "activo": True,
            "destacado": True,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["sku"] == "GLO-010"
    assert response.data["nombre"] == "Globo estrella"
    assert response.data["slug"] == "globo-estrella"


@pytest.mark.django_db
def test_gestion_producto_rechaza_reglas_comerciales_invalidas(
    api_client: APIClient,
    operator_user: Any,
    categoria: Categoria,
) -> None:
    api_client.force_authenticate(user=operator_user)

    response = api_client.post(
        reverse("gestion-productos-list"),
        {
            "categoria": categoria.pk,
            "sku": "ERR-001",
            "nombre": "Producto invalido",
            "precio_minorista": "1000.00",
            "precio_mayorista": "1200.00",
            "cantidad_minima_mayorista": 0,
            "stock": 1,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "precio_mayorista" in response.data
    assert "cantidad_minima_mayorista" in response.data


@pytest.mark.django_db
def test_operador_actualiza_stock_y_filtra_productos(
    api_client: APIClient,
    operator_user: Any,
    producto: Producto,
) -> None:
    api_client.force_authenticate(user=operator_user)

    update_response = api_client.patch(
        reverse("gestion-productos-detail", kwargs={"pk": producto.pk}),
        {"stock": 0, "activo": False},
        format="json",
    )
    list_response = api_client.get(
        reverse("gestion-productos-list"),
        {"activo": "false", "con_stock": "false", "search": "COT-001"},
    )

    assert update_response.status_code == status.HTTP_200_OK
    assert list_response.status_code == status.HTTP_200_OK
    assert list_response.data["count"] == 1
    assert list_response.data["results"][0]["stock"] == 0


@pytest.mark.django_db
def test_productos_de_categoria_inactiva_no_son_publicos(
    api_client: APIClient,
    producto: Producto,
) -> None:
    producto.categoria.activa = False
    producto.categoria.save(update_fields=["activa"])

    response = api_client.get(reverse("productos-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_filtro_invalido_devuelve_error_controlado(
    api_client: APIClient,
    operator_user: Any,
) -> None:
    api_client.force_authenticate(user=operator_user)

    response = api_client.get(
        reverse("gestion-productos-list"),
        {"categoria": "no-es-un-id"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "categoria" in response.data


@pytest.mark.django_db
def test_productos_y_categorias_se_desactivan_en_lugar_de_borrarse(
    api_client: APIClient,
    operator_user: Any,
    producto: Producto,
) -> None:
    api_client.force_authenticate(user=operator_user)

    response = api_client.delete(
        reverse("gestion-productos-detail", kwargs={"pk": producto.pk}),
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert Producto.objects.filter(pk=producto.pk).exists()


@pytest.mark.django_db
def test_operador_gestiona_una_sola_imagen_principal(
    api_client: APIClient,
    operator_user: Any,
    producto: Producto,
    tmp_path: Any,
) -> None:
    api_client.force_authenticate(user=operator_user)
    ruta = reverse("gestion-imagenes-producto-list")

    with override_settings(MEDIA_ROOT=str(tmp_path)):
        primera = api_client.post(
            ruta,
            {
                "producto": producto.pk,
                "imagen": crear_archivo_imagen("primera.jpg"),
                "texto_alt": "Primera imagen",
                "principal": True,
                "activa": True,
            },
            format="multipart",
        )
        segunda = api_client.post(
            ruta,
            {
                "producto": producto.pk,
                "imagen": crear_archivo_imagen("segunda.jpg"),
                "texto_alt": "Segunda imagen",
                "principal": True,
                "activa": True,
            },
            format="multipart",
        )

    assert primera.status_code == status.HTTP_201_CREATED
    assert segunda.status_code == status.HTTP_201_CREATED
    assert (
        ImagenProducto.objects.filter(
            producto=producto,
            principal=True,
        ).count()
        == 1
    )
    assert ImagenProducto.objects.get(pk=primera.data["id"]).principal is False
    assert ImagenProducto.objects.get(pk=segunda.data["id"]).principal is True


@pytest.mark.django_db
def test_catalogo_publico_excluye_imagenes_inactivas(
    api_client: APIClient,
    producto: Producto,
    tmp_path: Any,
) -> None:
    with override_settings(MEDIA_ROOT=str(tmp_path)):
        ImagenProducto.objects.create(
            producto=producto,
            imagen=crear_archivo_imagen("publica.jpg"),
            texto_alt="Publica",
            activa=True,
        )
        ImagenProducto.objects.create(
            producto=producto,
            imagen=crear_archivo_imagen("interna.jpg"),
            texto_alt="Interna",
            activa=False,
        )

        response = api_client.get(
            reverse("productos-detail", kwargs={"pk": producto.pk}),
        )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["imagenes"]) == 1
    assert response.data["imagenes"][0]["texto_alt"] == "Publica"


@pytest.mark.django_db
def test_borrar_imagen_elimina_archivos_derivados(
    api_client: APIClient,
    operator_user: Any,
    producto: Producto,
    tmp_path: Any,
) -> None:
    api_client.force_authenticate(user=operator_user)

    with override_settings(MEDIA_ROOT=str(tmp_path)):
        imagen = ImagenProducto.objects.create(
            producto=producto,
            imagen=crear_archivo_imagen("eliminar.jpg"),
        )
        rutas = [
            tmp_path / imagen.imagen.name,
            tmp_path / imagen.imagen_web.name,
            tmp_path / imagen.imagen_thumbnail.name,
        ]
        response = api_client.delete(
            reverse(
                "gestion-imagenes-producto-detail",
                kwargs={"pk": imagen.pk},
            ),
        )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert all(not ruta.exists() for ruta in rutas)
