from django.contrib import auth
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from combiapp.models import Chofer, Combi, InsumoComestible, Lugar, Ruta, Viaje, Tarjeta, Cliente, User, Comentario, \
    Pasaje, VentaInsumo, ValidationError
from combiapp.forms import BuscarEmailForm, LoginForm, ClienteForm, TarjetaForm, datetime, AltaExpresForm, TesteoCovidPositivo

import json
import pytz


def index(request):
    return render(request, 'index.html', {'lugares': Lugar.find_all()})


def login(request):
    if request.method == 'POST':
        user = auth.authenticate(email=request.POST['email'], password=request.POST['password'])
        if user is not None and user.habilitado:
            auth.login(request, user)
            response_data = {
                'result': 'Login',
                'message': 'Login'
            }
            return HttpResponse(json.dumps(response_data))
        else:
            response_data = {
             'result': 'Error',
             'message': 'Los datos ingresados son inválidos.'
            }

            if LoginForm(request.POST).campos_vacios():
                response_data = {
                    'result': 'Error',
                    'message': 'Se deben completar los campos.'
                }
            return HttpResponse(json.dumps(response_data))
    else:
        formLogin = LoginForm()
    return render(request, 'funcionalidades/login.html', {'formLogin': formLogin})


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')


@login_required
def listar(request, template_name, object_type):
    if not request.user.is_superuser:
        raise Http404

    objetos = object_type.objects.filter(habilitado=True)
    return render(request, template_name, {'objetos': objetos})


@login_required
def listar_chofer(request):
    return listar(request, 'funcionalidades/admin/listar-chofer.html', Chofer)


@login_required
def listar_combi(request):
    return listar(request, 'funcionalidades/admin/listar-combi.html', Combi)


@login_required
def listar_insumo_comestible(request):
    return listar(request, 'funcionalidades/admin/listar-insumo-comestible.html', InsumoComestible)


@login_required
def listar_lugar(request):
    return listar(request, 'funcionalidades/admin/listar-lugar.html', Lugar)


@login_required
def listar_ruta(request):
    return listar(request, 'funcionalidades/admin/listar-ruta.html', Ruta)


@login_required
def listar_viaje(request):
    if not request.user.is_superuser:
        raise Http404

    viajes_habilitados = Viaje.objects.filter(habilitado=True)
    viajes_deshabilitados = Viaje.objects.filter(habilitado=False)

    return render(request, 'funcionalidades/admin/listar-viaje.html', {'viajes_habilitados': viajes_habilitados, 'viajes_deshabilitados':viajes_deshabilitados})
    

@login_required
def editar(request, template_name, object_type, object_id):
    if not request.user.is_superuser:
        raise Http404

    if object_id is None:
        obj = object_type()
    else:
        try:
            obj = object_type.objects.get(pk=object_id)
        except ObjectDoesNotExist:
            raise Http404
    
    if request.method == 'GET':
        context = obj.get_context() 
        context.update({'object': obj})
        response = render(request, template_name, context)
    elif request.method == 'POST':
        result, message = obj.fill_and_save(dict(request.POST.items()))
        response = JsonResponse({
            'result': 'OK' if result else 'Error',
            'message': message
        })
    else:
        raise Http404
    
    return response


@login_required
def editar_chofer(request, object_id=None):
    return editar(request, 'funcionalidades/admin/editar-chofer.html', Chofer, object_id)


@login_required
def editar_combi(request, object_id=None):
    return editar(request, 'funcionalidades/admin/editar-combi.html', Combi, object_id)


@login_required
def editar_insumo_comestible(request, object_id=None):
    return editar(request, 'funcionalidades/admin/editar-insumo-comestible.html', InsumoComestible, object_id)


@login_required
def editar_lugar(request, object_id=None):
    return editar(request, 'funcionalidades/admin/editar-lugar.html', Lugar, object_id)


@login_required
def editar_ruta(request, object_id=None):
    return editar(request, 'funcionalidades/admin/editar-ruta.html', Ruta, object_id)


@login_required
def editar_viaje(request, object_id=None):
    return editar(request, 'funcionalidades/admin/editar-viaje.html', Viaje, object_id)


@login_required
def alta_chofer(request):
    return editar_chofer(request)


@login_required
def alta_combi(request):
    return editar_combi(request)


@login_required
def alta_insumo_comestible(request):
    return editar_insumo_comestible(request)


@login_required
def alta_lugar(request):
    return editar_lugar(request)


@login_required
def alta_ruta(request):
    return editar_ruta(request)


@login_required
def alta_viaje(request):
    return editar_viaje(request)


