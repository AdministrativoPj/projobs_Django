from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.db.models import Q, Count
from django.utils import timezone
import re

from .models import Usuario, OfertaLaboralIndependiente, MensajeContacto, Postulacion, Mensaje, Calificacion, Evidencia



# -------------------------
# Admin helpers
# -------------------------

def es_admin(user_id):
    try:
        usuario = Usuario.objects.get(id=user_id)
        return usuario.rol == 1
    except Usuario.DoesNotExist:
        return False

def require_admin(view_func):
    def _wrapped_view(request, *args, **kwargs):
        usuario_id = request.session.get('usuario_id')
        if not usuario_id or not es_admin(usuario_id):
            return redirect('baseperfil')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
# -------------------------
# Funciones generales
# -------------------------

def index(request):
    if request.session.get('usuario_id'):
        return redirect('perfilusuario')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        correo = request.POST.get('correo', '').strip()
        mensaje = request.POST.get('mensaje', '').strip()

        if not nombre or not correo or not mensaje:
            messages.error(request, "Por favor completa todos los campos.")
        else:
            asunto = f"Nuevo mensaje de contacto de {nombre}"
            cuerpo = f"Nombre: {nombre}\nCorreo: {correo}\n\nMensaje:\n{mensaje}"
            try:
                send_mail(asunto, cuerpo, settings.DEFAULT_FROM_EMAIL, ['projobsaddmin2025@gmail.com'])
                messages.success(request, "Mensaje enviado correctamente.")
            except Exception as e:
                print(f"Error al enviar correo: {e}")
                messages.error(request, "Ocurrió un error al enviar el mensaje.")

    return render(request, "index.html")


# -------------------------
# Autenticación
# -------------------------

