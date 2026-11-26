from django.db import models
from django.db.models import Q


# Create your models here.

class Tipo(models.Model):
    nombre = models.CharField(max_length=100)
    num_capitanes = models.IntegerField()
    capacidad_min = models.IntegerField()
    capacidad_max = models.IntegerField()


class Nave(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)



#Habilidades
class Habilidad(models.Model):
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Habilidad"
        verbose_name_plural = "Habilidades"

    def __str__(self):
        return f"{self.id} {self.nombre}"
#Usuarios
class Usuario (models.Model):
    nombre = models.CharField (max_length = 100)
    apellidos = models.CharField (max_length = 100)
    tipo = models.CharField(max_length=25)
    habilidad = models.ManyToManyField (Habilidad, blank=True)

    class Meta:
        constraints = [ models.CheckConstraint(
                condition=Q(tipo__in=['tripulante', 'capitan']),
                name='tipo_valido'
            ),]


    def __str__(self):
        return f"{self.id} {self.nombre} {self.apellidos}"


class Mision(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    exito = models.BooleanField()
    id_nave = models.ForeignKey(Nave, on_delete=models.CASCADE)
    usuarios= models.ManyToManyField(Usuario, blank=True)

class Exoplaneta(models.Model):
    nombre = models.CharField(max_length=100)
    id_mision = models.ForeignKey(Mision, on_delete=models.CASCADE)