def altaUsuario(request):
    if request.method == 'POST':


        formCliente = ClienteForm(request.POST)

        isGoldUser = request.POST.get('checkbox', '') == 'True'

        if isGoldUser:
            formTarjeta = TarjetaForm(request.POST)

            if formCliente.validar_cliente():

                if formTarjeta.validar_tarjeta():

                    t = formTarjeta.cleaned_data
                    print(t)

                    tarjeta = Tarjeta().create_tarjeta(t['numero'], t['titular'], formTarjeta.data['fecha_vencimiento'])

                    f = formCliente.cleaned_data
                    Cliente.objects.create_cliente(f['email'], f['first_name'], f['last_name'], f['dni'], f['fecha_nacimiento'], tarjeta, f['password'])

                    responseData = {
                        'result': 'Alta exitosa',
                        'message': 'Se ha dado el alta con exito al usuario gold ' + f['email']
                    }

                else:
                    context = {
                        'formCliente': formCliente,
                        'formTarjeta': formTarjeta,
                    }
                    if not formTarjeta.validar_tarjeta():
                        responseData = {
                            'result': 'Error',
                            'message': 'Los datos de la tarjeta no son validos.'
                        }

                return HttpResponse(json.dumps(responseData))

            else:
                context = {
                    'formCliente': formCliente,
                    'formTarjeta': formTarjeta,
                }
                if formCliente.validacion_de_contraseña_es_invalida(formCliente.data['password'], formCliente.data['confirmationPassword']):
                    responseData = {
                        'result': 'Error',
                        'message': 'La contraseña ingresada es inválida.'
                    }
                if formCliente.validar_campos_no_vacios():
                    responseData = {
                        'result': 'Error',
                        'message': 'Debe completar todos los campos'
                    }
                if formCliente.existe_cliente_con_mismo_nombre(None):
                    responseData = {
                        'result': 'Error',
                        'message': 'El nombre de usuario ingresado se encuentra en uso.'
                    }
                if formCliente.es_menor_de_edad():
                    responseData = {
                        'result': 'Error',
                        'message': 'No se puede dar de alta a personas menores de edad.'
                    }

                return HttpResponse(json.dumps(responseData))
        else:
            if formCliente.validar_cliente():
                f = formCliente.cleaned_data

                cliente = Cliente.objects.create_cliente(f['email'], f['first_name'], f['last_name'], f['dni'], f['fecha_nacimiento'], None, f['password'])

                responseData = {
                        'result': 'Alta exitosa',
                        'message': 'Se ha dado el alta con exito al usuario ' + f['email']
                }

            else:
                context = {
                    'formCliente': formCliente,
                    'formTarjeta': TarjetaForm(),
                }
                if formCliente.validar_campos_no_vacios():
                    responseData = {
                        'result': 'Error',
                        'message': 'Debe completar todos los campos'
                    }
                if formCliente.validacion_de_contraseña_es_invalida(formCliente.data['password'], formCliente.data['confirmationPassword']):
                    responseData = {
                        'result': 'Error',
                        'message': 'La contraseña ingresada es inválida.'
                    }
                if formCliente.existe_cliente_con_mismo_nombre(None):
                    responseData = {
                        'result': 'Error',
                        'message': 'El nombre de usuario ingresado se encuentra en uso.'
                    }
                if formCliente.es_menor_de_edad():
                    responseData = {
                        'result': 'Error',
                        'message': 'No se puede dar de alta a personas menores de edad.'
                    }
            return HttpResponse(json.dumps(responseData))
    else:
        context = {
            'formCliente': ClienteForm(),
            'formTarjeta': TarjetaForm(),
        }

        response = {
            'result': 'Error',
            'message': 'Los datos ingresados no son validos'
        }

    return render(request, 'funcionalidades/usuarios/usuario-anonimo/alta-usuario.html', context)

