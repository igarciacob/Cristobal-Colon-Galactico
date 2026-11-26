from django.shortcuts import render
from json import JSONDecodeError
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Usuario, Habilidad

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
def modificar_usuario(request, id):
    if request.method not in ("PUT", "PATCH"):
        return JsonResponse(
            {"error": "Tipo de petición no es correcta"},
            status=405,
        )

    try:
        usuario = Usuario.objects.get(id=id)
    except Usuario.DoesNotExist:
        return JsonResponse(
            {"error": "Usuario no encontrado"},
            status=404,
        )

    try:
        usuario_json = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse(
            {"error": "El JSON no está bien formado"},
            status=400,
        )

    if "tipo" in usuario_json:
        msg_error = validacion(usuario_json.get("tipo"))
        if msg_error != "":
            return JsonResponse({"error": msg_error}, status=400)
        usuario.tipo = usuario_json.get("tipo")

    if "nombre" in usuario_json:
        if not usuario_json.get("nombre"):
            return JsonResponse(
                {"error": "El nombre no puede estar vacío"},
                status=400,
            )
        usuario.nombre = usuario_json.get("nombre")

    if "apellidos" in usuario_json:
        if not usuario_json.get("apellidos"):
            return JsonResponse(
                {"error": "Los apellidos no pueden estar vacíos"},
                status=400,
            )
        usuario.apellidos = usuario_json.get("apellidos")

    usuario.save()

    if "habilidad" in usuario_json:
        habilidades = usuario_json.get("habilidad")
        if not isinstance(habilidades, list):
            return JsonResponse(
                {"error": "El campo 'habilidad' debe ser una lista"},
                status=400,
            )
        usuario.habilidad.clear()
        crear_habilidades(habilidades, usuario)

    return JsonResponse(
        {
            "exito": "Usuario modificado correctamente",
            "id": usuario.id,
        },
        status=200,
    )

@csrf_exempt
def eliminar_usuario(request, id):
    if request.method != "DELETE":
        return JsonResponse(
            {"error": "Tipo de petición no es correcta"},
            status=405,
        )

    try:
        usuario = Usuario.objects.get(id=id)
    except Usuario.DoesNotExist:
        return JsonResponse(
            {"error": "Usuario no encontrado"},
            status=404,
        )

    usuario.delete()

    return JsonResponse(
        {
            "exito": "Usuario eliminado correctamente",
            "id": id,
        },
        status=200,
    )