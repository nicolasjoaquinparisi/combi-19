"""sc19 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.views.generic import TemplateView
from combiapp.views import *

urlpatterns = [
    path('', index),
    path('login/', login),
    path('logout/', logout),
    path('about/', TemplateView.as_view(template_name='sobre-combi19.html')),

    # Listar
    path('listar-chofer/', listar_chofer),
    path('listar-combi/', listar_combi),
    path('listar-insumo-comestible/', listar_insumo_comestible),
    path('listar-lugar/', listar_lugar),
    path('listar-ruta/', listar_ruta),
    path('listar-viaje/', listar_viaje),

    # Altas
    path('alta-usuario/', altaUsuario),
    path('alta-chofer/', alta_chofer),
    path('alta-combi/', alta_combi),
    path('alta-insumo-comestible/', alta_insumo_comestible),
    path('alta-lugar/', alta_lugar),
    path('alta-ruta/', alta_ruta),
    path('alta-viaje/', alta_viaje),

    # Editar
    path('editar-usuario/', modificar_usuario),
    path('editar-chofer/<int:object_id>', editar_chofer),
    path('editar-combi/<int:object_id>', editar_combi),
    path('editar-insumo-comestible/<int:object_id>', editar_insumo_comestible),
    path('editar-lugar/<int:object_id>', editar_lugar),
    path('editar-ruta/<int:object_id>', editar_ruta),
    path('editar-viaje/<int:object_id>', editar_viaje),

    # Eliminar
    path('eliminar-chofer/<int:obj_id>', eliminar_chofer, name="eliminar-chofer"),
    path('eliminar-combi/<int:obj_id>', eliminar_combi, name="eliminar-combi"),
    path('eliminar-insumo-comestible/<int:obj_id>', eliminar_insumo_comestible, name="eliminar-insumo-comestible"),
    path('eliminar-lugar/<int:obj_id>', eliminar_lugar, name="eliminar-lugar"),
    path('eliminar-ruta/<int:obj_id>', eliminar_ruta, name="eliminar-ruta"),
    path('eliminar-viaje/<int:obj_id>', eliminar_viaje, name="eliminar-viaje"),
    path('eliminar-usuario/', eliminar_usuario, name="eliminar-usuario"),


    # Perfiles
    path('perfil/', perfil),

    # Cliente
    path('buscar-viajes/<int:origen_id>/<int:destino_id>/<str:fecha>', buscar_viajes),
    path('comprar-pasaje/<int:obj_id>', comprar_pasaje),
    path('mis-pasajes/', mis_pasajes),
    path('ver-pasaje/<int:pasaje_id>/', ver_pasaje),
    path('cancelar-pasaje/<int:obj_id>/', cancelar_pasaje, name="cancelar-pasaje"),

    #Comentarios
    path('comentarios/', alta_comentario),
    path('mis-comentarios/', mis_comentarios),
    path('editar-comentario/<int:obj_id>/<str:texto>', editar_comentario, name="editar-comentario"),
    path('eliminar-comentario/<int:obj_id>', eliminar_comentario, name="eliminar-comentario"),

    # Chofer
    path('proximos-viajes/', listar_proximos_viajes),
    path('viajes-realizados/', listar_viajes_realizados),
    path('listar-pasajeros/<int:viaje_id>', listar_pasajeros),
    path('no-se-presento/<int:pasaje_id>', no_se_presento),
    path('registrar-diagnostico/<int:pasaje_id>/<int:viaje_id>', registrar_diagnostico),
    path('buscar-email/<int:viaje_id>', buscar_email, name="buscar-email"),
    path('alta-usuario-express/<int:viaje_id>/<str:email>', alta_express),
    path('vender-pasaje-express/<int:viaje_id>/<str:email>', vender_pasaje_express),

    #Diagnósticos
    path('aceptar-pasaje/<int:pasaje_id>', aceptar_pasaje),
    path('rechazar-pasaje/<int:pasaje_id>', rechazar_pasaje),

    #Estado de viajes
    path('iniciar-viaje/<int:obj_id>/', iniciar_viaje, name="iniciar-viaje"),
    path('cancelar-viaje/<int:obj_id>/', cancelar_viaje, name="cancelar-viaje"),
    path('finalizar-viaje/<int:obj_id>/', finalizar_viaje),

    path('historial-viajes/', historial_viajes),
    path('historial-testeos/', historial_testeos),

    # Django
    path('admin/clearcache/', include('clearcache.urls')),
    path('admin/', admin.site.urls),

    # Django Browser Reload
    path("__reload__/", include("django_browser_reload.urls"))
]