@login_required()
def modificar_usuario(request):
    if request.method == 'POST':
        formCliente = ClienteForm(request.POST)

        #Se verifica si es usuario común o gold
        if request.user.cliente.tarjeta:

            # Se valida y modifican los datos del usuario
            if formCliente.validar_cliente(request.user.email):
                formTarjeta = TarjetaForm(request.POST)

                # Se modifican los datos de la tarjeta si se hicieron cambios
                if formTarjeta.validar_tarjeta():
                    tarjeta = Tarjeta.get_instance(request.user.cliente.tarjeta.numero)
                    tarjeta.modificar(request.POST)

                    cliente = Cliente.get_instance(request.user.email)
                    cliente.modificar(request.POST)

                    user = auth.authenticate(email=request.POST['email'], password=request.POST['password'])
                    auth.login(request, user)

                    responseData = {
                        'result': 'Modificacion',
                        'message': 'Se ha modificado al usuario gold ' + request.user.email
                    }

                else:
                    context = {
                        'formCliente': formCliente,
                        'formTarjeta': formTarjeta,
                    }
                    if not formTarjeta.validar_tarjeta():
                        responseData = {
                            'result': 'Error',
                            'message': 'Los datos de la tarjeta no son validos.'
                        }

                return HttpResponse(json.dumps(responseData))

            else:
                context = {
                    'formCliente': formCliente,
                    'formTarjeta': TarjetaForm(),
                }
                if formCliente.validar_campos_no_vacios():
                    responseData = {
                        'result': 'Error',
                        'message': 'Debe completar todos los campos'
                    }
                if formCliente.validacion_de_contraseña_es_invalida(formCliente.data['password'],
                                                                    formCliente.data['confirmationPassword']):
                    responseData = {
                        'result': 'Error',
                        'message': 'La contraseña ingresada es inválida.'
                    }
                if formCliente.existe_cliente_con_mismo_nombre(request.user.email):
                    responseData = {
                        'result': 'Error',
                        'message': 'El nombre de usuario ingresado se encuentra en uso.'
                    }
                if formCliente.es_menor_de_edad():
                    responseData = {
                        'result': 'Error',
                        'message': 'No se puede dar de alta a personas menores de edad.'
                    }

                return HttpResponse(json.dumps(responseData))

        else:
            if formCliente.validar_cliente(request.user.email):
                cliente = Cliente.get_instance(request.user.email)
                cliente.modificar(request.POST)

                user = auth.authenticate(email=request.POST['email'], password=request.POST['password'])
                auth.login(request, user)

                responseData = {
                    'result': 'Modificacion',
                    'message': 'Se ha modificado al usuario ' + request.user.email
                }

            else:
                context = {
                    'formCliente': formCliente,
                    'formTarjeta': TarjetaForm(),
                }
                if formCliente.validar_campos_no_vacios():
                    responseData = {
                        'result': 'Error',
                        'message': 'Debe completar todos los campos'
                    }
                if formCliente.validacion_de_contraseña_es_invalida(formCliente.data['password'],
                                                                    formCliente.data['confirmationPassword']):
                    responseData = {
                        'result': 'Error',
                        'message': 'La contraseña ingresada es inválida.'
                    }
                if formCliente.existe_cliente_con_mismo_nombre(request.user.email):
                    responseData = {
                        'result': 'Error',
                        'message': 'El nombre de usuario ingresado se encuentra en uso.'
                    }
                if formCliente.es_menor_de_edad():
                    responseData = {
                        'result': 'Error',
                        'message': 'No se puede dar de alta a personas menores de edad.'
                    }

            return HttpResponse(json.dumps(responseData))

    else:
        context = {'formCliente': ClienteForm(initial={'first_name': request.user.first_name,
                                                        'last_name': request.user.last_name,
                                                        'email':  request.user.email,
                                                        'dni':  request.user.cliente.dni,
                                                       'fecha_nacimiento': request.user.cliente.fecha_nacimiento})}
        if request.user.cliente.tarjeta is not None:
            context['formTarjeta'] = TarjetaForm(initial={'numero': request.user.cliente.tarjeta.numero,
                                                          'titular': request.user.cliente.tarjeta.titular,
                                                          'fecha_vencimiento': request.user.cliente.tarjeta.get_fecha_vencimiento})
    return render(request, 'funcionalidades/usuarios/usuario/modificar-usuario.html', context=context)

'''
def editar_comentario(request, object_id):
    if object_id is None:
        obj = Comentario()
    else:
        try:
            obj = Comentario.objects.get(pk=object_id)
        except ObjectDoesNotExist:
            raise Http404

    if request.method == 'GET':
        comentarios = Comentario.find_all()
        context = {'comentarios': comentarios}
        response = render(request, 'funcionalidades/usuarios/comentarios.html', context)
    elif request.method == 'POST':
        if request.user.is_anonymous:
            raise Http404
        obj.texto = request.POST['texto']
        obj.cliente = request.user.cliente
        obj.fecha = datetime.today()
        obj.hora = datetime.today().time()
        obj.save()
        return redirect('/comentarios')
    else:
        raise Http404

    return response
'''

