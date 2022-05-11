from django.contrib import admin

# Register your models here.
from combiapp.models import *

admin.site.register(Chofer)
admin.site.register(Cliente)
admin.site.register(Lugar)
admin.site.register(Ruta)
admin.site.register(Viaje)
admin.site.register(Combi)
admin.site.register(InsumoComestible)