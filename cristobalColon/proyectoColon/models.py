from django.db import models


# Create your models here.

class Tipos(models.Model):
    nombre = models.CharField(max_length=100)
    num_capitanes = models.IntegerField()
    capacidad_min = models.IntegerField()
    capacidad_max = models.IntegerField()


class Naves(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.ForeignKey(Tipos, on_delete=models.CASCADE)


class Misiones(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    exito = models.BooleanField()
    id_nave = models.ForeignKey(Naves, on_delete=models.CASCADE)


class Exoplanetas(models.Model):
    nombre = models.CharField(max_length=100)
    id_mision = models.ForeignKey(Misiones, on_delete=models.CASCADE)