def alta_comentario(request):
    if hasattr(request.user, 'chofer') or request.user.is_superuser:
        raise PermissionDenied

    if request.method == "POST":
        Comentario.create_comentario(request.user.cliente, request.POST['texto'])

    comentarios = Comentario.find_all()
    context = {'comentarios': comentarios}
    return render(request, 'funcionalidades/usuarios/comentarios.html', context)

def editar_comentario(request, obj_id, texto):
    comentario = Comentario.objects.filter(pk=obj_id).first()
    comentario.editar(texto)
    return redirect('/mis-comentarios')


@login_required()
def eliminar_chofer(request, obj_id):
    chofer = Chofer.objects.filter(pk=obj_id).first()

    combi_con_chofer = Combi.objects.filter(chofer=chofer.pk).first()


    if combi_con_chofer is not None:
        if combi_con_chofer.habilitado:
            responseData = {
                'result': 'Error',
                'message': 'No se puede eliminar al chofer seleccionado ya que forma parte de una combi'
            }
            return JsonResponse(responseData)


    responseData = {
        'result': 'OK',
        'message': f'Se ha eliminado al chofer \'{chofer}\' de forma exitosa.'
    }
    chofer.delete()
    return JsonResponse(responseData)


@login_required()
def eliminar_combi(request, obj_id):


    combi = Combi.objects.filter(pk=obj_id).first()

    ruta_con_combi = Ruta.objects.filter(combi=combi.pk).first()


    if ruta_con_combi is not None:
        if ruta_con_combi.habilitado:
            responseData = {
                'result': 'Error',
                'message': 'No se puede eliminar la combi seleccionada ya que forma parte de una ruta'
            }
            return JsonResponse(responseData)



    responseData = {
        'result': 'OK',
        'message': f'Se ha eliminado la combi \'{combi}\' de forma exitosa.'
    }
    combi.delete()
    return JsonResponse(responseData)


@login_required()
def eliminar_insumo_comestible(request, obj_id):


    insumo = InsumoComestible.objects.filter(pk=obj_id).first()


    responseData = {
        'result': 'OK',
        'message': f'Se ha eliminado el insumo comestible \'{insumo}\' de forma exitosa.'
    }

    insumo.delete()
    return JsonResponse(responseData)



@login_required()
def eliminar_lugar(request, obj_id):
    lugar = Lugar.objects.filter(pk=obj_id).first()

    ruta_con_lugar_como_origen = Ruta.objects.filter(origen=lugar.pk).first()
    ruta_con_lugar_como_destino = Ruta.objects.filter(destino=lugar.pk).first()

    if ruta_con_lugar_como_origen is not None:
        if ruta_con_lugar_como_origen.habilitado:
            responseData = {
                'result': 'Error',
                'message': 'No se puede eliminar el lugar seleccionado ya que forma parte de una ruta'
            }
            return JsonResponse(responseData)

    if ruta_con_lugar_como_destino is not None:
        if ruta_con_lugar_como_destino.habilitado:
            responseData = {
                'result': 'Error',
                'message': 'No se puede eliminar el lugar seleccionado ya que forma parte de una ruta'
            }
            return JsonResponse(responseData)

    responseData = {
        'result': 'OK',
        'message': f'Se ha eliminado el lugar \'{lugar}\' de forma exitosa.'
    }

    lugar.delete()
    return JsonResponse(responseData)


@login_required()
def eliminar_ruta(request, obj_id):
    ruta = Ruta.objects.filter(pk=obj_id).first()

    viaje_con_ruta = Viaje.objects.filter(ruta=ruta.pk).first()

    if viaje_con_ruta is not None:
        if viaje_con_ruta.habilitado:
            responseData = {
                'result': 'Error',
                'message': 'No se puede eliminar la ruta seleccionada ya que forma parte de una viaje.'
            }
            return JsonResponse(responseData)

    responseData = {
        'result': 'OK',
        'message': f'Se ha eliminado la ruta \'{ruta}\' de forma exitosa.'
    }


    ruta.delete()
    return JsonResponse(responseData)


@login_required()
def eliminar_viaje(request, obj_id):
    viaje = Viaje.objects.filter(pk=obj_id).first()
    return JsonResponse(viaje.delete())


@login_required()
def eliminar_usuario(request):
    for pasaje in Pasaje.get_pasajes_de_cliente(request.user.email):
        if pasaje.get_estado == "Pendiente":
            responseData = {
                'result': 'Error',
                'message': 'No se puede dar de baja al usuario debido a que tiene viajes pendientes'
            }
            return JsonResponse(responseData)

    cliente = request.user.cliente
    tarjeta = cliente.tarjeta

    comentarios_del_usuario = Comentario.objects.filter(cliente=cliente.pk)
    for comentario in comentarios_del_usuario:
        comentario.delete()
        comentario.save()

    auth.logout(request)

    if tarjeta is not None:
        tarjeta.delete()

    cliente.delete()

    responseData = {
        'result': 'OK',
        'message': 'Se dió de baja el usuario'
    }
    return JsonResponse(responseData)

