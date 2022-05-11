from django.core.exceptions import ValidationError
from django.db.models.fields import EmailField
from django.forms.widgets import Input
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm, EmailInput, TextInput, Select, ChoiceField, DateInput, CharField, ModelChoiceField, \
    IntegerField
from django.forms import forms
from combiapp.models import *
from datetime import datetime

def repetido(form, campos):
    args = {}
    for campo in campos:
        args[campo] = form.cleaned_data[campo]
    return type(form).Meta.model.objects.filter(**args).exists()


#Validaciones de contraseñas
def contraseña_no_tiene_caracter_especial(password):
    caracteres_especiales = ['!','@','#','$','%','^','&','*','(',')','-','_','=','+','[','{',
                             ']','}','\\','|',';',':','\"',',','<','.','>','/','?','`','~']
    for caracter in password:
        if caracter in caracteres_especiales:
            return False
    return True

def contraseña_no_tiene_tamaño_minimo(password):
    return len(password) < 6

def contraseñas_ingresadas_no_son_iguales(password, cofirmation_password):
    if password == cofirmation_password:
        return False
    return True


#Validación de nombre de usuario para los clientes y choferes
def verificar_email(args):
    #if Cliente.objects.filter(**args).exists():
    #    return Cliente
    #if Chofer.objects.filter(**args).exists():
    #    return Chofer
    #return False
    if User.objects.filter(**args).exists():
        return User
    return False


class LoginForm(ModelForm):
    class Meta:
        model = User

        fields = {'email', 'password'}

        widgets = {
            'email' : EmailInput(attrs={'type': 'email', 'class': 'form-control', 'id' : 'inputEmail'
                                        , 'placeholder' : 'Ingresa aquí tu email', 'required': 'True'}),
            'password': TextInput(attrs={'type' : 'password','class': 'form-control', 'id' : 'inputPassword',
                                        'placeholder' : 'Ingresa aquí tu contraseña', 'required': 'True'}),
        }

    def validar_login(self):
        if self.campos_vacios():
            return False

    def campos_vacios(self):
        if not self.data['email'] or not self.data['password']:
            return True
        return False


class LugarForm(ModelForm):
    class Meta:
        PROVINCIAS = [
            ('Buenos Aires', 'Buenos Aires'),
            ('Catamarca', 'Catamarca'),
            ('Chaco', 'Chaco'),
            ('Chubut', 'Chubut'),
            ('Córdoba', 'Córdoba'),
            ('Corrientes', 'Corrientes'),
            ('Entre Ríos', 'Entre Ríos'),
            ('Formosa', 'Formosa'),
            ('Jujuy', 'Jujuy'),
            ('La Pampa', 'La Pampa'),
            ('La Rioja', 'La Rioja'),
            ('Mendoza', 'Mendoza'),
            ('Misiones', 'Misiones'),
            ('Neuquén', 'Neuquén'),
            ('Río Negro', 'Río Negro'),
            ('Salta', 'Salta'),
            ('San Juan', 'San Juan'),
            ('San Luis', 'San Luis'),
            ('Santa Cruz', 'Santa Cruz'),
            ('Santa Fe', 'Santa Fe'),
            ('Santiago del Estero', 'Santiago del Estero'),
            ('Tierra del Fuego', 'Tierra del Fuego'),
            ('Tucumán', 'Tucumán'),
        ]

        model = Lugar

        fields = {'ciudad', 'provincia'}

        widgets = {
            'ciudad': TextInput(attrs={'type': 'text', 'class': 'form-control', 'id' : 'nombreCiudad',
                                        'placeholder' : 'Ingrese el nombre de la ciudad', 'required' : 'True'}),
            'provincia': Select(attrs={'class': 'form-control form-select mb-3', 'placeholder': 'Ingrese el nombre de la provincia', 'required': 'True'}, choices=PROVINCIAS)
        }

    def validar(self):
        if not self.__validar_campos_no_vacios():
            return False, 'Debe completar todos los campos.'
        if not self.__validar_ciudad():
            return False, 'El nombre de la ciudad ingresado es inválido.'
        if not self.__validar_provincia():
            return False, 'La provincia ingresada no existe.'
        if not self.__validar_existe_lugar_similar():
            return False, 'Ya existe un lugar con la misma ciudad y provincia.'
        return True, f'Se ha creado el lugar {self.data["ciudad"]}, {self.data["provincia"]}.'
    
    def __validar_campos_no_vacios(self):
        return self.data['ciudad'] and self.data['provincia']

    def __validar_ciudad(self):
        return all(c.isalnum() or c == ' ' for c in self.data['ciudad'])
    
    def __validar_provincia(self):
        return (self.data['provincia'], self.data['provincia']) in self.Meta.PROVINCIAS

    def __validar_existe_lugar_similar(self):
        args = {'ciudad': self.data['ciudad'], 'provincia': self.data['provincia']}
        # Se verifica si existe un lugar con la misma ciudad y provincia
        if Lugar.objects.filter(**args).exists():
            # Se verifica si el mismo está habilitado, en caso de estarlo no se puede darlo de alta,
            # ya que tiene la misma ciudad y provincia
            similar = Lugar.objects.filter(**args).first()
            if similar.habilitado:
                return False
            # Caso contrario se elimina físicamente el lugar deshabilitado
            similar.delete()
        return True


