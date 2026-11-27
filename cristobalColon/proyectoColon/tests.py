from django.test import TestCase

from .models import Usuario, Habilidad

# Create your tests here.
class usuarioTest(TestCase):

    def setUp(self):
        # Estos objetos estarán disponibles en cada test
        self.habilidad_1 = Habilidad.objects.create(nombre="Misiones largas")
        self.habilidad_2 = Habilidad.objects.create(nombre="Explorador de cortas distancias")
        self.habilidad_3 = Habilidad.objects.create(nombre="Conflictivo")
        self.habilidad_4 = Habilidad.objects.create(nombre="Cocinero")
        self.habilidad_5 = Habilidad.objects.create(nombre="Mantenimiento")

    def test_crear_usuario_api(self):
        datos = {
            "nombre": "Hernán",
            "apellidos": "Cortés",
            "tipo": "capitan",
            "habilidad": ["Misiones largas", "Explorador de cortas distancias","Conflictivo"]
        }

        respuesta = self.client.post(
            "/api/crearusuario/",
            data=datos,

            content_type="application/json"
        )

        self.assertEqual(respuesta.status_code, 201, respuesta.content.decode('utf-8'))
        self.assertEqual(Usuario.objects.count(), 1)

    def test_no_permitir_get(self):
        respuesta = self.client.get("/api/crearusuario/")

        self.assertEqual(respuesta.status_code, 405)

    def test_json_incorrecto(self):
        respuesta = self.client.post(
            "/api/crearusuario/",
            data="{json incorrecto}",
            content_type="application/json"
        )
        self.assertEqual(respuesta.status_code, 400, respuesta.content.decode('utf-8'))