@login_required()
def eliminar_comentario(request, obj_id):

    comentario = Comentario.objects.filter(pk=obj_id).first()

    comentario.delete()

    responseData = {
        'result': 'OK',
        'message': 'Se ha eliminado el comentario  de forma exitosa.'
    }

    

    return JsonResponse(responseData)


@login_required()
def perfil(request):
    return render(request, 'funcionalidades/usuarios/perfil/perfil.html')

def buscar_viajes(request, origen_id, destino_id, fecha):
    viajes = Viaje.get_viajes_disponibles(origen_id, destino_id, fecha)
    context = {'viajes' : viajes }
    return render(request, 'funcionalidades/usuarios/buscar-viajes.html', context=context)


def comprar_pasaje(request, obj_id):
    if request.user.is_authenticated:
        if hasattr(request.user, 'chofer') or request.user.is_superuser:
            raise PermissionDenied

        viaje = Viaje.objects.get(pk=obj_id)
        if viaje is None:
            return Http404

        if request.method == 'POST':
            if request.user.cliente.esta_bloqueado:
                response = JsonResponse({
                    'result': 'Error',
                    'message': 'No puede realizar la compra del pasaje debido a que su cuenta está bloqueada'
                })
                return response

            try:
                p = request.POST
                if not p['cc-name'] or not p['cc-number'] or not p['cc-expiration'] or not p['cc-cvv']:
                    raise ValidationError('Se deben completar los datos de la tarjeta de credito.')

                if viaje.pasajes_vendidos >= viaje.ruta.combi.asientos:
                    raise ValidationError('El viaje ya tiene todos los asientos ocupados.')

                pasaje = Pasaje(cliente=request.user.cliente, viaje=viaje)
                total = viaje.precio
                ventas = []
                for pk, cant in p.items():
                    if not pk.startswith('i-') or int(cant) == 0:
                        continue
                    pk = pk[2:]
                    insumo = InsumoComestible.find_pk(pk)
                    venta = VentaInsumo(pasaje=pasaje, insumo=insumo, cantidad=int(cant))
                    ventas.append(venta)
                    total += venta.precio
                if request.user.cliente.tarjeta is not None:
                    total *= 0.9
                pasaje.precio = total 
                pasaje.save()
                for venta in ventas:
                    venta.save()
                viaje.pasajes_vendidos += 1
                viaje.save()
            except ValidationError as e:
                response = JsonResponse({
                    'result': 'Error',
                    'message': str(e)
                })
            else:
                response = JsonResponse({
                    'result': 'OK',
                    'message': f'Se compro un pasaje para el viaje \'{viaje}\' a ${total:.0f}.'
                })
        else:
            insumos_comestibles = InsumoComestible.objects.filter(habilitado=True)
            context = {
                'insumos' : insumos_comestibles,
                'viaje': viaje,
                'fecha_de_salida': viaje.fecha_de_salida.strftime('%Y-%m-%d'),
                'hora_de_salida': viaje.hora_de_salida.strftime('%H:%M')
            }

            response = render(request, 'funcionalidades/usuarios/usuario/comprar-pasaje.html', context=context)

        return response
    else:
        return redirect('/login')

@login_required()
def ver_pasaje(request, pasaje_id):
    if hasattr(request.user, 'chofer') or request.user.is_superuser:
        raise PermissionDenied

    pasaje = Pasaje.objects.filter(pk=pasaje_id).first()
    insumos_comestibles = pasaje.ventas_de_insumos

    puede_cancelar = True
    if pasaje.get_estado == "Cancelado" or pasaje.get_estado == "Finalizado":
        puede_cancelar = False

    context = {'pasaje': pasaje, 'insumos': insumos_comestibles, 'puede_cancelar':puede_cancelar}
    return render(request, 'funcionalidades/usuarios/usuario/ver-pasaje.html', context=context)

@login_required()
def mis_comentarios(request):
    if hasattr(request.user, 'chofer') or request.user.is_superuser:
        raise PermissionDenied

    comentarios = request.user.cliente.comentarios
    context = {'comentarios': comentarios}
    return render(request, 'funcionalidades/usuarios/usuario/mis-comentarios.html', context=context)

