from os import name
from django.urls import path
from . import views

urlpatterns = [
    # path('bienvenida/', views.bienvenida, name='bienvenida')
    path('crearusuario/',views.crear_usuario, name='crearUsuario'),
    path('consultarusuario/<int:id>/', views.consultar_usuario, name='usuario'),
    path("usuarios/<int:id>/modificar/", views.modificar_usuario),
    path("usuarios/<int:id>/eliminar/", views.eliminar_usuario),
    path('asignarmision/',views.asignar_mision, name='asignarMision'),
]
