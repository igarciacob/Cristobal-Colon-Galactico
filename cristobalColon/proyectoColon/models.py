from django.db import models


# Create your models here.

class Tipo(models.Model):
    nombre = models.CharField(max_length=100)
    num_capitanes = models.IntegerField()
    capacidad_min = models.IntegerField()
    capacidad_max = models.IntegerField()


class Nave(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)


class Mision(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    exito = models.BooleanField()
    id_nave = models.ForeignKey(Nave, on_delete=models.CASCADE)


class Exoplaneta(models.Model):
    nombre = models.CharField(max_length=100)
    id_mision = models.ForeignKey(Mision, on_delete=models.CASCADE)