@login_required()
def mis_pasajes(request):
    if hasattr(request.user, 'chofer') or request.user.is_superuser:
        raise PermissionDenied

    pasajes = Pasaje.get_pasajes_de_cliente(request.user.get_username())
    context = {'pasajes' : pasajes}
    return render(request, 'funcionalidades/usuarios/usuario/mis-pasajes.html', context=context)

@login_required()
def finalizar_viaje(request, obj_id):
    viaje = Viaje.objects.filter(pk=obj_id).first()
    viaje.finalizar()
    return redirect('/proximos-viajes')

@login_required()
def cancelar_pasaje(request, obj_id):
    pasaje = Pasaje.objects.filter(pk=obj_id).first()
    return JsonResponse(pasaje.reembolsar())

@login_required()
def cancelar_viaje(request, obj_id):
    viaje = Viaje.objects.filter(pk=obj_id).first()
    return JsonResponse(viaje.cancelar())

@login_required()
def iniciar_viaje(request, obj_id):

    viaje = Viaje.objects.filter(pk=obj_id).first()
    pendiente = Pasaje.get_pasajes_pendientes(obj_id)
    iniciado = Pasaje.get_pasajes_aceptados(obj_id)

    if request.user.chofer.tiene_viaje_iniciado:
        responseData = {
            'result': 'Error',
            'message': 'No se puede iniciar el viaje seleccionado dado que tienes otro viaje iniciado'
        }
        return JsonResponse(responseData)

    if pendiente:
        responseData = {
            'result': 'Error',
            'message': 'No se puede iniciar el viaje seleccionado dado que aun hay pasajes que no fueron verificados'
        }
        return JsonResponse(responseData)

    if iniciado:
        return JsonResponse(viaje.iniciar())
    else:
        responseData = {
            'result': 'Error',
            'message': 'No se puede iniciar el viaje seleccionado dado que aun no hay pasajes aprobados'
        }
        return JsonResponse(responseData)


@login_required()
def listar_proximos_viajes(request):
    if hasattr(request.user, 'cliente') or request.user.is_superuser:
        raise PermissionDenied

    proximos_viajes = request.user.chofer.get_proximos_viajes

    #Como no se puede realizar la comparación en el template con el tamaño de la lista, guarde el resultado en vacia
    vacia = len(proximos_viajes) == 0
    context = {'viajes' : proximos_viajes, 'esta_vacia' : vacia }

    return render(request, 'funcionalidades/choferes/listar-proximos-viajes.html', context)

@login_required()
def listar_viajes_realizados(request):
    if hasattr(request.user, 'cliente') or request.user.is_superuser:
        raise PermissionDenied

    viajes_realizados = request.user.chofer.get_viajes_realizados

    #Como no se puede realizar la comparación en el template con el tamaño de la lista, guarde el resultado en vacia
    vacia = len(viajes_realizados) == 0
    context = {'viajes' : viajes_realizados, 'esta_vacia' : vacia }

    return render(request, 'funcionalidades/choferes/listar-viajes-realizados.html', context)

@login_required()
def listar_pasajeros(request, viaje_id):
    if hasattr(request.user, 'cliente') or request.user.is_superuser:
        raise PermissionDenied

    viaje = Viaje.objects.filter(pk=viaje_id).first()
    print(viaje)
    pasajes = viaje.pasajes

    # Como no se puede realizar la comparación en el template con el tamaño de la lista, guarde el resultado en vacia
    vacia = len(pasajes) == 0

    puede_registrar_sintomas_o_registrar_ausente = not(viaje.estado == "Iniciado" or viaje.estado == "Finalizado")

    context = {'pasajes' : pasajes, 'viaje' : viaje, 'esta_vacia' : vacia, 'puede_registrar_sintomas_o_registrar_ausente' : puede_registrar_sintomas_o_registrar_ausente }
    return render(request, 'funcionalidades/choferes/listar-pasajeros.html', context)


@login_required()
def no_se_presento(request, pasaje_id):
    pasaje = Pasaje.objects.filter(pk=pasaje_id).first()
    pasaje.registrar_ausencia()
    return redirect('/listar-pasajeros/' + str(pasaje.viaje.pk))


