"""Tests para imagenes de productos."""

from decimal import Decimal
from io import BytesIO

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

from apps.productos.image_processing import procesar_imagen_producto
from apps.productos.models import Categoria, ImagenProducto, Producto
from apps.productos.validators import validar_imagen_producto


def crear_archivo_imagen(
    nombre: str = "producto.jpg",
    formato: str = "JPEG",
    tamano: tuple[int, int] = (2000, 1000),
) -> SimpleUploadedFile:
    """Crea una imagen valida en memoria para tests."""
    buffer = BytesIO()
    imagen = Image.new("RGB", tamano, "white")
    imagen.save(buffer, format=formato)

    return SimpleUploadedFile(
        nombre,
        buffer.getvalue(),
        content_type="image/jpeg",
    )


def crear_producto() -> Producto:
    """Crea un producto para pruebas de imagen."""
    categoria = Categoria.objects.create(
        nombre="Categoria test",
        slug="categoria-test",
        descripcion="",
    )

    return Producto.objects.create(
        categoria=categoria,
        sku="IMG-001",
        nombre="Producto con imagen",
        slug="producto-con-imagen",
        descripcion="Producto usado para test de imagen.",
        precio_minorista=Decimal("1000.00"),
        precio_mayorista=Decimal("800.00"),
        cantidad_minima_mayorista=5,
        stock=20,
        activo=True,
        destacado=True,
    )


def test_validar_imagen_producto_acepta_imagen_valida() -> None:
    """Debe aceptar imagenes JPG validas."""
    archivo = crear_archivo_imagen()

    validar_imagen_producto(archivo)


def test_validar_imagen_producto_rechaza_svg() -> None:
    """Debe rechazar formatos no permitidos."""
    archivo = SimpleUploadedFile(
        "producto.svg",
        b"<svg></svg>",
        content_type="image/svg+xml",
    )

    with pytest.raises(ValidationError):
        validar_imagen_producto(archivo)


def test_validar_imagen_producto_rechaza_archivo_pesado() -> None:
    """Debe rechazar imagenes que superen el peso maximo."""
    archivo = SimpleUploadedFile(
        "producto.jpg",
        b"0" * (9 * 1024 * 1024),
        content_type="image/jpeg",
    )

    with pytest.raises(ValidationError):
        validar_imagen_producto(archivo)


def test_validar_imagen_producto_rechaza_contenido_invalido() -> None:
    """Debe rechazar archivos con extension valida pero contenido invalido."""
    archivo = SimpleUploadedFile(
        "producto.jpg",
        b"contenido invalido",
        content_type="image/jpeg",
    )

    with pytest.raises(ValidationError):
        validar_imagen_producto(archivo)


def test_procesar_imagen_producto_genera_webp_y_thumbnail() -> None:
    """Debe generar version web y thumbnail en formato WebP."""
    archivo = crear_archivo_imagen()
    imagen_web, thumbnail = procesar_imagen_producto(
        archivo,
        "producto-test",
    )

    assert imagen_web.name == "producto-test-web.webp"
    assert thumbnail.name == "producto-test-thumb.webp"

    with Image.open(BytesIO(imagen_web.read())) as imagen_web_generada:
        assert imagen_web_generada.format == "WEBP"
        assert imagen_web_generada.width == 1600

    with Image.open(BytesIO(thumbnail.read())) as thumbnail_generado:
        assert thumbnail_generado.format == "WEBP"
        assert thumbnail_generado.width == 500


@pytest.mark.django_db
def test_imagen_producto_genera_versiones_optimizadas(tmp_path) -> None:
    """Debe generar imagen web y thumbnail al guardar."""
    producto = crear_producto()

    with override_settings(MEDIA_ROOT=str(tmp_path)):
        imagen_producto = ImagenProducto.objects.create(
            producto=producto,
            imagen=crear_archivo_imagen(),
            texto_alt="Imagen de producto",
            principal=True,
        )

        assert imagen_producto.imagen_web.name.endswith(".webp")
        assert imagen_producto.imagen_thumbnail.name.endswith(".webp")
        assert imagen_producto.imagen_web.storage.exists(
            imagen_producto.imagen_web.name,
        )
        assert imagen_producto.imagen_thumbnail.storage.exists(
            imagen_producto.imagen_thumbnail.name,
        )
