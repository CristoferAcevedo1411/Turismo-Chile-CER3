from django.contrib import admin

from .models import Categoria, Experiencia


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "slug"]
    search_fields = ["nombre"]
    prepopulated_fields = {"slug": ["nombre"]}


@admin.register(Experiencia)
class ExperienciaAdmin(admin.ModelAdmin):
    list_display = [
        "nombre",
        "fecha",
        "ubicacion",
        "precio_por_persona",
        "capacidad_maxima",
        "cupos_disponibles",
        "publicada",
    ]
    list_filter = ["publicada", "categorias", "region", "fecha"]
    list_editable = ["publicada"]
    search_fields = ["nombre", "descripcion", "ubicacion", "region"]
    filter_horizontal = ["categorias"]
    date_hierarchy = "fecha"
    readonly_fields = ["cupos_disponibles", "creada", "actualizada"]
    actions = ["publicar", "despublicar"]

    fieldsets = [
        (None, {"fields": ["nombre", "descripcion", "categorias", "imagen"]}),
        ("Ubicación", {"fields": ["ubicacion", "region", "latitud", "longitud"]}),
        ("Fecha y duración", {"fields": ["fecha", "hora_inicio", "duracion_horas"]}),
        (
            "Precio y cupos",
            {"fields": ["precio_por_persona", "capacidad_maxima", "cupos_disponibles"]},
        ),
        ("Publicación", {"fields": ["publicada", "creada", "actualizada"]}),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).con_cupos()

    @admin.display(description="Cupos disponibles")
    def cupos_disponibles(self, obj):
        return obj.cupos_disponibles

    @admin.action(description="Publicar experiencias seleccionadas")
    def publicar(self, request, queryset):
        actualizadas = queryset.update(publicada=True)
        self.message_user(request, f"{actualizadas} experiencia(s) publicadas.")

    @admin.action(description="Despublicar experiencias seleccionadas")
    def despublicar(self, request, queryset):
        actualizadas = queryset.update(publicada=False)
        self.message_user(request, f"{actualizadas} experiencia(s) despublicadas.")
