from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from experiencias.models import Experiencia


class Reserva(models.Model):
    class Estado(models.TextChoices):
        ACTIVA = "activa", "Activa"
        CANCELADA = "cancelada", "Cancelada"

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservas",
    )
    experiencia = models.ForeignKey(
        Experiencia,
        on_delete=models.PROTECT,
        related_name="reservas",
    )
    cantidad_participantes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    costo_total = models.PositiveIntegerField(editable=False)
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.ACTIVA
    )
    creada = models.DateTimeField(auto_now_add=True)
    cancelada_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-creada"]

    def __str__(self):
        return f"Reserva #{self.pk} - {self.cliente} - {self.experiencia.nombre}"

    def save(self, *args, **kwargs):
        # el total siempre se calcula aca, nunca viene del formulario
        self.costo_total = self.experiencia.precio_por_persona * self.cantidad_participantes
        super().save(*args, **kwargs)
