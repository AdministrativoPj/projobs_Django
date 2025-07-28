from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('inicioSesion/', views.inicioSesion, name='inicioSesion'),
    path('formulario/', views.formulario, name='formulario'),
    

    # Usuarios
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('perfilusuario/', views.perfilusuario, name='perfilusuario'),
    path('perfiltrabajador/', views.perfiltrabajador, name='perfiltrabajador'),
    path('recuperar-password/', views.recuperar_password, name='recuperar_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('trabajadores/', views.ver_trabajadores, name='ver_trabajadores'),


    # Ofertas y postulaciones
    path('crear-oferta/', views.crear_oferta, name='crear_oferta'),
    path('lista_ofertas/', views.lista_ofertas, name='lista_ofertas'),
    path('marcar_revisada/', views.marcar_como_revisada, name='marcar_revisada'),
    path('historial/', views.historial_postulaciones, name='historial_postulaciones'),
    path('contratos/', views.contratos_usuario, name='contratos_usuario'),
    path('finalizar_postulacion/<int:id>/', views.finalizar_postulacion, name='finalizar_postulacion'),


    # Chat
    path('chat/<int:id_usuario>/', views.chat_con_usuario, name='chat_con_usuario'),

    # Notificaciones
    path('notificaciones/', views.obtener_notificaciones, name='obtener_notificaciones'),
    path('notificaciones/marcar/', views.marcar_notificaciones_leidas, name='marcar_notificaciones_leidas'),

    # Perfil trabajador
    path('trabajador/<int:id>/', views.perfil_trabajador_detalle, name='perfil_trabajador_detalle'),

    # Evidencias
    path('subir_evidencia/', views.subir_evidencia_view, name='subir_evidencia'),

    # Admin propio
    path('admin-usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard-graficos/', views.admin_dashboard_graficos, name='admin_dashboard_graficos'),
    path('admin-ofertas/', views.admin_ofertas, name='admin_ofertas'),
    path('admin-postulaciones/', views.admin_postulaciones, name='admin_postulaciones'),
    path('admin-calificaciones/', views.admin_calificaciones, name='admin_calificaciones'),
    path('admin-calificaciones/eliminar/<int:id>/', views.admin_eliminar_calificacion, name='admin_eliminar_calificacion'),
    path('admin-evidencias/', views.admin_evidencias, name='admin_evidencias'),
    path('admin-evidencias/eliminar/<int:id>/', views.admin_eliminar_evidencia, name='admin_eliminar_evidencia'),
    path('admin-chats/', views.admin_chats, name='admin_chats'),
    path('admin-chats/<int:usuario1_id>/<int:usuario2_id>/', views.admin_ver_chat, name='admin_ver_chat'),




]