def inicioSesion(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        try:
            usuario = Usuario.objects.get(correo=correo)
            if check_password(password, usuario.password):
                request.session['usuario_id'] = usuario.id
                if usuario.rol == 1:
                    return redirect('perfilusuario')
                else:
                    return redirect('perfilusuario')
            else:
                messages.error(request, "Contraseña incorrecta")
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado")
    return render(request, 'inicioSesion.html')


def formulario(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        apellido = request.POST.get("apellido", "").strip()
        correo = request.POST.get("correo", "").strip()
        password = request.POST.get("password", "").strip()
        foto = request.FILES.get("foto")
        rol = request.POST.get("rol", "").strip()

        errores = []
        if not nombre or not apellido or not correo or not password or not rol:
            errores.append("Todos los campos son obligatorios.")
        if rol not in ["2", "3"]:
            errores.append("Rol inválido. Selecciona Cliente o Trabajador.")
        if not re.match(r'^[\w\.-]+@(gmail\.com|hotmail\.com|outlook\.com)$', correo):
            errores.append("Solo se permiten correos de gmail.com, hotmail.com o outlook.com.")
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', password):
            errores.append("La contraseña debe contener mínimo 6 caracteres con letras y números.")
        if Usuario.objects.filter(correo=correo).exists():
            errores.append("Este correo ya está registrado.")

        if errores:
            for error in errores:
                messages.error(request, error)
        else:
            Usuario.objects.create(
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                password=make_password(password),
                foto=foto,
                rol=int(rol)
            )
            messages.success(request, "Usuario registrado correctamente")
            return redirect('inicioSesion')

    return render(request, "formulario.html")


def cerrar_sesion(request):
    request.session.flush()
    logout(request)
    return redirect('index')


# -------------------------
# Perfil
# -------------------------

def perfilusuario(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    if not usuario.correo or "@" not in usuario.correo:
        messages.warning(request, "⚠️ Por favor edita tu perfil y agrega un correo válido para poder contactarte.")
    return render(request, 'perfilusuario.html', {'usuario': usuario})


def perfiltrabajador(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    return render(request, 'perfiltrabajador.html', {'usuario': usuario})


def editar_perfil(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    mensaje = None

    if request.method == "POST":
        nuevo_correo = request.POST.get("correo", "").strip()
        if Usuario.objects.exclude(id=usuario.id).filter(correo=nuevo_correo).exists():
            mensaje = "Este correo ya está registrado por otro usuario."
        else:
            usuario.nombre = request.POST.get("nombre", usuario.nombre).strip()
            usuario.apellido = request.POST.get("apellido", usuario.apellido).strip()
            usuario.correo = nuevo_correo or usuario.correo
            if request.POST.get("password", "").strip():
                usuario.password = make_password(request.POST.get("password"))
            if usuario.rol != 1:
                usuario.rol = int(request.POST.get("rol", usuario.rol))
            if request.FILES.get("foto"):
                usuario.foto = request.FILES.get("foto")
            usuario.save()
            mensaje = "Perfil actualizado correctamente."

    return render(request, 'editar_perfil.html', {'usuario': usuario, 'mensaje': mensaje})


# -------------------------
# Ofertas y postulaciones
# -------------------------

def crear_oferta(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    if request.method == 'POST':
        OfertaLaboralIndependiente.objects.create(
            cliente=usuario,
            titulo=request.POST.get('titulo'),
            descripcion=request.POST.get('descripcion'),
            ubicacion=request.POST.get('ubicacion'),
            modo_trabajo=request.POST.get('modo_trabajo'),
            rango_pago=request.POST.get('rango_pago'),
            fecha_limite=request.POST.get('fecha_limite'),
            categoria=request.POST.get('categoria'),
            descripcion_profesion=request.POST.get('descripcion_profesion', '')
        )
        messages.success(request, "✅ Oferta publicada exitosamente.")
    return render(request, 'ofertas/crear_oferta.html', {'usuario': usuario})


def lista_ofertas(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    if usuario.rol != 3:
        messages.error(request, "Solo los trabajadores pueden ver las ofertas para postularse.")
        return redirect('perfilusuario')

    categoria = request.GET.get('categoria')
    ofertas = OfertaLaboralIndependiente.objects.exclude(cliente=usuario)
    if categoria:
        ofertas = ofertas.filter(categoria=categoria).order_by('-fecha_publicacion')
    else:
        ofertas = ofertas.order_by('-fecha_publicacion')[:5]

    if request.method == 'POST':
        id_oferta = request.POST.get('id_oferta')
        oferta = get_object_or_404(OfertaLaboralIndependiente, id=id_oferta)
        if oferta.cliente == usuario:
            messages.error(request, "No puedes postularte a tu propia oferta.")
        elif Postulacion.objects.filter(trabajador=usuario, oferta=oferta).exists():
            messages.warning(request, "Ya estás postulado a esta oferta.")
        else:
            Postulacion.objects.create(trabajador=usuario, oferta=oferta, revisada=False)
            messages.success(request, "Te has postulado correctamente.")
        return redirect('lista_ofertas')

    return render(request, 'ofertas/lista_ofertas.html', {
        'usuario': usuario,
        'ofertas': ofertas,
        'categoria_seleccionada': categoria
    })


@require_http_methods(["GET", "POST"])
def historial_postulaciones(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    if usuario.rol == 2:
        postulaciones = Postulacion.objects.filter(oferta__cliente=usuario)
    elif usuario.rol == 3:
        postulaciones = Postulacion.objects.filter(trabajador=usuario)
    else:
        postulaciones = []

    if request.method == 'POST':
        post_id = request.POST.get('postulacion_id')
        if usuario.rol == 2:
            postulacion = get_object_or_404(Postulacion, id=post_id, oferta__cliente=usuario)
            postulacion.estado = request.POST.get('estado')
            postulacion.revisada = True
            postulacion.save()
            messages.success(request, "✅ Estado actualizado correctamente.")
        elif usuario.rol == 3:
            try:
                postulacion = Postulacion.objects.get(id=post_id, trabajador=usuario)
                postulacion.delete()
                messages.success(request, "🗑️ Postulación eliminada correctamente.")
            except Postulacion.DoesNotExist:
                messages.error(request, "❌ No se pudo eliminar la postulación.")
        return redirect('historial_postulaciones')

    return render(request, 'historial_postulaciones.html', {'usuario': usuario, 'postulaciones': postulaciones})


# -------------------------
# Chat, calificaciones y admin
# -------------------------

@require_http_methods(["GET", "POST"])
def chat_con_usuario(request, id_usuario):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    receptor = get_object_or_404(Usuario, id=id_usuario)

    if request.method == "POST":
        contenido = request.POST.get("contenido", "").strip()
        if contenido:
            Mensaje.objects.create(emisor=usuario, receptor=receptor, contenido=contenido)
        return redirect('chat_con_usuario', id_usuario=id_usuario)

    mensajes = Mensaje.objects.filter(Q(emisor=usuario, receptor=receptor) | Q(emisor=receptor, receptor=usuario)).order_by('fecha_envio')
    Mensaje.objects.filter(emisor=receptor, receptor=usuario, leido=False).update(leido=True)

    return render(request, "chat/chat.html", {'usuario': usuario, 'receptor': receptor, 'mensajes': mensajes})


@require_http_methods(["GET", "POST"])
def perfil_trabajador_detalle(request, id):
    cliente = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    trabajador = get_object_or_404(Usuario, id=id, rol=3)
    calificaciones = Calificacion.objects.filter(trabajador=trabajador).order_by('-fecha')

    if request.method == 'POST':
        puntuacion = request.POST.get('calificacion')
        comentario = request.POST.get('comentario', '').strip()
        if puntuacion and comentario and 1 <= int(puntuacion) <= 5:
            Calificacion.objects.update_or_create(
                trabajador=trabajador, cliente=cliente,
                defaults={'puntuacion': int(puntuacion), 'comentario': comentario}
            )
            messages.success(request, "✅ Calificación guardada correctamente.")
        else:
            messages.error(request, "❌ La puntuación debe estar entre 1 y 5 o falta comentario.")
        return redirect('perfil_trabajador_detalle', id=trabajador.id)

    return render(request, 'trabajador/perfil_trabajador_detalle.html', {
        'usuario': cliente, 'trabajador': trabajador,
        'promedio': trabajador.promedio_calificaciones(),
        'calificaciones': calificaciones[:10],
        'mostrar_todas': calificaciones.count() > 3
    })


def obtener_notificaciones(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    data = []
    if usuario.rol == 2:
        data += [{'mensaje': f"{p.trabajador.nombre} se postuló a {p.oferta.titulo}",
                  'fecha': p.fecha_postulacion.strftime("%Y-%m-%d %H:%M"), 'url': '/historial/'}
                 for p in Postulacion.objects.filter(oferta__cliente=usuario, revisada=False)]
    if usuario.rol == 3:
        data += [{'mensaje': f"Tu postulación a {r.oferta.titulo} fue revisada",
                  'fecha': r.fecha_postulacion.strftime("%Y-%m-%d %H:%M"), 'url': '/historial/'}
                 for r in Postulacion.objects.filter(trabajador=usuario, revisada=True)]
    data += [{'mensaje': f"{m.emisor.nombre} te envió un mensaje",
              'fecha': m.fecha_envio.strftime("%Y-%m-%d %H:%M"), 'url': f"/chat/{m.emisor.id}/"}
             for m in Mensaje.objects.filter(receptor=usuario, leido=False)]
    return JsonResponse({'notificaciones': data})


@require_POST
def marcar_notificaciones_leidas(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    if usuario.rol == 2:
        Postulacion.objects.filter(oferta__cliente=usuario, revisada=False).update(revisada=True)
    Mensaje.objects.filter(receptor=usuario, leido=False).update(leido=True)
    return JsonResponse({'ok': True})


@require_POST
def marcar_como_revisada(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    postulacion = get_object_or_404(Postulacion, id=request.POST.get('id'), oferta__cliente_id=usuario.id)
    postulacion.revisada = True
    postulacion.save()
    return JsonResponse({'ok': True})


@require_http_methods(["POST"])
def subir_evidencia(request):
    trabajador = get_object_or_404(Usuario, id=request.session.get('usuario_id'), rol=3)
    postulacion = get_object_or_404(Postulacion, id=request.POST.get('postulacion_id'), trabajador=trabajador, estado='aceptado')
    Evidencia.objects.create(trabajador=trabajador, postulacion=postulacion,
                             archivo=request.FILES.get('archivo'),
                             descripcion=request.POST.get('descripcion', '').strip())
    return JsonResponse({'ok': True})


# -------------------------
# Admin
# -------------------------

def admin_dashboard(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    if usuario.rol != 1:
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('perfilusuario')
    return render(request, 'admin/dashboard.html', {
        'usuario': usuario,
        'total_usuarios': Usuario.objects.count(),
        'total_ofertas': OfertaLaboralIndependiente.objects.count(),
        'total_postulaciones': Postulacion.objects.count(),
        'total_calificaciones': Calificacion.objects.count(),
        'total_evidencias': Evidencia.objects.count()
    })


@require_http_methods(["GET", "POST"])
@require_admin
def admin_usuarios(request):
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id=usuario_id)

    usuarios = Usuario.objects.all().order_by('rol', 'nombre')

    if request.method == "POST":
        user_id = request.POST.get('user_id')
        accion = request.POST.get('accion')

        usuario_edit = get_object_or_404(Usuario, id=user_id)

        if accion == 'eliminar':
            usuario_edit.delete()
            messages.success(request, "✅ Usuario eliminado correctamente.")
        elif accion.startswith('rol_'):
            nuevo_rol = int(accion.split('_')[1])
            usuario_edit.rol = nuevo_rol
            usuario_edit.save()
            messages.success(request, f"✅ Rol actualizado a {usuario_edit.get_rol_display()}.")
        return redirect('admin_usuarios')

    return render(request, 'admin/usuarios.html', {
        'usuario': usuario,
        'usuarios': usuarios,
    })
    
@require_admin
def admin_dashboard_graficos(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))

    # Usuarios por rol con nombres claros
    roles_map = {
        1: "Admin",
        2: "Cliente",
        3: "Trabajador"
    }
    data_usuarios = { roles_map.get(u['rol'], f"Rol {u['rol']}"): u['total']
                      for u in Usuario.objects.values('rol').annotate(total=Count('id')) }

    # Ofertas por categoría
    data_ofertas = { o['categoria'] or 'Sin Categoría': o['total'] 
                     for o in OfertaLaboralIndependiente.objects.values('categoria').annotate(total=Count('id')) }

    # Postulaciones por estado
    data_postulaciones = { p['estado']: p['total'] 
                           for p in Postulacion.objects.values('estado').annotate(total=Count('id')) }

    # Calificaciones con nombre del trabajador
    data_calificaciones = {}
    for c in Calificacion.objects.values('trabajador').annotate(total=Count('id')):
        trabajador = Usuario.objects.filter(id=c['trabajador']).first()
        nombre = f"{trabajador.nombre} {trabajador.apellido}" if trabajador else f"ID {c['trabajador']}"
        data_calificaciones[nombre] = c['total']

    # Evidencias con nombre del trabajador
    data_evidencias = {}
    for e in Evidencia.objects.values('trabajador').annotate(total=Count('id')):
        trabajador = Usuario.objects.filter(id=e['trabajador']).first()
        nombre = f"{trabajador.nombre} {trabajador.apellido}" if trabajador else f"ID {e['trabajador']}"
        data_evidencias[nombre] = e['total']

    return render(request, 'admin/dashboard_graficos.html', {
        'usuario': usuario,
        'data_usuarios': data_usuarios,
        'data_ofertas': data_ofertas,
        'data_postulaciones': data_postulaciones,
        'data_calificaciones': data_calificaciones,
        'data_evidencias': data_evidencias
    })
@require_http_methods(["GET", "POST"])
@require_admin
def admin_ofertas(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    ofertas = OfertaLaboralIndependiente.objects.all().order_by('-fecha_publicacion')

    if request.method == "POST":
        oferta_id = request.POST.get('oferta_id')
        accion = request.POST.get('accion')
        oferta = get_object_or_404(OfertaLaboralIndependiente, id=oferta_id)

        if accion == 'eliminar':
            oferta.delete()
            messages.success(request, "✅ Oferta eliminada correctamente.")
        # Podrías añadir más acciones (como cambiar estado) aquí

        return redirect('admin_ofertas')

    return render(request, 'admin/ofertas.html', {'usuario': usuario, 'ofertas': ofertas})

@require_http_methods(["GET", "POST"])
@require_admin
def admin_postulaciones(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))

    postulaciones = Postulacion.objects.select_related('oferta', 'trabajador').all().order_by('-fecha_postulacion')

    if request.method == "POST":
        post_id = request.POST.get('postulacion_id')
        accion = request.POST.get('accion')

        postulacion = get_object_or_404(Postulacion, id=post_id)

        if accion == 'eliminar':
            postulacion.delete()
            messages.success(request, "✅ Postulación eliminada correctamente.")
        elif accion in ['aceptado', 'rechazado', 'pendiente']:
            postulacion.estado = accion
            postulacion.revisada = True
            postulacion.save()
            messages.success(request, f"✅ Estado cambiado a {accion}.")
        return redirect('admin_postulaciones')

    return render(request, 'admin/postulaciones.html', {
        'usuario': usuario,
        'postulaciones': postulaciones,
    })
@require_admin
def admin_calificaciones(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    calificaciones = Calificacion.objects.select_related('trabajador', 'cliente').order_by('-fecha')

    return render(request, 'admin/calificaciones.html', {
        'usuario': usuario,
        'calificaciones': calificaciones
    })

@require_admin
def admin_eliminar_calificacion(request, id):
    calificacion = get_object_or_404(Calificacion, id=id)
    calificacion.delete()
    messages.success(request, "✅ Calificación eliminada correctamente.")
    return redirect('admin_calificaciones')

@require_admin
def admin_evidencias(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    evidencias = Evidencia.objects.select_related('trabajador', 'postulacion').order_by('-id')

    return render(request, 'admin/evidencias.html', {
        'usuario': usuario,
        'evidencias': evidencias
    })

@require_admin
def admin_eliminar_evidencia(request, id):
    evidencia = get_object_or_404(Evidencia, id=id)
    evidencia.delete()
    messages.success(request, "✅ Evidencia eliminada correctamente.")
    return redirect('admin_evidencias')

@require_admin
def admin_chats(request):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    # Obtener todas las combinaciones únicas de chats
    chats = Mensaje.objects.values_list('emisor_id', 'receptor_id').distinct()

    pares_unicos = set()
    for emisor_id, receptor_id in chats:
        par = tuple(sorted((emisor_id, receptor_id)))
        pares_unicos.add(par)

    lista_chats = []
    for u1_id, u2_id in pares_unicos:
        u1 = Usuario.objects.filter(id=u1_id).first()
        u2 = Usuario.objects.filter(id=u2_id).first()
        if u1 and u2:
            lista_chats.append({'usuario1': u1, 'usuario2': u2})

    return render(request, 'admin/chats.html', {
        'usuario': usuario,
        'chats': lista_chats
    })

@require_admin
def admin_ver_chat(request, usuario1_id, usuario2_id):
    usuario = get_object_or_404(Usuario, id=request.session.get('usuario_id'))
    user1 = get_object_or_404(Usuario, id=usuario1_id)
    user2 = get_object_or_404(Usuario, id=usuario2_id)

    mensajes = Mensaje.objects.filter(
        Q(emisor=user1, receptor=user2) | Q(emisor=user2, receptor=user1)
    ).order_by('fecha_envio')

    return render(request, 'admin/chat_detalle.html', {
        'usuario': usuario,
        'user1': user1,
        'user2': user2,
        'mensajes': mensajes
    })
