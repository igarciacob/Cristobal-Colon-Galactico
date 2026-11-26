from os import name
from django.urls import path
from . import views

urlpatterns = [
    # path('bienvenida/', views.bienvenida, name='bienvenida')
    path('crearusuario/',views.crear_usuario, name='crearUsuario'),
    path('consultarusuario/<int:id>/', views.consultar_usuario, name='usuario'),
]