from os import name
from django.urls import path
from . import views

urlpatterns = [
    # path('bienvenida/', views.bienvenida, name='bienvenida')
    path('crearusuario/', views.crear_usuario, name='crearUsuario'),
    path('consultarusuario/<int:id>/', views.consultar_usuario, name='usuario'),
    path("modificarusuarios/<int:id>", views.modificar_usuario),
    path("eliminarusuarios/<int:id>/", views.eliminar_usuario),
    path('asignarmision/', views.asignar_mision, name='asignarMision'),
    path('consultartripulacion/<int:id>/', views.consultar_tripulacion, name='tripulacion'),
    path("finalizarmisiones/<int:id>/", views.finalizar_mision),
    path("consultarplanetascapitan/<int:id>/", views.consultar_planetas_capitan, name="consultar_planetas_capitan"),
]
