from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

# -------------------------
# Modelo de Usuario
# -------------------------
class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=254)

    ROLES = (
        (1, "Admin"),
        (2, "Cliente"),
        (3, "Trabajador"),
    )
    rol = models.IntegerField(choices=ROLES, default=2)
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    token_recuperacion = models.CharField(max_length=255, null=True, blank=True)  # <-- NUEVO CAMPO

    def promedio_calificaciones(self):
        promedio = self.calificaciones_recibidas.aggregate(avg=Avg('puntuacion'))['avg']
        return round(promedio, 1) if promedio else None

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.correo}"


# -------------------------
# Modelo de Oferta Laboral
# -------------------------
class OfertaLaboralIndependiente(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=100)

    MODO_TRABAJO = [
        ('presencial', 'Presencial'),
        ('remoto', 'Remoto'),
        ('hibrido', 'Híbrido')
    ]
    modo_trabajo = models.CharField(max_length=20, choices=MODO_TRABAJO)

    rango_pago = models.CharField(max_length=50)
    fecha_limite = models.DateField()
    max_postulaciones = models.PositiveIntegerField(default=5)  # <-- AÑADE ESTO AQUÍ

    PROFESIONES = [
        ('Electricista', 'Electricista'),
        ('Diseñador Gráfico', 'Diseñador Gráfico'),
        ('Programador', 'Programador'),
        ('Plomero', 'Plomero'),
        ('Jardinero', 'Jardinero'),
        ('Otro', 'Otro'),
    ]
    categoria = models.CharField(max_length=50, choices=PROFESIONES)
    descripcion_profesion = models.CharField(max_length=100, blank=True)

    estado = models.CharField(max_length=20, default='abierta')
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo



# -------------------------
# Modelo de Contacto
# -------------------------
class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.correo}) - {self.fecha_envio.strftime('%Y-%m-%d %H:%M')}"


# -------------------------
# Modelo de Postulación
# -------------------------
class Postulacion(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
    ]

    trabajador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='postulaciones')
    oferta = models.ForeignKey(OfertaLaboralIndependiente, on_delete=models.CASCADE, related_name='postulaciones')
    fecha_postulacion = models.DateTimeField(auto_now_add=True)
    revisada = models.BooleanField(default=False)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    finalizada = models.BooleanField(default=False)  # <-- NUEVO CAMPO

    class Meta:
        unique_together = ('trabajador', 'oferta')

    def __str__(self):
        return f"{self.trabajador.nombre} -> {self.oferta.titulo} [{self.estado}]"

# -------------------------
#  Modelo de Mensaje Directo
# -------------------------
class Mensaje(models.Model):
    emisor = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='mensajes_enviados')
    receptor = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='mensajes_recibidos')
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.emisor} ➜ {self.receptor} : {self.contenido[:30]}"


# -------------------------
# Modelo de Calificación
# -------------------------
class Calificacion(models.Model):
    trabajador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="calificaciones_recibidas")
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="calificaciones_realizadas")
    puntuacion = models.IntegerField()
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trabajador', 'cliente')

    def __str__(self):
        return f"{self.cliente} → {self.trabajador}: {self.puntuacion}"

class Evidencia(models.Model):
    trabajador = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 3})
    postulacion = models.ForeignKey(Postulacion, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='evidencias/')
    descripcion = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidencia de {self.trabajador.nombre} - {self.fecha.strftime('%Y-%m-%d')}"