class RutaForm(ModelForm):

    # Se agregan al Select de origen los lugares habilitados
    origen = ModelChoiceField(widget=Select(attrs={'class': 'form-select form-select mb-3', 'id' : 'origen',
                                        'aria-label' : '.form-select-lg example'}),queryset=Lugar.objects.filter(habilitado=True))

    #Se agregan al Select de destino los lugares habilitados
    destino = ModelChoiceField(widget=Select(attrs={'class': 'form-select form-select mb-3', 'id' : 'destino',
                                        'aria-label' : '.form-select-lg example'}), queryset=Lugar.objects.filter(habilitado=True))


    combi = ModelChoiceField(widget=Select(attrs={'class': 'form-select form-select mb-3', 'id' : 'combi',
                                        'aria-label' : '.form-select-lg example'}), queryset=Combi.objects.filter(habilitado=True))

    hours = IntegerField(widget=TextInput({'type': 'text', 'class': 'form-control', 'id': 'hours',
                                           'placeholder': 'Horas', 'required': 'True'}))
    minutes = IntegerField(widget=TextInput({'type': 'text', 'class': 'form-control', 'id': 'minutes',
                                             'placeholder': 'Minutos', 'required': 'True'}))

    class Meta:
        model = Ruta

        fields = {'origen', 'destino', 'distancia'}

        widgets = {
            'kilometros': TextInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'kilometros',
                                          'placeholder': 'Ingrese la distancia en kilometros', 'required': 'True'})
        }

    def validar_ruta(self):
        if self.campos_vacios():
            return False
        if self.es_origen_invalido():
            return False
        if self.es_destino_invalido():
            return False
        if self.es_combi_invalida():
            return False
        if self.mismo_origen_y_destino():
            return False
        if self.existe_ruta_con_origen_y_destino():
            return False
        if self.es_kilometro_negativo():
            return False
        if self.es_duracion_invalida():
            return False
        self.is_valid()
        return True

    def es_duracion_invalida(self):
        if self.es_hora_invalida() or self.son_minutos_invalidos():
            return True
        return False

    def es_hora_invalida(self):
        hora = self.data['hours']
        if not hora:
            return True
        if int(hora) < 0:
            return True
        return False

    def son_minutos_invalidos(self):
        minutos = self.data['minutes']
        if not minutos:
            return True
        if int(minutos) < 0 or int(minutos) > 59:
            return True
        return False

    def es_kilometro_negativo(self):
        return int(self.data['kilometros']) < 0

    def es_origen_invalido(self):
        return not self.data['origen']

    def es_destino_invalido(self):
        return not self.data['destino']

    def es_combi_invalida(self):
        return not self.data['combi']

    def mismo_origen_y_destino(self):
        origen = self.data['origen']
        destino = self.data['destino']
        return origen == destino

    def existe_ruta_con_origen_y_destino(self):
        origen = self.data['origen']
        destino = self.data['destino']
        combi = self.data['combi']

        args = {'origen': origen, 'destino': destino}

        # Se verifica si existe una ruta con el mismo origen y destino
        if Ruta.objects.filter(**args).exists():
            # Se verifica si la misma está habilitada, en caso de estarlo no se puede darla de alta,
            # ya que tiene el mismo origen y destino
            if Ruta.objects.filter(**args).first().habilitado:
                return True
            # Caso contrario se elimina físicamente la ruta deshabilitada
            Ruta.objects.filter(**args).delete()
        return False

    def campos_vacios(self):
        if not self.data['origen'] or not self.data['destino'] or not self.data['kilometros'] or not self.data['hours'] \
                or not self.data['minutes'] or not self.data['combi']:
            return True
        return False


