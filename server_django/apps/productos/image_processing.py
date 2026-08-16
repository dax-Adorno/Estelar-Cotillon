"""Procesamiento de imagenes de productos."""

from io import BytesIO
from typing import Any

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont, ImageOps

ANCHO_MAXIMO_WEB = 1600
ANCHO_MAXIMO_THUMBNAIL = 500
CALIDAD_WEBP = 85
MARCA_DE_AGUA = "ESTELART"


def procesar_imagen_producto(
    archivo: Any,
    nombre_base: str,
) -> tuple[ContentFile, ContentFile]:
    """Genera version web optimizada y thumbnail con marca de agua."""
    archivo.open("rb")
    archivo.seek(0)

    with Image.open(archivo) as imagen_original:
        imagen = ImageOps.exif_transpose(imagen_original)
        imagen = _convertir_a_rgb(imagen)

        imagen_web = _redimensionar(imagen, ANCHO_MAXIMO_WEB)
        imagen_web = _aplicar_marca_de_agua(imagen_web)

        thumbnail = _redimensionar(imagen, ANCHO_MAXIMO_THUMBNAIL)

    archivo.seek(0)

    return (
        _guardar_webp(imagen_web, f"{nombre_base}-web.webp"),
        _guardar_webp(thumbnail, f"{nombre_base}-thumb.webp"),
    )


def _convertir_a_rgb(imagen: Image.Image) -> Image.Image:
    """Convierte una imagen a RGB con fondo blanco si tiene transparencia."""
    if imagen.mode in ("RGBA", "LA"):
        fondo = Image.new("RGB", imagen.size, "white")
        fondo.paste(imagen, mask=imagen.getchannel("A"))
        return fondo

    if imagen.mode != "RGB":
        return imagen.convert("RGB")

    return imagen.copy()


def _redimensionar(imagen: Image.Image, ancho_maximo: int) -> Image.Image:
    """Reduce dimensiones manteniendo proporcion."""
    if imagen.width <= ancho_maximo:
        return imagen.copy()

    relacion = ancho_maximo / imagen.width
    alto = int(imagen.height * relacion)

    return imagen.resize(
        (ancho_maximo, alto),
        Image.Resampling.LANCZOS,
    )


def _aplicar_marca_de_agua(imagen: Image.Image) -> Image.Image:
    """Agrega una marca de agua simple sobre la version publica."""
    resultado = imagen.copy()
    capa = Image.new("RGBA", resultado.size, (255, 255, 255, 0))
    dibujo = ImageDraw.Draw(capa)

    fuente = ImageFont.load_default()
    margen = max(20, resultado.width // 50)
    bbox = dibujo.textbbox((0, 0), MARCA_DE_AGUA, font=fuente)
    texto_ancho = bbox[2] - bbox[0]
    texto_alto = bbox[3] - bbox[1]

    posicion = (
        resultado.width - texto_ancho - margen,
        resultado.height - texto_alto - margen,
    )

    dibujo.rectangle(
        (
            posicion[0] - 10,
            posicion[1] - 6,
            posicion[0] + texto_ancho + 10,
            posicion[1] + texto_alto + 6,
        ),
        fill=(255, 255, 255, 150),
    )
    dibujo.text(
        posicion,
        MARCA_DE_AGUA,
        fill=(30, 30, 30, 180),
        font=fuente,
    )

    return Image.alpha_composite(resultado.convert("RGBA"), capa).convert("RGB")


def _guardar_webp(imagen: Image.Image, nombre_archivo: str) -> ContentFile:
    """Guarda una imagen en memoria como WebP."""
    buffer = BytesIO()

    imagen.save(
        buffer,
        format="WEBP",
        quality=CALIDAD_WEBP,
        method=6,
    )

    return ContentFile(
        buffer.getvalue(),
        name=nombre_archivo,
    )
