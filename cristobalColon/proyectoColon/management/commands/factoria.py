import random
from datetime import date

from django.core.management.base import BaseCommand
from faker import Faker

from proyectoColon.models import Exoplaneta, Habilidad, Mision, Nave, Tipo, Usuario


class Command(BaseCommand):
    help = "Genera datos de prueba para el proyecto Cristóbal Colón Galáctico"

    def handle(self, *args, **options):
        faker = Faker("es_ES")

        try:
            # 1. Crear habilidades básicas
            nombres_habilidades = [
                "Misiones largas",
                "Explorador de cortas distancias",
                "Conflictivo",
                "Cocinero",
                "Mantenimiento",
            ]
            habilidades = []
            for nombre in nombres_habilidades:
                hab, _ = Habilidad.objects.get_or_create(nombre=nombre)
                habilidades.append(hab)

            # 2. Crear tipos de nave
            tipo_pequena, _ = Tipo.objects.get_or_create(
                nombre="Pequeña",
                defaults={
                    "num_capitanes": 1,
                    "capacidad_min": 4,
                    "capacidad_max": 4,
                },
            )
            tipo_mediana, _ = Tipo.objects.get_or_create(
                nombre="Mediana",
                defaults={
                    "num_capitanes": 1,
                    "capacidad_min": 8,
                    "capacidad_max": 10,
                },
            )
            tipo_grande, _ = Tipo.objects.get_or_create(
                nombre="Grande",
                defaults={
                    "num_capitanes": 2,
                    "capacidad_min": 11,
                    "capacidad_max": 30,
                },
            )

            tipos_por_nombre = {
                "Pequeña": tipo_pequena,
                "Mediana": tipo_mediana,
                "Grande": tipo_grande,
            }

            # 3. Crear 12 capitanes con habilidades aleatorias
            capitanes = []
            for _ in range(12):
                capitan = Usuario.objects.create(
                    nombre=faker.first_name(),
                    apellidos=f"{faker.last_name()} {faker.last_name()}",
                    tipo="capitan",
                )
                cantidad_hab = random.randint(1, len(habilidades))
                random.shuffle(habilidades)
                for hab in habilidades[:cantidad_hab]:
                    capitan.habilidad.add(hab)
                capitanes.append(capitan)

            # 4. Crear 90 tripulantes con habilidades aleatorias
            tripulantes = []
            for _ in range(90):
                tripulante = Usuario.objects.create(
                    nombre=faker.first_name(),
                    apellidos=f"{faker.last_name()} {faker.last_name()}",
                    tipo="tripulante",
                )
                cantidad_hab = random.randint(1, len(habilidades))
                random.shuffle(habilidades)
                for hab in habilidades[:cantidad_hab]:
                    tripulante.habilidad.add(hab)
                tripulantes.append(tripulante)

            # 5. Crear 10 naves (las 2 últimas quedan libres sin misión para probar endpoints)
            naves_datos = [
                ("SS Alborán", "Pequeña"),
                ("SS Ícaro", "Pequeña"),
                ("SS Magallanes", "Mediana"),
                ("SS Kepler", "Mediana"),
                ("SS Cristóbal Colón", "Grande"),
                ("SS Horizonte", "Grande"),
                ("SS Galileo", "Pequeña"),
                ("SS Cassini", "Mediana"),
                ("SS Voyager", "Grande"),
                ("SS Artemis", "Mediana"),
            ]
            naves = []
            for nombre_nave, nombre_tipo in naves_datos:
                nave, _ = Nave.objects.get_or_create(
                    nombre=nombre_nave,
                    defaults={"tipo": tipos_por_nombre[nombre_tipo]},
                )
                naves.append(nave)

            # 6. Crear 8 misiones de prueba (en curso y finalizadas) + exoplanetas
            ids_ocupados_en_curso = []

            planes = [
                {
                    "nave_idx": 0,
                    "en_curso": False,
                    "exito": True,
                    "exoplanetas": 2,
                    "fecha_inicio": date(2026, 9, 1),
                    "fecha_fin": date(2026, 9, 20),
                },
                {
                    "nave_idx": 1,
                    "en_curso": False,
                    "exito": False,
                    "exoplanetas": 0,
                    "fecha_inicio": date(2026, 9, 10),
                    "fecha_fin": date(2026, 9, 25),
                },
                {
                    "nave_idx": 2,
                    "en_curso": True,
                    "exito": None,
                    "exoplanetas": 0,
                    "fecha_inicio": date(2026, 11, 15),
                    "fecha_fin": None,
                },
                {
                    "nave_idx": 3,
                    "en_curso": False,
                    "exito": True,
                    "exoplanetas": 1,
                    "fecha_inicio": date(2026, 10, 1),
                    "fecha_fin": date(2026, 10, 18),
                },
                {
                    "nave_idx": 4,
                    "en_curso": True,
                    "exito": None,
                    "exoplanetas": 0,
                    "fecha_inicio": date(2026, 11, 18),
                    "fecha_fin": None,
                },
                {
                    "nave_idx": 5,
                    "en_curso": False,
                    "exito": True,
                    "exoplanetas": 3,
                    "fecha_inicio": date(2026, 8, 15),
                    "fecha_fin": date(2026, 9, 5),
                },
                {
                    "nave_idx": 6,
                    "en_curso": True,
                    "exito": None,
                    "exoplanetas": 0,
                    "fecha_inicio": date(2026, 11, 20),
                    "fecha_fin": None,
                },
                {
                    "nave_idx": 7,
                    "en_curso": False,
                    "exito": False,
                    "exoplanetas": 0,
                    "fecha_inicio": date(2026, 10, 5),
                    "fecha_fin": date(2026, 10, 12),
                },
            ]

            contador_misiones = 0
            for plan in planes:
                nave = naves[plan["nave_idx"]]
                num_cap = nave.tipo.num_capitanes

                # Elegimos cuántos tripulantes extra poner según el tipo de nave, algunas estarán enteras, otras a mitad y otras con la capacidad mínima
                if nave.tipo.nombre == "Pequeña":
                    num_trip = 3
                elif nave.tipo.nombre == "Mediana":
                    num_trip = random.randint(7, 9)
                else:
                    num_trip = random.randint(10, 20)

                if plan["en_curso"]:
                    # Filtro capitanes y tripulantes que no estén ya en una misión activa
                    caps_libres = []
                    for c in capitanes:
                        if c.id not in ids_ocupados_en_curso:
                            caps_libres.append(c)

                    trips_libres = []
                    for t in tripulantes:
                        if t.id not in ids_ocupados_en_curso:
                            trips_libres.append(t)

                    if len(caps_libres) < num_cap or len(trips_libres) < num_trip:
                        continue

                    random.shuffle(caps_libres)
                    random.shuffle(trips_libres)
                    caps_elegidos = caps_libres[:num_cap]
                    trips_elegidos = trips_libres[:num_trip]

                    for u in caps_elegidos:
                        ids_ocupados_en_curso.append(u.id)
                    for u in trips_elegidos:
                        ids_ocupados_en_curso.append(u.id)
                else:
                    caps_copia = list(capitanes)
                    trips_copia = list(tripulantes)
                    random.shuffle(caps_copia)
                    random.shuffle(trips_copia)

                    caps_elegidos = caps_copia[:num_cap]
                    trips_elegidos = trips_copia[:num_trip]

                contador_misiones += 1
                mision = Mision.objects.create(
                    nombre=f"Expedición {faker.word().capitalize()}-{contador_misiones}",
                    fecha_inicio=plan["fecha_inicio"],
                    fecha_fin=plan["fecha_fin"],
                    exito=plan["exito"],
                    id_nave=nave,
                )

                for cap in caps_elegidos:
                    mision.usuarios.add(cap)
                for trip in trips_elegidos:
                    mision.usuarios.add(trip)

                # Solo creamos exoplanetas si la misión terminó y tuvo éxito
                if not plan["en_curso"] and plan["exito"] is True:
                    for _ in range(plan["exoplanetas"]):
                        Exoplaneta.objects.create(
                            nombre=f"{faker.last_name()}-{random.randint(100, 999)}b",
                            id_mision=mision,
                        )

            print(
                f"Datos creados correctamente: {len(capitanes)} capitanes, "
                f"{len(tripulantes)} tripulantes, {len(naves)} naves, "
                f"{contador_misiones} misiones y {Exoplaneta.objects.count()} exoplanetas."
            )

        except Exception as e:
            print(f"Ha ocurrido un error: {e}")
