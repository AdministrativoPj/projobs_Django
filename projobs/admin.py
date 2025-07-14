from django.contrib import admin
from .models import Usuario, OfertaLaboralIndependiente, MensajeContacto

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'correo', 'rol')
    search_fields = ('nombre', 'apellido', 'correo')
    list_filter = ('rol',)

@admin.register(OfertaLaboralIndependiente)
class OfertaLaboralIndependienteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'cliente', 'modo_trabajo', 'categoria', 'fecha_limite', 'estado')
    search_fields = ('titulo', 'descripcion', 'cliente__nombre')
    list_filter = ('modo_trabajo', 'categoria', 'estado')
    date_hierarchy = 'fecha_publicacion'

@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'mensaje')
    search_fields = ('nombre', 'correo')
