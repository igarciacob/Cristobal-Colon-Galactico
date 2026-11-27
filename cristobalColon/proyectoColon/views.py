from datetime import date
from json import JSONDecodeError
import json

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Exoplaneta, Habilidad, Mision, Nave, Tipo, Usuario


# Create your views here.
def validacion(tipo):
    descrError = ""
    tipos_usuario = ("tripulante", "capitan")
    if tipo not in tipos_usuario:
        descrError = "El usuario debe ser capitan o tripulante\n"

    return descrError


def crear_habilidades(habilidades, objeto):
    for habilidad in habilidades:
        habilidad_model, creada = Habilidad.objects.get_or_create(nombre=habilidad)
        # una vez creada la habilidad, se asocia al usuario
        objeto.habilidad.add(habilidad_model)
    if not creada:
        print("Etiqueta ya creada")
    else:
        print("Etiqueta nueva")


def validar_datos_usuario(datos, comprobar_obligatorios=True):
    errores = []
    tipos_usuario = ("tripulante", "capitan")

    if comprobar_obligatorios:
        if not datos.get("nombre"):
            errores.append("El nombre es obligatorio")
        if not datos.get("apellidos"):
            errores.append("Los apellidos son obligatorios")
        if not datos.get("tipo"):
            errores.append("El tipo es obligatorio")

    if "nombre" in datos:
        if not datos.get("nombre") or not isinstance(datos.get("nombre"), str):
            errores.append("El nombre debe ser un texto no vacío")

    if "apellidos" in datos:
        if not datos.get("apellidos") or not isinstance(datos.get("apellidos"), str):
            errores.append("Los apellidos deben ser un texto no vacío")

    if "tipo" in datos and datos.get("tipo") is not None:
        if datos.get("tipo") not in tipos_usuario:
            errores.append("El usuario debe ser capitan o tripulante")

    if "habilidad" in datos and not isinstance(datos.get("habilidad"), list):
        errores.append("El campo 'habilidad' debe ser una lista")

    return errores


@csrf_exempt
def crear_usuario(request):
    if request.method != "POST":
        return JsonResponse({"error": "Tipo de petición no es correcta"}, status=405)

    try:
        usuario_json = json.loads(request.body)
    except JSONDecodeError as e:
        return JsonResponse({"error": "El JSON no está bien formado"}, status=400)

    errores = validar_datos_usuario(usuario_json, comprobar_obligatorios=True)
    if len(errores) > 0:
        return JsonResponse({"errores": errores}, status=400)

    usuario = Usuario.objects.create(
        nombre=usuario_json.get("nombre"),  # .get para que no falle si no viene el dato
        apellidos=usuario_json.get("apellidos"),
        tipo=usuario_json.get("tipo"),
    )
    usuario.save()
    # si en el usuario vienen habilidades que no existen las creamos
    habilidades = usuario_json.get("habilidad", [])
    crear_habilidades(habilidades, usuario)
    return JsonResponse(
        {
            "exito": "Usuario creado correctamente",
            "id": usuario.id,
        },
        status=201,
    )