class ViajeForm(ModelForm):
    ruta = ModelChoiceField(widget=Select(attrs={'class': 'form-select form-select mb-3', 'id': 'origen',
                                                   'aria-label': '.form-select-lg example'}),
                              queryset=Ruta.objects.filter(habilitado=True))

    class Meta:
        model = Viaje

        fields = {'ruta', 'fecha_de_salida', 'hora_de_salida', 'precio'}

        widgets = {
            'ruta' : Select(attrs={'class': 'form-select form-select mb-3', 'id' : 'ruta',
                                        'aria-label' : '.form-select-lg example'}),

            'fechaDeSalida' : TextInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'fechaDeSalida'}),

            'precio' : TextInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'precio',
                                          'placeholder': 'Ingrese aquí el precio', 'required': 'True'})
        }

    def validar_viaje(self):
        if self.campos_vacios():
            return False
        if self.es_precio_negativo():
            return False
        if self.es_fecha_invalida():
            return False
        if self.combi_no_disponible():
            return False
        self.is_valid()
        return True

    def es_precio_negativo(self):
        precio = self.data['precio']
        return float(precio) < 0

    def es_fecha_invalida(self):
        fecha = self.data['fechaDeSalida']

        if not fecha:
            return True

        year = fecha.split("-")[0]
        month = fecha.split("-")[1]
        day = fecha.split("-")[2]
        fechaFormateada = (month + "/" + day + "/" + year + " 00:00:00.000000")
        fecha = datetime.strptime(fechaFormateada, '%m/%d/%Y %H:%M:%S.%f')

        return fecha <= datetime.today()

    def combi_no_disponible(self):
        combi = Ruta.objects.filter(pk=self.data['ruta']).first().combi

        fecha = self.data['fechaDeSalida']
        year = fecha.split("-")[0]
        month = fecha.split("-")[1]
        day = fecha.split("-")[2]
        fechaFormateada = (month + "/" + day + "/" + year + " 00:00:00.000000")
        fecha = datetime.strptime(fechaFormateada, '%m/%d/%Y %H:%M:%S.%f')

        viajes = Viaje.objects.filter(fechaDeSalida=fecha)
        for viaje in viajes:
            if viaje.ruta.combi == combi:
                if viaje.habilitado:
                    return True
                else:
                    Viaje.objects.filter(pk=viaje.pk).delete()
                    return False
        return False

    def campos_vacios(self):
        if not self.data['ruta'] or not self.data['fechaDeSalida'] or not self.data['precio']:
            return True
        return False


