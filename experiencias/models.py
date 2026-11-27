from datetime import timedelta

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.nombre


class ExperienciaQuerySet(models.QuerySet):
    def publicadas(self):
        return self.filter(publicada=True)

    def vigentes(self):
        # las que todavia no pasan (hoy incluido)
        return self.filter(fecha__gte=timezone.localdate())

    def proximas(self, dias=14):
        hoy = timezone.localdate()
        return self.filter(fecha__gte=hoy, fecha__lte=hoy + timedelta(days=dias))

    def con_cupos(self):
        # suma los participantes de las reservas activas para calcular cupos en una sola consulta
        return self.annotate(
            cupos_ocupados_db=Coalesce(
                Sum(
                    "reservas__cantidad_participantes",
                    filter=Q(reservas__estado="activa"),
                ),
                Value(0),
            )
        )


class Experiencia(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    categorias = models.ManyToManyField(
        Categoria, related_name="experiencias", blank=True
    )

    ubicacion = models.CharField(
        "ubicación", max_length=150, help_text="Ej: San Pedro de Atacama"
    )
    region = models.CharField("región", max_length=80, blank=True)
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    imagen = models.ImageField(upload_to="experiencias/", blank=True)
    fecha = models.DateField()
    hora_inicio = models.TimeField(null=True, blank=True)
    duracion_horas = models.DecimalField(
        "duración (horas)",
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(0.5)],
    )
    precio_por_persona = models.PositiveIntegerField(help_text="Precio en CLP")
    capacidad_maxima = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    publicada = models.BooleanField(default=False)

    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    objects = ExperienciaQuerySet.as_manager()

    class Meta:
        ordering = ["fecha", "hora_inicio"]

    def __str__(self):
        return f"{self.nombre} ({self.fecha:%d-%m-%Y})"

    @property
    def cupos_ocupados(self):
        # si viene del queryset con_cupos() se usa ese valor y no se consulta de nuevo
        if hasattr(self, "cupos_ocupados_db"):
            return self.cupos_ocupados_db
        total = self.reservas.filter(estado="activa").aggregate(
            total=Sum("cantidad_participantes")
        )["total"]
        return total or 0

    @property
    def cupos_disponibles(self):
        return max(self.capacidad_maxima - self.cupos_ocupados, 0)

    @property
    def ya_paso(self):
        return self.fecha < timezone.localdate()

    @property
    def es_reservable(self):
        return self.publicada and not self.ya_paso and self.cupos_disponibles > 0
