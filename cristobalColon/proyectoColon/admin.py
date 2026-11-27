from django.contrib import admin
from .models import Mision, Tipo, Nave, Exoplaneta, Habilidad, Usuario

# Register your models here.
admin.site.register(Tipo)
admin.site.register(Nave)
admin.site.register(Mision)
admin.site.register(Exoplaneta)
admin.site.register(Habilidad)
admin.site.register(Usuario)