class ClienteForm(ModelForm):
    confirmationPassword = CharField(
        widget=TextInput(attrs={'type': 'password', 'class': 'form-control validate', 'id': 'password2',
                                'placeholder': 'Ingrese la contraseña', 'required': 'True',
                                'pattern': '(?=.*\d[@\[\]^_`{|}~!#$%&()*+,-./]).{6,}'}))

    class Meta:
        model = Cliente

        fields = {'first_name', 'last_name', 'email', 'dni', 'password', 'fecha_nacimiento'}

        widgets = {
            'first_name': TextInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'firstName',
                                           'placeholder': 'Ingrese el nombre', 'required': 'True',
                                           'pattern': '(?=.*[áéíóúÁÉÍÓÚ])(?=.*[ ])(?=.*[a-z])(?=.*[A-Z]),{,}'}),

            'last_name': TextInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'lastName',
                                          'placeholder': 'Ingrese el apellido', 'required': 'True'}),

            'email': EmailInput(attrs={'class': 'form-control', 'id': 'email',
                                       'placeholder': 'Ingrese el email', 'placeholder': 'email@example.com',
                                       'aria-label': '.form-select-lg example', 'required': 'True'}),

            'dni': TextInput(attrs={'type': 'number', 'class': 'form-control', 'id': 'dni',
                                         'placeholder': 'Ingrese el dni', 'required': 'True'}),

            'password': TextInput(attrs={'type': 'password', 'class': 'form-control validate', 'id': 'password',
                                         'placeholder': 'Ingrese la contraseña', 'required': 'True',
                                         'pattern': '(?=.*\d[@\[\]^_`{|}~!#$%&()*+,-./]).{6,}'}),
            'fecha_nacimiento' : DateInput(attrs={'type' : 'date', 'class' : 'form-control', 'id' : 'fechaNacimiento', 'required' : 'True'})
        }

    def validar_cliente(self, user_email=None):
        password = self.data['password']
        confirmation_password = self.data['confirmationPassword']
        if self.validar_campos_no_vacios():
            return False
        if self.es_menor_de_edad():
            return False
        if self.validacion_de_contraseña_es_invalida(password, confirmation_password):
            return False
        if self.existe_cliente_con_mismo_nombre(user_email):
            return False
        self.is_valid()
        return True

    def validacion_de_contraseña_es_invalida(self, password, confirmation_password):
        if contraseña_no_tiene_caracter_especial(password):
            return True
        if contraseña_no_tiene_tamaño_minimo(password):
            return True
        if contraseñas_ingresadas_no_son_iguales(password, confirmation_password):
            return True
        return False

    def existe_cliente_con_mismo_nombre(self, user_email):
        email = self.data['email']
        args = {'email': email}

        #Si son iguales es porque se está modificando al usuario
        if user_email == self.data['email']:
            return False

        resultado = verificar_email(args)

        if resultado == False:
            return False
        else:
            if User.objects.filter(**args).first().habilitado:
                return True
            User.objects.filter(email=email).delete()
        return False

    def es_menor_de_edad(self):
        fecha_de_nacimiento = self.data['fecha_nacimiento']
        año = fecha_de_nacimiento.split("-")[0]
        edad = datetime.today().year - int(año)

        if edad < 18:
            return True
        return False

    def validar_campos_no_vacios(self):
        if not self.data['first_name'] or not self.data['last_name'] or not self.data['dni'] or not self.data['fecha_nacimiento']:
            return True
        return False

class TarjetaForm(ModelForm):
    codigo = CharField(
        widget=TextInput(attrs={'type': 'password', 'class': 'form-control validate', 'id': 'codigo', 'required': 'True'}))


    class Meta:
        model = Tarjeta

        fields = {'numero', 'titular', 'fecha_vencimiento'}

        widgets = {
            'titular': TextInput(attrs={'type':'text', 'class' : 'form-control', 'id' : 'cc-name',
                                        'pattern' : '(?=.*[áéíóúÁÉÍÓÚ.])(?=.*[ ])(?=.*[a-z])(?=.*[A-Z]),{,}',
                                        'placeholder' : 'Ingrese aquí el titular de la tarjeta', 'required': 'True'}),

            'numero': TextInput(attrs={'type':'text', 'class':'form-control', 'id':'cc-number ',
                                        'placeholder':'Ingrese aquí el número de la tarjeta', 'required':'True'}),

            'fecha_vencimiento': DateInput(attrs={'class':'form-control', 'type':'month', 'value':'2022-01',
                                                    'id':'expiration-card'}),
        }

    def validar_tarjeta(self):
        if self.campos_vacios():
            return False
        if self.verificar_existencia():
            return False
        if self.es_fecha_invalida():
            return False
        self.is_valid()
        return True

    def verificar_existencia(self):
        return Tarjeta.objects.filter(numero=self.data['numero']).exists()

    def es_fecha_invalida(self):
        fecha = self.data['fecha_vencimiento']

        if not fecha:
            return True

        year = fecha.split("-")[0]
        month = fecha.split("-")[1]
        fechaFormateada = (month + "/" + "01" + "/" + year + " 00:00:00.000000")
        fecha = datetime.strptime(fechaFormateada, '%m/%d/%Y %H:%M:%S.%f')

        return fecha <= datetime.today()

    def campos_vacios(self):
        if not self.data['titular'] or not self.data['numero'] or not self.data['fecha_vencimiento']:
            return True
        return False


