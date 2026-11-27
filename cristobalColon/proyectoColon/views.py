from django.db.models import Q
from django.shortcuts import render
from json import JSONDecodeError
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Usuario, Habilidad, Nave, Tipo, Mision


# Create your views here.
@csrf_exempt
def crear_usuario(request):

     if (request.method != 'POST'):
         return JsonResponse({"error": "Tipo de petición no es correcta"}, status=405)

     try:
         usuario_json =json.loads(request.body)
     except JSONDecodeError as e:
         return JsonResponse({"error": 'El JSON no está bien formado'}, status=400)

     msgError = validacion(usuario_json.get('tipo'))
     if msgError != '':
         return JsonResponse({'error': msgError}, status=400)

     usuario =Usuario.objects.create(
         nombre=usuario_json.get('nombre'),#.get para que no falle si no viene el dato
         apellidos=usuario_json.get('apellidos'),
         tipo=usuario_json.get('tipo')
     )
     usuario.save()
     # si en el usuario vienen habilidades que no existen las creamos
     habilidades = usuario_json.get('habilidad', [])
     crear_habilidades(habilidades, usuario)
     return JsonResponse({
         "exito": "Usuario creado correctamente",
         "id": usuario.id
     },
         status=201)

def validacion (tipo):
    descrError=''
    tipos_usuario = ('tripulante', 'capitan')
    if tipo not in tipos_usuario:
        descrError ='El usuario debe ser capitan o tripulante\n'

    return descrError


def crear_habilidades(habilidades,objeto):
    for habilidad in habilidades:
        habilidad_model,creada = Habilidad.objects.get_or_create(nombre=habilidad)
        #una vez creada la habilidad, se asocia al usuario
        objeto.habilidad.add(habilidad_model)
    if not creada:
        print("Etiqueta ya creada")
    else:
        print("Etiqueta nueva")


def consultar_usuario(request, id):
    if request.method != "GET":
        return JsonResponse(
            {"error": "Esta petición solo funciona con get"},
            status=405
        )
    usuario = Usuario.objects.get(id=id)
    datos = {
        'nombre': usuario.nombre,
        'apellidos': usuario.apellidos,
        'tipo': usuario.tipo,
    }
    return JsonResponse(datos, safe=False)

@csrf_exempt
def asignar_mision(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Esta petición solo funciona con post"},
            status=405
        )
    try:
        mision_json = json.loads(request.body)
    except JSONDecodeError as e:
        return JsonResponse({"error": 'El JSON no está bien formado'}, status=400)
    nombre = mision_json.get('nombre')
    fecha_inicio = mision_json.get('fecha_inicio')
    fecha_fin = mision_json.get('fecha_fin')

    #validamos los campos obligatorios
    if not all([nombre, fecha_inicio, fecha_fin]):
        return JsonResponse(
            {"error": "Faltan campos obligatorios (nombre, fecha_inicio, fecha_fin)"},
            status=400
        )

    if fecha_inicio > fecha_fin:
        return JsonResponse(
            {"error": "La fecha de inicio no puede ser posterior a la de fin"},
            status=400
        )

    # escogemos una nave aleatoria que en esa fecha no esté de mision
    nave = Nave.objects.exclude(
        mision__fecha_inicio__lte=fecha_fin,
        mision__fecha_fin__gte=fecha_inicio).order_by('?').first()

    if nave is None:
        return JsonResponse(
            {"error": "No hay naves disponibles para las fechas de la misión"},
            status=404
        )
    tipo = Tipo.objects.get(id=nave.tipo.id)
    num_capitanes = tipo.num_capitanes
    capacidad_min = tipo.capacidad_min
    capacidad_max = tipo.capacidad_max
    #Seleccionamos capitan(es) de manera aleatoria
    capitanes = (
        Usuario.objects.filter(tipo='capitan').exclude(Q(mision__fecha_inicio__lte=fecha_fin) &
            Q(mision__fecha_fin__gte=fecha_inicio)
        ).distinct().order_by('?')[:num_capitanes]
    )
    #validamos que hay suficientes
    if capitanes is None or len(capitanes) < num_capitanes:
        return JsonResponse(
            {"error": "No hay un numero suficiente de capitanes para las fechas de la misión"},
            status=404
        )
    #seleccionamos tripulantes
    max_tripulantes = max(0, capacidad_max - num_capitanes)
    min_tripulantes = max(0, capacidad_min - num_capitanes)
    #num_tripulantes = capacidad_max - num_capitanes
    tripulantes = (
        Usuario.objects.filter(tipo = 'tripulante').exclude(Q(mision__fecha_inicio__lte=fecha_fin) &
            Q(mision__fecha_fin__gte=fecha_inicio)
        ).distinct().order_by('?')[:max_tripulantes]
    )
    # validamos que hay suficientes
    if len(tripulantes) < min_tripulantes:
        return JsonResponse(
            {"error": "No hay un número suficiente de  tripulación disponible"
                      " para las fechas de la misión "},
            status=404
        )
    # creamos la mision y una vez creada le añadimos la tripulacion
    mision = Mision.objects.create(
        nombre = mision_json.get('nombre'),
        fecha_inicio = mision_json.get('fecha_inicio'),
        fecha_fin = mision_json.get('fecha_fin'),
        exito = False,
        id_nave = nave
    )
    mision.save()
    for capitan in capitanes:
        mision.usuarios.add(capitan)

    for tripulante in tripulantes:
        mision.usuarios.add(tripulante)

    return JsonResponse({
        "exito": "Misión creada correctamente",
        "id": mision.id
    },
    status=201)