def consultar_usuario(request, id):
    if request.method != "GET":
        return JsonResponse(
            {"error": "Esta petición solo funciona con get"},
            status=405,
        )
    usuario = Usuario.objects.get(id=id)
    datos = {
        "nombre": usuario.nombre,
        "apellidos": usuario.apellidos,
        "tipo": usuario.tipo,
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

    errores = validar_datos_usuario(usuario_json, comprobar_obligatorios=False)
    if len(errores) > 0:
        return JsonResponse({"errores": errores}, status=400)

    if "tipo" in usuario_json:
        usuario.tipo = usuario_json.get("tipo")

    if "nombre" in usuario_json:
        usuario.nombre = usuario_json.get("nombre")

    if "apellidos" in usuario_json:
        usuario.apellidos = usuario_json.get("apellidos")

    usuario.save()

    if "habilidad" in usuario_json:
        habilidades = usuario_json.get("habilidad")
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


@csrf_exempt
def asignar_mision(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Esta petición solo funciona con post"},
            status=405,
        )
    try:
        mision_json = json.loads(request.body)
    except JSONDecodeError as e:
        return JsonResponse({"error": "El JSON no está bien formado"}, status=400)
    nombre = mision_json.get("nombre")
    fecha_inicio = mision_json.get("fecha_inicio")
    fecha_fin = mision_json.get("fecha_fin")

    # validamos los campos obligatorios
    if not all([nombre, fecha_inicio, fecha_fin]):
        return JsonResponse(
            {"error": "Faltan campos obligatorios (nombre, fecha_inicio, fecha_fin)"},
            status=400,
        )

    if fecha_inicio > fecha_fin:
        return JsonResponse(
            {"error": "La fecha de inicio no puede ser posterior a la de fin"},
            status=400,
        )

    # escogemos una nave aleatoria que en esa fecha no esté de mision
    nave = (
        Nave.objects.exclude(
            mision__fecha_inicio__lte=fecha_fin,
            mision__fecha_fin__gte=fecha_inicio,
        )
        .order_by("?")
        .first()
    )

    if nave is None:
        return JsonResponse(
            {"error": "No hay naves disponibles para las fechas de la misión"},
            status=404,
        )
    tipo = Tipo.objects.get(id=nave.tipo.id)
    num_capitanes = tipo.num_capitanes
    capacidad_min = tipo.capacidad_min
    capacidad_max = tipo.capacidad_max
    # Seleccionamos capitan(es) de manera aleatoria
    capitanes = (
        Usuario.objects.filter(tipo="capitan")
        .exclude(
            Q(mision__fecha_inicio__lte=fecha_fin)
            & Q(mision__fecha_fin__gte=fecha_inicio)
        )
        .distinct()
        .order_by("?")[:num_capitanes]
    )
    # validamos que hay suficientes
    if capitanes is None or len(capitanes) < num_capitanes:
        return JsonResponse(
            {
                "error": "No hay un numero suficiente de capitanes para las fechas de la misión"
            },
            status=404,
        )
    # seleccionamos tripulantes
    max_tripulantes = max(0, capacidad_max - num_capitanes)
    min_tripulantes = max(0, capacidad_min - num_capitanes)
    # num_tripulantes = capacidad_max - num_capitanes
    tripulantes = (
        Usuario.objects.filter(tipo="tripulante")
        .exclude(
            Q(mision__fecha_inicio__lte=fecha_fin)
            & Q(mision__fecha_fin__gte=fecha_inicio)
        )
        .distinct()
        .order_by("?")[:max_tripulantes]
    )
    # validamos que hay suficientes
    if len(tripulantes) < min_tripulantes:
        return JsonResponse(
            {
                "error": "No hay un número suficiente de  tripulación disponible"
                         " para las fechas de la misión "
            },
            status=404,
        )
    # creamos la mision y una vez creada le añadimos la tripulacion
    mision = Mision.objects.create(
        nombre=mision_json.get("nombre"),
        fecha_inicio=mision_json.get("fecha_inicio"),
        fecha_fin=mision_json.get("fecha_fin"),
        exito=False,
        id_nave=nave,
    )
    mision.save()
    for capitan in capitanes:
        mision.usuarios.add(capitan)

    for tripulante in tripulantes:
        mision.usuarios.add(tripulante)

    return JsonResponse(
        {
            "exito": "Misión creada correctamente",
            "id": mision.id,
        },
        status=201,
    )


# Consultar los tripulantes de una misión
def consultar_tripulacion(request, id):
    if request.method != "GET":
        return JsonResponse(
            {"error": "Esta petición solo funciona con get"}, status=405
        )
    try:
        mision = Mision.objects.get(id=id)
    except Mision.DoesNotExist:
        return JsonResponse({"error": "Misión no encontrada"}, status=404)
    tripulacion = []
    # recogemos los usuarios de la tripulacion
    for usuario in mision.usuarios.all():
        tripulacion.append(
            {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "apellidos": usuario.apellidos,
                "tipo": usuario.tipo,
                "habilidad": list(usuario.habilidad.values()),
            }
        )
    return JsonResponse(
        {"id": mision.id, "nombre": mision.nombre, "tripulacion": tripulacion}
    )


def validar_finalizar_mision(datos):
    errores = []

    if "exito" not in datos or not isinstance(datos.get("exito"), bool):
        errores.append("El campo 'exito' es obligatorio y debe ser true o false")

    if "fecha_fin" in datos and datos.get("fecha_fin"):
        if not isinstance(datos.get("fecha_fin"), str):
            errores.append(
                "El campo 'fecha_fin' debe ser una fecha en texto (YYYY-MM-DD)"
            )

    if "exoplanetas" in datos and not isinstance(datos.get("exoplanetas"), list):
        errores.append("El campo 'exoplanetas' debe ser una lista")

    return errores


@csrf_exempt
def finalizar_mision(request, id):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Tipo de petición no es correcta"},
            status=405,
        )

    try:
        mision = Mision.objects.get(id=id)
    except Mision.DoesNotExist:
        return JsonResponse(
            {"error": "Misión no encontrada"},
            status=404,
        )

    try:
        mision_json = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse(
            {"error": "El JSON no está bien formado"},
            status=400,
        )

    errores = validar_finalizar_mision(mision_json)
    if len(errores) > 0:
        return JsonResponse({"errores": errores}, status=400)

    exito = mision_json.get("exito")

    if "fecha_fin" in mision_json and mision_json.get("fecha_fin"):
        fecha_fin = mision_json.get("fecha_fin")
    else:
        fecha_fin = date.today()

    mision.exito = exito
    mision.fecha_fin = fecha_fin
    mision.save()

    exoplanetas_creados = []
    if exito is True and "exoplanetas" in mision_json:
        exoplanetas = mision_json.get("exoplanetas")
        for exo in exoplanetas:
            if isinstance(exo, dict):
                nombre_exo = exo.get("nombre")
            else:
                nombre_exo = exo

            if nombre_exo:
                nuevo_exo = Exoplaneta.objects.create(
                    nombre=nombre_exo,
                    id_mision=mision,
                )
                exoplanetas_creados.append(
                    {
                        "id": nuevo_exo.id,
                        "nombre": nuevo_exo.nombre,
                    }
                )

    return JsonResponse(
        {
            "exito": "Misión finalizada correctamente",
            "id": mision.id,
            "resultado": mision.exito,
            "fecha_fin": str(mision.fecha_fin),
            "exoplanetas": exoplanetas_creados,
        },
        status=200,
    )


def consultar_planetas_capitan(request, id):
    if request.method != "GET":
        return JsonResponse(
            {"error": "Esta petición solo funciona con get"},
            status=405,
        )

    try:
        capitan = Usuario.objects.get(id=id)
    except Usuario.DoesNotExist:
        return JsonResponse(
            {"error": "Usuario no encontrado"},
            status=404,
        )

    if capitan.tipo != "capitan":
        return JsonResponse(
            {"error": "El usuario indicado no es un capitán"},
            status=400,
        )

    misiones = Mision.objects.filter(usuarios=capitan)
    exoplanetas_lista = []

    for mision in misiones:
        planetas_mision = Exoplaneta.objects.filter(id_mision=mision)
        for planeta in planetas_mision:
            exoplanetas_lista.append(
                {
                    "id": planeta.id,
                    "nombre": planeta.nombre,
                    "mision_id": mision.id,
                    "mision_nombre": mision.nombre,
                }
            )

    return JsonResponse(
        {
            "capitan_id": capitan.id,
            "nombre": capitan.nombre,
            "apellidos": capitan.apellidos,
            "exoplanetas": exoplanetas_lista,
        },
        status=200,
    )