class AltaExpresForm(ClienteForm):

        class Meta:
            model = Cliente

            fields = {'first_name', 'last_name', 'email', 'dni', 'password', 'fecha_nacimiento'}

            widgets = {

                'email': EmailInput(attrs={'class': 'form-control', 'id': 'email',
                                           'placeholder': 'Ingrese el email', 'placeholder': 'email@example.com',
                                           'aria-label': '.form-select-lg example', 'required': 'True'}),

                'dni': TextInput(attrs={'type': 'number', 'class': 'form-control', 'id': 'dni',
                                        'placeholder': 'Ingrese el dni', 'required': 'True'}),

                'fecha_nacimiento': DateInput(
                    attrs={'type': 'date', 'class': 'form-control', 'id': 'fechaNacimiento', 'required': 'True'})
            }

        def validar_cliente(self, user_email=None):
            if self.validar_campos_no_vacios():
                return False
            if super(AltaExpresForm, self).es_menor_de_edad():
                return False
            if super(AltaExpresForm, self).existe_cliente_con_mismo_nombre(user_email):
                return False
            self.is_valid()
            return True

        def validar_campos_no_vacios(self):
            if not self.data['email'] or not self.data['dni'] or not self.data['fecha_nacimiento']:
                return True
            return False


class ChoferForm(ModelForm):
    password2 = CharField(widget=TextInput(attrs={'type': 'password', 'class': 'form-control validate', 'id': 'password',
                                          'placeholder': 'Ingrese la contraseña', 'required': 'True',
                                           'pattern' : '(?=.*\d[@\[\]^_`{|}~!#$%&()*+,-./]).{6,}'}))

    class Meta:
        model = Chofer

        fields = {'first_name', 'last_name', 'email', 'password', 'telefono'}

        widgets = {
            'first_name': TextInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'firstName',
                                          'placeholder': 'Ingrese el nombre', 'required': 'True',
                                        'pattern' : '(?=.*[áéíóúÁÉÍÓÚ])(?=.*[ ])(?=.*[a-z])(?=.*[A-Z]),{,}'}),

            'last_name': TextInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'lastName',
                                          'placeholder': 'Ingrese el apellido', 'required': 'True'}),

            'email': EmailInput(attrs={'class': 'form-control', 'id' : 'email',
                                        'placeholder': 'Ingrese el email', 'placeholder' :'email@example.com',
                                       'aria-label' : '.form-select-lg example', 'required': 'True'}),

            'password': TextInput(attrs={'type': 'password', 'class': 'form-control validate', 'id': 'password',
                                          'placeholder': 'Ingrese la contraseña', 'required': 'True',
                                           'pattern' : '(?=.*\d[@\[\]^_`{|}~!#$%&()*+,-./]).{6,}'}),

            'telefono': TextInput(attrs={'type': 'number', 'class': 'form-control', 'id': 'telefono',
                                          'placeholder': 'Ingrese el telefono', 'required': 'True'})
        }
    
    def crear(self):
        f = self.data
        Chofer.objects.create_chofer(f['email'], f['first_name'], f['last_name'], f['telefono'], f['password'])
    
    def guardar(self):
        pass
    
    def validar_alta(self):
        if not self.__validar_campos_no_vacios():
            return False, 'Debe completar todos los campos.'
        if not self.__validar_contraseña(self.data['password'], self.data['password2']):
            return False, 'La contraseña ingresada es inválida.'
        if not self.__validar_chofer_unico():
            return False, 'El nombre de usuario ingresado se encuentra en uso.'
        return True, f'Se ha creado el usuario chofer {self.data["email"]}.'
    
    def validar_editar(self):
        pass
    
    def __validar_campos_no_vacios(self):
        return self.data['first_name'] and self.data['last_name'] and self.data['telefono']

    def __validar_contraseña(self, password, confirmation_password):
        if contraseña_no_tiene_caracter_especial(password):
            return False
        if contraseña_no_tiene_tamaño_minimo(password):
            return False
        if contraseñas_ingresadas_no_son_iguales(password, confirmation_password):
            return False
        return True

    def __validar_chofer_unico(self):
        email = self.data['email']
        args = {'email': email}

        resultado = verificar_email(args)

        if resultado == False:
            return True
        else:
            if User.objects.filter(email=email).first().habilitado:
                return False
            User.objects.filter(email=email).delete()
        return True