@login_required()
def buscar_email(request, viaje_id):
    if hasattr(request.user, 'cliente') or request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        form = BuscarEmailForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']

            if not email:
                responseData = {
                    'result': 'Error',
                    'message': 'Debe ingresar un email.'
                }
                return JsonResponse(responseData)

            """Se verifica si el mail ingresado corresponde a un chofer"""
            es_chofer = Chofer.objects.filter(email=email).exists()
            if es_chofer:
                responseData = {
                    'result': 'Error',
                    'message': 'El email ingresado corresponde a un chofer, y por lo tanto, no se le puede vender un pasaje.'
                }
                return JsonResponse(responseData)

            """Se verifica si el mail ingresado corresponde al admin"""
            admin = User.objects.filter(email=email).first()
            if admin != None:
                es_admin = admin.is_superuser
                if es_admin:
                    responseData = {
                        'result': 'Error',
                        'message': 'El email ingresado corresponde al admin.'
                    }
                    return JsonResponse(responseData)

            """Se verifica si el mail ingresado corresponde a un cliente"""
            existe = Cliente.objects.filter(email=email).exists()

            if not existe:
                responseData = {
                    'result': 'Warning',
                    'message': 'El email ingresado no existe. Deberá crearle una cuenta a la persona.',
                    'viaje_id': str(viaje_id),
                    'email': str(email),
                }
                return JsonResponse(responseData)

            responseData = {
                    'result': 'OK'
                }
            return JsonResponse(responseData)
        
        responseData = {
                    'result': 'Error',
                    'message': 'Debe ingresar un email.'
                }
        return JsonResponse(responseData)

    viaje = Viaje.objects.filter(pk=viaje_id).first()
    context = {'viaje' : viaje, 'form' : BuscarEmailForm() }
    return render(request, 'funcionalidades/choferes/vender-pasaje-express.html', context)

@login_required()
def alta_express(request, viaje_id, email):

    if request.method == 'POST':

        form = AltaExpresForm(request.POST)

        if form.validar_cliente():
            data = form.cleaned_data

            cliente = Cliente.objects.create_cliente(data['email'], '', '', data['dni'], data['fecha_nacimiento'],
                                   None, 'combi19.')

            viaje = Viaje.objects.filter(pk=viaje_id).first()

            if viaje.pasajes_vendidos >= viaje.ruta.combi.asientos:
                responseData = {
                    'result': 'Warning',
                    'message': 'Se ha dado el alta con exito al usuario ' + cliente.email + \
                                '. No se pudo realizar la venta del pasaje debido a que no hay más pasajes disponibles.'
                }
                return JsonResponse(responseData)

            pasaje = Pasaje(cliente=cliente, viaje=viaje)
            pasaje.precio = viaje.precio 
            pasaje.save()
            viaje.pasajes_vendidos += 1
            viaje.save()

            responseData = {
                'result': 'Venta exitosa',
                'message': 'Se ha dado el alta con exito al usuario \'' + cliente.email + '\'. '\
                            'Se vendió el pasaje de forma exitosa'
            }

            return JsonResponse(responseData)

        else:
            context = {
                'form': form
            }
            if form.es_menor_de_edad():
                responseData = {
                    'result': 'Error',
                    'message': 'El usuario debe ser mayor de edad'
                }
            if form.existe_cliente_con_mismo_nombre(None):
                responseData = {
                    'result': 'Error',
                    'message': 'Ya existe un usuario con el mismo nombre'
                }

        return HttpResponse(json.dumps(responseData))

    context = {
        'form': AltaExpresForm(),
        'email' : email,
        'viaje_id': viaje_id
    }
    responseData = {
        'result': 'Error',
        'message': 'Los datos ingresados no son validos.'
    }

    return render(request, 'funcionalidades/choferes/alta-usuario-express.html', context)


@login_required()
def vender_pasaje_express(request, viaje_id, email):
    if hasattr(request.user, 'cliente') or request.user.is_superuser:
        raise PermissionDenied


    """Se verifica si el mail ingresado corresponde a un chofer"""
    es_chofer = Chofer.objects.filter(email=email).exists()
    if es_chofer:
        responseData = {
            'result': 'Error',
            'message': 'El email ingresado corresponde a un chofer, y por lo tanto, no se le puede vender un pasaje.'
        }
        return JsonResponse(responseData)

    """Se verifica si el mail ingresado corresponde al admin"""
    admin = User.objects.filter(email=email).first()
    if admin != None:
        es_admin = admin.is_superuser
        if es_admin:
            responseData = {
                'result': 'Error',
                'message': 'El email ingresado corresponde al admin.'
            }
            return JsonResponse(responseData)

    cliente = Cliente.objects.filter(email=email).first()
    viaje = Viaje.objects.filter(pk=viaje_id).first()

    if cliente.esta_bloqueado:
        return JsonResponse({
            'result': 'Error',
            'message': 'El mail ingresado corresponde a un usuario que esta bloqueado.'
        })

    if viaje.pasajes_vendidos >= viaje.ruta.combi.asientos:
        responseData = {
            'result': 'Error',
            'message': 'No se ha podido llevar a cabo la venta del pasaje debido a que no hay más pasajes disponibles'
        }
        return JsonResponse(responseData)

    pasaje = Pasaje(cliente=cliente, viaje=viaje)
    pasaje.precio = viaje.precio 
    pasaje.save()
    viaje.pasajes_vendidos += 1
    viaje.save()

    responseData = {
        'result': 'OK',
        'message': 'Se ha realizado la venta del pasaje de forma exitosa'
    }

    return JsonResponse(responseData)

