from django.contrib import admin

from .models import Reserva


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "cliente",
        "experiencia",
        "cantidad_participantes",
        "costo_total",
        "estado",
        "creada",
    ]
    list_filter = ["estado", "experiencia"]
    search_fields = ["cliente__username", "experiencia__nombre"]
    readonly_fields = ["costo_total", "creada", "cancelada_en"]
    list_select_related = ["cliente", "experiencia"]