class CombiForm(ModelForm):


    chofer = ModelChoiceField(widget=Select(attrs={'class': 'form-select form-select mb-3', 'id': 'chofer',
                                              'aria-label': '.form-select-lg example'}), queryset=Chofer.objects.filter(habilitado=True))
    class Meta:
        model = Combi

        fields = {'modelo', 'patente', 'asientos', 'chofer', 'tipo'}

        TIPOS_DE_COMBIS = (
            ('Cómoda', 'Cómoda'),
            ('Súper cómoda', 'Súper cómoda'),
        )

        widgets = {
            'modelo' : TextInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'modelo',
                                          'placeholder': 'Ingrese el modelo', 'required': 'True',
                                        'pattern' : '(?=.*[áéíóúÁÉÍÓÚ])(?=.*[ ])(?=.*[a-z])(?=.*[A-Z]),{,}'}),

            'patente': TextInput(attrs={'type': 'text', 'class': 'form-control', 'id': 'patente',
                                          'placeholder': 'Ingrese la patente', 'required': 'True'}),

            'chofer' : Select(attrs={'class': 'form-select form-select mb-3', 'id' : 'chofer',
                                        'aria-label' : '.form-select-lg example'}),

            'tipo' : Select(attrs={'class': 'form-select form-select mb-3', 'id' : 'tipo',
                                       'aria-label' : '.form-select-lg example'}, choices=TIPOS_DE_COMBIS),

            'asiento': TextInput(attrs={'type': 'number', 'class': 'form-control', 'id': 'asientos',
                                          'placeholder': 'Ingrese la cantidad de asientos', 'required': 'True'})
        }

    def validar_combi(self):

        if self.campos_vacios():
            return False
        if self.es_asiento_invalido():
            return False
        if self.es_chofer_invalido():
            return False
        if self.existe_combi_con_misma_patente():
            return False
        if self.existe_combi_con_mismo_chofer():
            return False
        self.is_valid()
        return True

    def campos_vacios(self):
        if not self.data['patente'] or not self.data['modelo'] or not self.data['asiento']:
            return True
        return False


    def es_asiento_invalido(self):
        return int(self.data['asiento']) < 0

    def es_chofer_invalido(self):
        return not self.data['chofer']



    def existe_combi_con_mismo_chofer(self):
        chofer = self.data['chofer']
        args = {'chofer': chofer}

        if Combi.objects.filter(**args).exists():
            if Combi.objects.filter(**args).first().habilitado:
                return True
            Combi.objects.filter(**args).delete()
        return False

    def existe_combi_con_misma_patente(self):
        patente = self.data['patente']
        args = {'patente': patente}

        if Combi.objects.filter(**args).exists():
            if Combi.objects.filter(**args).first().habilitado:
                return True
            Combi.objects.filter(**args).delete()
        return False
    


class InsumoComestibleForm(ModelForm):
    class Meta:
        TIPOS_DE_INSUMO_COMESTIBLE = [
            ('Salado', 'Salado'),
            ('Dulce', 'Dulce')
        ]

        model = InsumoComestible
        fields = {'nombre', 'tipo', 'precio'}
        widgets = {
            'tipo': Select(attrs={'class': 'form-select mb-3', 'aria-label': '.form-select-lg example'}, choices=TIPOS_DE_INSUMO_COMESTIBLE),
            'nombre': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre', 'required': 'True'}),
            'precio': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el precio', 'required': 'True'})
        }

    def validar(self, obj):
        if not self.__validar_campos_no_vacios():
            return False, 'TODO'
        if not self.__validar_precio_positivo():
            return False, 'TODO'
        if not self.__validar_nombre_disponible(obj):
            return False, 'TODO'
        return True, 'TODO'
    
    def guardar(self, obj):
        if not obj:
            obj = InsumoComestible()
        print(self.data)
        for name in ('nombre', 'tipo', 'precio'):
            setattr(obj, name, self.data[name])
        obj.save()

    def __validar_campos_no_vacios(self):
        return self.data['tipo'] and self.data['nombre'] and self.data['precio']

    def __validar_precio_positivo(self):
        return int(self.data['precio']) >= 0

    def __validar_nombre_disponible(self, obj):
        nombre = self.data['nombre']
        args = {'nombre' : nombre }

        # Se verifica si existe un insumo comestible con el mismo nombre
        queryset = InsumoComestible.objects.filter(**args)
        if queryset.exists():
            similar = queryset.first()
            if similar != obj:
                # Se verifica si el mismo está habilitado, en caso de estarlo no se puede darlo de alta, ya que tiene el mismo nombre
                if similar.habilitado:
                    return False
                else:
                    # Caso contrario se elimina físicamente el insumo deshabilitado
                    InsumoComestible.objects.filter(nombre=nombre).delete()
        return True


class BuscarEmailForm(forms.Form):
    email = CharField(widget=TextInput(attrs={'type': 'email', 'class': 'form-control validate', 'id': 'email', 
    'placeholder': 'ejemplo@gmail.com', 'required': 'True'}))