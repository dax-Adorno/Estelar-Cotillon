"""Validadores para imagenes de productos."""

from pathlib import Path
from typing import Any

from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

EXTENSIONES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".webp"}
TAMANO_MAXIMO_MB = 8
PIXELS_MAXIMOS = 24_000_000


def validar_imagen_producto(archivo: Any) -> None:
    """Valida formato, peso y dimensiones de una imagen de producto."""
    extension = Path(archivo.name).suffix.lower()

    if extension not in EXTENSIONES_PERMITIDAS:
        raise ValidationError(
            "Formato no permitido. Use JPG, PNG o WebP.",
        )

    if archivo.size > TAMANO_MAXIMO_MB * 1024 * 1024:
        raise ValidationError(
            f"La imagen no puede superar {TAMANO_MAXIMO_MB} MB.",
        )

    posicion = archivo.tell()

    try:
        imagen = Image.open(archivo)
        imagen.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError("El archivo no es una imagen valida.") from exc
    finally:
        archivo.seek(posicion)

    imagen = Image.open(archivo)
    ancho, alto = imagen.size
    archivo.seek(posicion)

    if ancho * alto > PIXELS_MAXIMOS:
        raise ValidationError(
            "La imagen tiene dimensiones demasiado grandes.",
        )
