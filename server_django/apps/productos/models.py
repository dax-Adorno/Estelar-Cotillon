"""Modelos de productos y categorias."""

from django.db import models


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
    imagen = models.ImageField(upload_to="productos/originales/")
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
