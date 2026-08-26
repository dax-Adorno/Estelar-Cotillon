"""Modelos de productos."""

from typing import Any
from uuid import uuid4

from django.db import models
from django.utils.text import slugify

from apps.productos.image_processing import procesar_imagen_producto
from apps.productos.validators import validar_imagen_producto


class Categoria(models.Model):
    """Categoria comercial para agrupar productos del catalogo."""

    nombre = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categorias"
        ordering = ["nombre"]
        verbose_name = "categoria"
        verbose_name_plural = "categorias"

    def __str__(self) -> str:
        return self.nombre


class Producto(models.Model):
    """Producto comercializable dentro del catalogo de ESTELART."""

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="productos",
    )
    sku = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    descripcion = models.TextField(blank=True)
    precio_minorista = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    precio_mayorista = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    cantidad_minima_mayorista = models.PositiveIntegerField(default=1)
    stock = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "productos"
        ordering = ["nombre"]
        verbose_name = "producto"
        verbose_name_plural = "productos"
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["activo"]),
            models.Index(fields=["destacado"]),
        ]

    def __str__(self) -> str:
        return f"{self.sku} - {self.nombre}"


class ImagenProducto(models.Model):
    """Imagen asociada a un producto del catalogo."""

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="imagenes",
    )
    imagen = models.ImageField(
        upload_to="productos/originales/",
        validators=[validar_imagen_producto],
    )
    imagen_web = models.ImageField(
        upload_to="productos/web/",
        blank=True,
    )
    imagen_thumbnail = models.ImageField(
        upload_to="productos/thumbnails/",
        blank=True,
    )
    texto_alt = models.CharField(max_length=180, blank=True)
    principal = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "imagenes_producto"
        ordering = ["orden", "id"]
        verbose_name = "imagen de producto"
        verbose_name_plural = "imagenes de producto"
        indexes = [
            models.Index(fields=["producto"]),
            models.Index(fields=["principal"]),
            models.Index(fields=["activa"]),
        ]

    def __str__(self) -> str:
        return f"{self.producto.sku} - imagen {self.id}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Procesa la imagen original antes de guardar."""
        debe_procesar = self._debe_procesar_imagen()
        archivos_anteriores = (
            self._obtener_archivos_anteriores() if debe_procesar else []
        )

        if debe_procesar:
            nombre_base = self._generar_nombre_base()
            imagen_web, imagen_thumbnail = procesar_imagen_producto(
                self.imagen,
                nombre_base,
            )

            nombre_web = imagen_web.name or f"{nombre_base}-web.webp"
            nombre_thumbnail = imagen_thumbnail.name or f"{nombre_base}-thumb.webp"

            self.imagen_web.save(
                nombre_web,
                imagen_web,
                save=False,
            )
            self.imagen_thumbnail.save(
                nombre_thumbnail,
                imagen_thumbnail,
                save=False,
            )

        super().save(*args, **kwargs)
        self._eliminar_archivos_reemplazados(archivos_anteriores)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """Elimina tambien los archivos asociados cuando se borra la imagen."""
        archivos = [self.imagen, self.imagen_web, self.imagen_thumbnail]
        resultado = super().delete(*args, **kwargs)
        for archivo in archivos:
            if archivo and archivo.name:
                archivo.storage.delete(archivo.name)
        return resultado

    def _debe_procesar_imagen(self) -> bool:
        """Indica si deben generarse versiones optimizadas."""
        if not self.imagen:
            return False

        if self.pk is None:
            return True

        if not self.imagen_web or not self.imagen_thumbnail:
            return True

        imagen_guardada = (
            ImagenProducto.objects.filter(pk=self.pk).only("imagen").first()
        )

        if imagen_guardada is None:
            return True

        return imagen_guardada.imagen.name != self.imagen.name

    def _generar_nombre_base(self) -> str:
        """Genera un nombre seguro para archivos derivados."""
        base = slugify(self.producto.sku or self.producto.nombre)

        if not base:
            base = "producto"

        return f"{base}-{uuid4().hex[:12]}"

    def _obtener_archivos_anteriores(self) -> list[Any]:
        """Recupera archivos previos antes de reemplazar una imagen."""
        if self.pk is None:
            return []
        anterior = ImagenProducto.objects.filter(pk=self.pk).first()
        if anterior is None:
            return []
        return [anterior.imagen, anterior.imagen_web, anterior.imagen_thumbnail]

    def _eliminar_archivos_reemplazados(self, archivos: list[Any]) -> None:
        """Evita acumular originales y derivados obsoletos."""
        nombres_actuales = {
            archivo.name
            for archivo in (self.imagen, self.imagen_web, self.imagen_thumbnail)
            if archivo and archivo.name
        }
        for archivo in archivos:
            if archivo and archivo.name not in nombres_actuales:
                archivo.storage.delete(archivo.name)