@login_required()
def registrar_diagnostico(request, pasaje_id, viaje_id):
    if hasattr(request.user, 'cliente') or request.user.is_superuser:
        raise PermissionDenied

    context = {'pasaje_id' : pasaje_id, 'viaje_id' : viaje_id}
    return render(request, 'funcionalidades/choferes/registrar-diagnostico.html', context)

login_required()
def aceptar_pasaje(request, pasaje_id):
    if hasattr(request.user, 'cliente') or request.user.is_superuser:
        raise PermissionDenied

    pasaje = Pasaje.objects.filter(pk=pasaje_id).first()
    pasaje.aceptar()

    responseData = {
        'result': 'OK',
        'message': 'Se ha registrado con éxito el diagnóstico del pasajero'
    }

    return JsonResponse(responseData)

login_required()
def rechazar_pasaje(request, pasaje_id):
    if hasattr(request.user, 'cliente') or request.user.is_superuser:
        raise PermissionDenied

    pasaje = Pasaje.objects.filter(pk=pasaje_id).first()

    pasaje.rechazar()

    responseData = {
            'result': 'Error',
            'message': 'Se ha rechazado el pasaje del pasajero. Su cuenta ha sido bloqueada por 15 días'
        }

    return JsonResponse(responseData)


@login_required
def historial_viajes(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    context = {
        'daterange': '-'
    }

    if request.method == 'GET':
        viajes = []
        context['busqueda'] = False
    else:
        post = dict(request.POST.items())

        for key in ('daterange', 'origen', 'destino', 'chofer'):
            context[key] = post[key]

        if post['daterange'] and post['daterange'] != '-':
            daterange = list(map(str.strip, post['daterange'].split('-')))
            desde = pytz.UTC.localize(datetime.strptime(daterange[0], '%d/%m/%Y'))
            hasta = pytz.UTC.localize(datetime.strptime(daterange[1], '%d/%m/%Y'))
        else:
            daterange = None
        origen = Lugar.find_pk(int(post['origen']))
        destino = Lugar.find_pk(int(post['destino']))
        chofer = Chofer.find_pk(int(post['chofer']))

        viajes = []
        for viaje in Viaje.find_all():
            if daterange and (viaje.fecha_de_salida < desde or viaje.fecha_de_salida > hasta):
                continue
            if origen and viaje.ruta.origen != origen:
                continue
            if destino and viaje.ruta.destino != destino:
                continue
            if chofer and viaje.ruta.combi.chofer != chofer:
                continue
            viajes.append(viaje)
        
        context['busqueda'] = True
    
    context['lugares'] = Lugar.find_all()
    context['choferes'] = Chofer.find_all()
    context['viajes'] = viajes

    return render(request, 'funcionalidades/admin/historial-viajes.html', context)


@login_required
def historial_testeos(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    context = {
        'daterange': '-'
    }

    if request.method == 'GET':
        context['busqueda'] = False
    elif request.method == 'POST':
        post = dict(request.POST.items())

        for key in ('daterange', ):
            context[key] = post[key]

        if post['daterange'] and post['daterange'] != '-':
            daterange = list(map(str.strip, post['daterange'].split('-')))
            desde = pytz.UTC.localize(datetime.strptime(daterange[0], '%d/%m/%Y'))
            hasta = pytz.UTC.localize(datetime.strptime(daterange[1], '%d/%m/%Y'))
        else:
            daterange = None
        
        if daterange:
            testeos = []
            for testeo in TesteoCovidPositivo.find_all():
                if daterange and (testeo.fecha_bloqueo < desde or testeo.fecha_bloqueo > hasta):
                    continue
                testeos.append(testeo)
            context['testeos'] = testeos
        else:
            context['msg_error'] = 'Debe ingresar un rango de fechas menor a 15 dias.'
        
        context['busqueda'] = True
    else:
        raise PermissionDenied

    return render(request, 'funcionalidades/admin/historial-testeos.html', context)