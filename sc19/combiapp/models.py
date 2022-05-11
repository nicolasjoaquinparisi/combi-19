from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
import datetime
import re
import pytz


class ValidationError(Exception):
    pass


# Clase encargada de crear los distintos tipos de usuarios del sistema
class AccountManager(BaseUserManager):
    def create_superuser(self, email, first_name, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, first_name, password, **other_fields)

    def create_user(self, email, first_name, password, **other_fields):
        user = self.model(email=email, first_name=first_name, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_cliente(self, email, first_name, last_name, dni, fecha_nacimiento, tarjeta, password):
        if not email:
            raise ValueError(_('You must provide an email address'))

        cliente = self.model(email=email, first_name=first_name,
                             last_name=last_name, dni=dni, fecha_nacimiento=fecha_nacimiento, tarjeta=tarjeta)
        cliente.set_password(password)
        cliente.save()
        return cliente

    def create_chofer(self, email, first_name, last_name, telefono, password):
        chofer = self.model(email=email, first_name=first_name,
                            last_name=last_name, telefono=telefono)
        chofer.set_password(password)
        chofer.save()
        return chofer


class BaseModel(models.Model):
    class Meta:
        abstract = True
    
    habilitado = models.BooleanField(default=True)
    
    def get_context(self):
        return {}

    def fill_and_save(self, post):
        if self.pk is not None and not self._check_can_modify():
            return False, self._get_cant_modify_message()

        # El método abstracto '_get_field_cleaners' devuelve una lista de
        # tuplas con el nombre de un campo y una función que valida el campo
        # del POST y lo convierte al tipo de dato a guardar.
        cleaners = self._get_field_cleaners()
        
        # Valido todos los campos y los guardo en el diccionario 'fields'.
        # Esto se hace para evitar modificar los campos del objeto sin antes
        # haber verificado que todos los datos ingresados sean correctos.
        # También se genera el diccionario 'queryset_args' que se utiliza mas
        # adelante para verificar que el objeto sea único.
        fields = {}
        for name, display_name, clean in cleaners:
            try:
                value = clean(post)
            except ValidationError as e:
                return False, f'Error en {display_name}: {str(e)}.'
            fields[name] = value

        # Una vez que se verificaron todos los campos, los asigno uno por uno
        # al objeto.
        for name, value in fields.items():
            if isinstance(self, User) and name == 'password':
                self.set_password(value)
            else:
                setattr(self, name, value)
        
        # Compruebo que el objeto sea único.
        qobject = self._get_unique_check(fields)
        if qobject:
            other = self.find_first(qobject)
            if other and self != other:
                return False, self._get_not_unique_message(other)
        
        try:
            self._do_extra_validations()
        except ValidationError as e:
            return False, str(e)
        
        # Si el objeto tiene una primary key significa que ya existe en la base
        # de datos. Utilizo esto para determinar el tipo de mensaje de exito a
        # imprimir.
        if self.pk is None:
            message = self._get_creation_message()
        else:
            message = self._get_modification_message()

        self.save()
        
        return True, message
    
    def delete(self):
        if self.habilitado:
            self.habilitado = False
            self.save()
    
    @classmethod
    def find_all(cls, qobject=None):
        if qobject:
            qobject &= models.Q(habilitado=True)
        else:
            qobject = models.Q(habilitado=True)

        return cls.objects.filter(qobject)

    @classmethod
    def find_first(cls, qobject=None):
        query = cls.find_all(qobject)
        if query.exists():
            instance = query.first()
        else:
            instance = None
        
        return instance
    
    @classmethod
    def find_pk(cls, pk):
        return cls.find_first(models.Q(pk=pk))
    
    def _get_cant_modify_message(self):
        raise NotImplementedError
    
    def _get_not_unique_message(self, other):
        raise NotImplementedError
    
    def _get_creation_message(self):
        raise NotImplementedError
    
    def _get_modification_message(self):
        raise NotImplementedError
    
    def _check_can_modify(self):
        return True

    def _do_extra_validations(self):
        pass

    @classmethod
    def _get_field_cleaners(cls):
        raise NotImplementedError
    
    @classmethod
    def _get_unique_check(cls, fields):
        raise NotImplementedError

    # Validaciones comúnes para ser reutilizadas
    @classmethod
    def _clean_name(cls, value, is_valid_char):
        if not value:
            raise ValidationError('el campo está vacío')

        if not all(c == ' ' or is_valid_char(c) for c in value):
            raise ValidationError('contiene caracteres no permitidos')

        return ' '.join(value.split())
    
    @classmethod
    def _clean_name_alpha(cls, value):
        return cls._clean_name(value, str.isalpha)
    
    @classmethod
    def _clean_name_alnum(cls, value):
        return cls._clean_name(value, str.isalnum)
    
    @classmethod
    def _clean_integer(cls, value):
        if not value:
            raise ValidationError('el campo está vacío')

        try:
            value = int(value)
        except ValueError:
            raise ValidationError('no es un número válido')
        
        return value
    
    @classmethod
    def _clean_integer_positive(cls, value):
        value = cls._clean_integer(value)
        if value < 0:
            raise ValidationError('el número es negativo')
        
        return value

    @classmethod
    def _clean_integer_negative(cls, value):
        value = cls._clean_integer(value)
        if value >= 0:
            raise ValidationError('el número es positivo')
        
        return value
    
    @classmethod
    def _clean_float(cls, value):
        if not value:
            raise ValidationError('el campo está vacío')

        try:
            value = float(value)
        except ValueError:
            raise ValidationError('no es un número válido')
        
        return value
    
    @classmethod
    def _clean_float_positive(cls, value):
        value = cls._clean_float(value)
        if value < 0:
            raise ValidationError('el número es negativo')
        
        return value
    
    @classmethod
    def _clean_float_negative(cls, value):
        value = cls._clean_float(value)
        if value >= 0:
            raise ValidationError('el número es positivo')
        
        return value
    
    @classmethod
    def _clean_email(cls, value):
        if not value:
            raise ValidationError('el campo está vacío')

        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        m = re.search(regex, value)
        if not m:
            raise ValidationError('no es un email válido')
        
        return value
    
    @classmethod
    def _clean_phone_number(cls, value):
        if not value:
            raise ValidationError('el campo está vacío')

        value = value.replace(' ', '')
        if value.startswith('+'):
            value = value[1:]
        
        if not all(c.isdigit() for c in value):
            raise ValidationError('no es un número teléfono válido')
        
        return value
    
    @classmethod
    def _clean_password(cls, password, password_confirm):
        especiales = '!@#$%^&*()-_=+[{]}\|;:",<.>/?`~'

        if not password:
            raise ValidationError('el campo está vacío')

        if len(password) < 6:
            raise ValidationError('debe contener por lo menos 6 caracteres')

        if not all(c.isalnum() or c in especiales for c in password):
            raise ValidationError('contiene caracteres no permitidos')

        if not any(c in especiales for c in password):
            raise ValidationError('debe contener por lo menos un caracter especial')
        
        if password != password_confirm:
            raise ValidationError('no coincide con la confirmación')

        return password

    @classmethod
    def _clean_select(cls, value, options):
        if not value:
            raise ValidationError('el campo está vacío')

        if value not in options:
            raise ValidationError('el item no existe')
        
        return value
    
    @classmethod
    def _clean_patente_argentina(cls, value):
        if not value:
            raise ValidationError('el campo está vacío')

        value = value.replace(' ', '').upper()
        if len(value) == 6:
            if all(c.isalpha() for c in value[0:3]) and all(c.isdigit() for c in value[3:6]):
                value = f'{value[0:3]} {value[3:6]}'
            else:
                value = None
        elif len(value) == 7:
            if all(c.isalpha() for c in value[0:2]) and all(c.isdigit() for c in value[2:5]) and all(c.isalpha() for c in value[5:7]):
                value = f'{value[0:2]} {value[2:5]} {value[5:7]}'
            else:
                value = None
        else:
            value = None
        
        if not value:
            raise ValidationError('no es una patente válida')
        
        return value
    
    @classmethod
    def _clean_object_ref(cls, value, object_type):
        if not value:
            raise ValidationError('el campo está vacío')

        value = object_type.find_first(models.Q(pk=value))
        if not value:
            raise ValidationError('el objeto no existe')
        
        return value
    
    @classmethod
    def _clean_date(cls, value):
        try:
            year, month, day = value.split('-')
            value = datetime.date(int(year), int(month), int(day))
        except:
            raise ValidationError('no es una fecha válida')
        
        return value
    
    @classmethod
    def _clean_date_in_future(cls, value):
        value = cls._clean_date(value)
        if value < datetime.date.today():
            raise ValidationError('la fecha debe ser futura')

        return value

    @classmethod
    def _clean_hour(cls, time):
        try:
            hour, minutes = time.split(':')
            time = datetime.time(int(hour), int(minutes), 0)
        except:
            raise ValidationError('no es una hora válida')

        return time


class Tarjeta(BaseModel):
    numero = models.IntegerField()
    titular = models.CharField(max_length=100)
    fecha_vencimiento = models.DateTimeField()

    @classmethod
    # Se formatea la fecha para que se pueda guardar, tomando el mes y el año seleccionado
    def get_formated_fecha(cls, fecha):
        return str(str(fecha[0] + fecha[1] +
                        fecha[2] + fecha[3]) + '-' +
                    str(fecha[5] + fecha[6]) + "-01 10:14:30.287447-03")

    def create_tarjeta(self, numero, titular, fecha_vencimiento):
        tarjeta         = Tarjeta()
        tarjeta.numero  = numero
        tarjeta.titular = titular
        tarjeta.fecha_vencimiento = Tarjeta.get_formated_fecha(fecha_vencimiento)
        tarjeta.save()
        return tarjeta

    def __str__(self):
        return f'**** **** **** {self.numero % 4:04d}, {self.titular}'

    @classmethod
    def get_instance(cls, numero):
        return Tarjeta.objects.filter(numero=numero).first()

    @property
    def get_fecha_vencimiento(self):
        #Se formatea la fecha de vencimiento de la tarjeta para poder visualizarla correctamente
        if self.fecha_vencimiento.month < 10:
            return str(self.fecha_vencimiento.year) + "-" + "0" + str(self.fecha_vencimiento.month)
        else:
            return str(self.fecha_vencimiento.year) + "-" + str(self.fecha_vencimiento.month)

    @property
    def get_formated_fecha_vencimiento(self):
        #Se formatea la fecha de vencimiento para mostrarla en el perfil del usuario gold
        if self.fecha_vencimiento.month < 10:
            return  "0" + str(self.fecha_vencimiento.month) + "/" + str(self.fecha_vencimiento.year)
        else:
            return str(self.fecha_vencimiento.month)  + "-" + str(self.fecha_vencimiento.year)

    def modificar(self, data):
        self.numero = data['numero']
        self.titular = data['titular']
        self.fecha_vencimiento = Tarjeta.get_formated_fecha(data['fecha_vencimiento'])
        self.save()

# Entidad base que guarda los datos que tienen en común los clientes y los choferes
class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    email = models.EmailField(_('Email Address'), unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name  = models.CharField(max_length=150, blank=True)
    is_staff   = models.BooleanField(default=False)
    is_active  = models.BooleanField(default=True)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email
    
    def _get_not_unique_message(self, other):
        return f'Ya existe un usuario con email \'{self.email}\'.'
    
    @classmethod
    def _get_unique_check(cls, fields):
        return models.Q(email=fields['email'])


class Cliente(User):
    """ Creación de un modelo Usuario tipo Cliente """

    dni = models.IntegerField()
    fecha_nacimiento = models.DateTimeField()
    tarjeta = models.ForeignKey(Tarjeta, on_delete=models.SET_NULL, null=True)
    fecha_bloqueo = models.DateTimeField(default=None, null=True)

    class Meta:
        permissions = [
            ("can_view_perfilUsuario", "Puede ver su perfil"),
            ("can_chages_user", "Puede modificar usuario"),
            ("can_delete_user", "Puede eliminar usuario"),
        ]

    def delete_cliente(self):
        self.habilitado = False
        self.save()

    def modificar(self, data):
        self.first_name       = data['first_name']
        self.last_name        = data['last_name']
        self.dni              = data['dni']
        self.fecha_nacimiento = data['fecha_nacimiento']
        self.email            = data['email']
        self.set_password(data['password'])
        self.save()

    @classmethod
    def get_instance(cls, email):
        return Cliente.objects.filter(email=email).first()

    @property
    def get_nombre_completo(self):
        return self.last_name + ", " + self.first_name
    
    @property
    def pasajes(self):
        return Pasaje.find_all(models.Q(cliente=self))
    
    @property
    def comentarios(self):
        return Comentario.find_all(models.Q(cliente=self))

    @property
    def get_pasaje_finalizado(self):
        for pasaje in self.pasajes:
            if pasaje.get_estado == 'Finalizado':
                return True
        return False

    def bloquear_cuenta(self):
        self.fecha_bloqueo = datetime.datetime.today()
        self.save()

    @property
    def cantidad_dias_bloqueo(self):
        """
        "Determinar la cantidad de días de bloqueo"
        if self.fecha_bloqueo == None:
            return 0

        "Se resta a la fecha actual la fecha de bloqueo, si es cero, entonces se pone en None self.fecha_bloqueo y retorna 0"
        "Caso contrario retorna la cantidad de dias"
        """
        if self.fecha_bloqueo is not None:
            fecha_bloqueo = self.fecha_bloqueo.replace(tzinfo=None)
            today = datetime.datetime.today().replace(tzinfo=None)

            fecha_fin_bloqueo =  fecha_bloqueo + datetime.timedelta(days=15)

            dias_restantes = fecha_fin_bloqueo - today

            return dias_restantes.days
        else:
            return 0

    @property
    def esta_bloqueado(self):
        if self.cantidad_dias_bloqueo > 0:
            return True
        return False

class Chofer(User):
    class Meta:
        permissions = [
            ("can_view_perfilChofer", "Puede ver su perfil"),
        ]
    
    telefono = models.CharField(max_length=16)

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'

    def _get_creation_message(self):
        return f'Se creó el chofer \'{self}\' con éxito.'
    
    def _get_modification_message(self):
        return f'Se modificó el chofer con éxito.'

    @classmethod
    def _get_field_cleaners(cls):
        return (
            ('first_name', 'el nombre ingresado', cls.__clean_first_name),
            ('last_name', 'el apellido ingresado', cls.__clean_last_name),
            ('email', 'el email ingresado', cls.__clean_email),
            ('telefono', 'el teléfono ingresado', cls.__clean_phone_number),
            ('password', 'la contraseña ingresada', cls.__clean_password)
        )

    @classmethod
    def __clean_first_name(cls, post):
        return cls._clean_name_alpha(post['first_name'])
    
    @classmethod
    def __clean_last_name(cls, post):
        return cls._clean_name_alpha(post['last_name'])
    
    @classmethod
    def __clean_email(cls, post):
        print(post)
        return cls._clean_email(post['email'])
    
    @classmethod
    def __clean_phone_number(cls, post):
        return cls._clean_phone_number(post['phone_number'])
    
    @classmethod
    def __clean_password(cls, post):
        return cls._clean_password(post['password'], post['password_confirm'])

    "Función que retorna los viajes de forma ordenada por fecha y hora"
    def sort_proximos_viajes(self, proximos_viajes):
        proximos_viajes_sorted = []

        cantidad_viajes = len(proximos_viajes)
        while cantidad_viajes > 0:

            "Fecha mínima se utiliza para comparar y determinar cuál es el viaje con fecha y hora de salida menor"
            fecha_minima = datetime.datetime(5000, 12, 30, 23, 59, 59)
            "viaje_con_fecha_minima se utiliza para guardar el viaje con fecha minima actual"
            viaje_con_fecha_minima = None

            "Por cada viaje se determina cuál es el menor y se determina que el mismo no esté en el array"
            for viaje in proximos_viajes:
                "Se genera un datetime con la fecha y hora de salida del viaje actual para poder compararlo con el minimo"
                fecha_actual = datetime.datetime(viaje.fecha_de_salida.year, viaje.fecha_de_salida.month,
                                                 viaje.fecha_de_salida.day, viaje.hora_de_salida.hour, viaje.hora_de_salida.minute)

                if fecha_actual < fecha_minima and viaje not in proximos_viajes_sorted:
                    fecha_minima = fecha_actual
                    viaje_con_fecha_minima = viaje

            if viaje_con_fecha_minima is not None:
                proximos_viajes_sorted.append(viaje_con_fecha_minima)

            cantidad_viajes -= 1

        return proximos_viajes_sorted

    @property
    def tiene_viaje_iniciado(self):

        for viaje in Viaje.find_all():
            if (viaje.ruta.combi.chofer == self) and (viaje.estado == "Iniciado"):
                return True
        return False



    @property
    def get_proximos_viajes(self):
        proximos_viajes = []

        viajes = Viaje.find_all()
        for viaje in viajes:
            if (viaje.ruta.combi.chofer == self) and ((viaje.estado == "Pendiente") or (viaje.estado == "Iniciado")):
                proximos_viajes.append(viaje)

        return self.sort_proximos_viajes(proximos_viajes)

    @property
    def get_viajes_realizados(self):
        viajes_realizados = []

        viajes = Viaje.find_all()
        for viaje in viajes:
            if (viaje.ruta.combi.chofer == self) and (viaje.estado == "Finalizado"):
                viajes_realizados.append(viaje)

        return self.sort_proximos_viajes(viajes_realizados)

class Combi(BaseModel):
    TIPOS = (
        'Cómoda',
        'Súper cómoda'
    )

    identificacion = models.CharField(max_length=5)
    asientos = models.IntegerField(default=0)
    patente = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)
    chofer = models.ForeignKey(Chofer, on_delete=models.SET_NULL, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.pk:
            ident = type(self).objects.count() + 1
            self.identificacion = f'C{ident:04d}'

    def __str__(self):
        return f'{self.identificacion}, {self.patente}'
    
    def get_context(self):
        return {'tipos': self.TIPOS, 'choferes': Chofer.find_all()}

    def _get_cant_modify_message(self):
        if self.esta_asociada_a_viaje_con_pasajes_vendidos:
            return f'No se puede modificar la combi \'{self}\' ya que está asociada a un viaje el cual tiene pasajes vendidos'
        return f'No se puede modificar la combi \'{self}\' ya que existe al menos una ruta que la usa.'

    def _get_not_unique_message(self, other):
        if self.patente == other.patente:
            return f'Ya existe una combi con patente \'{self.patente}\'.'
        elif self.chofer == other.chofer:
            return f'Ya existe una combi con el chofer \'{self.chofer}\'.'

    def _get_creation_message(self):
        return f'Se creó la combi \'{self}\' con éxito.'
    
    def _get_modification_message(self):
        return f'Se modificó la combi con éxito.'
    
    def _check_can_modify(self):
        return Ruta.find_first(models.Q(combi=self)) is None and self.esta_asociada_a_viaje_con_pasajes_vendidos

    @property
    def esta_asociada_a_viaje_con_pasajes_vendidos(self):
        viajes = Viaje.find_all()
        for viaje in viajes:
            if viaje.ruta.combi == self and viaje.pasajes_vendidos > 0:
                return True
        return False
    
    @classmethod
    def _get_field_cleaners(cls):
        return (
            ('modelo', 'el modelo ingresado', cls.__clean_modelo),
            ('patente', 'la patente ingresada', cls.__clean_patente),
            ('asientos', 'la cantidad de asientos ingresada', cls.__clean_asientos),
            ('chofer', 'el chofer', cls.__clean_chofer),
            ('tipo', 'el tipo', cls.__clean_tipo)
        )
    
    @classmethod
    def _get_unique_check(cls, fields):
        return models.Q(patente=fields['patente']) | models.Q(chofer=fields['chofer'])

    @classmethod
    def __clean_modelo(cls, post):
        return cls._clean_name_alnum(post['modelo'])
    
    @classmethod
    def __clean_patente(cls, post):
        return cls._clean_patente_argentina(post['patente'])
    
    @classmethod
    def __clean_asientos(cls, post):
        return cls._clean_integer_positive(post['asientos'])
    
    @classmethod
    def __clean_chofer(cls, post):
        return cls._clean_object_ref(post['chofer'], Chofer)
    
    @classmethod
    def __clean_tipo(cls, post):
        return cls._clean_select(post['tipo'], cls.TIPOS)


class InsumoComestible(BaseModel):
    TIPOS = ('Dulce', 'Salado')

    tipo = models.CharField(max_length=max(len(t) for t in TIPOS))
    nombre = models.CharField(max_length=100)
    precio = models.FloatField(default=0)

    def __str__(self):
        return self.nombre
    
    def get_context(self):
        return {'tipos': self.TIPOS}
    
    def _get_not_unique_message(self, other):
        return f'Ya existe un insumo comestible con el nombre \'{self}\'.'

    def _get_creation_message(self):
        return f'Se creó el insumo comestible \'{self}\' con éxito.'
    
    def _get_modification_message(self):
        return f'Se modificó el insumo comestible con éxito.'
    
    @classmethod
    def _get_field_cleaners(cls):
        return [
            ('tipo', 'el tipo ingresado', cls.__clean_tipo),
            ('nombre', 'el nombre ingresado', cls.__clean_nombre),
            ('precio', 'el precio ingresado', cls.__clean_precio)
        ]

    @classmethod
    def _get_unique_check(cls, fields):
        return models.Q(nombre=fields['nombre'])
    
    @classmethod
    def __clean_tipo(cls, post):
        return cls._clean_select(post['tipo'], cls.TIPOS)

    @classmethod
    def __clean_nombre(cls, post):
        return cls._clean_name_alnum(post['nombre'])

    @classmethod
    def __clean_precio(cls, post):
        return cls._clean_float_positive(post['precio'])


class Lugar(BaseModel):
    PROVINCIAS = (
        'Buenos Aires',
        'Catamarca',
        'Chaco',
        'Chubut',
        'Córdoba',
        'Corrientes',
        'Entre Ríos',
        'Formosa',
        'Jujuy',
        'La Pampa',
        'La Rioja',
        'Mendoza',
        'Misiones',
        'Neuquén',
        'Río Negro',
        'Salta',
        'San Juan',
        'San Luis',
        'Santa Cruz',
        'Santa Fe',
        'Santiago del Estero',
        'Tierra del Fuego',
        'Tucumán'
    )

    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=max(len(i) for i in PROVINCIAS))

    def __str__(self):
        return f'{self.ciudad}, {self.provincia}'
    
    def get_context(self):
        return {'provincias': self.PROVINCIAS}
    
    def _get_cant_modify_message(self):
        return f'No se puede modificar el lugar \'{self}\' ya que existe al menos una ruta que lo contiene como origen o destino.'
    
    def _get_not_unique_message(self, other):
        return f'Ya existe un lugar con nombre de ciudad \'{self.ciudad}\' y provincia \'{self.provincia}\'.'

    def _get_creation_message(self):
        return f'Se creó el lugar \'{self}\' con éxito.'
    
    def _get_modification_message(self):
        return f'Se modificó el lugar con éxito.'
    
    def _check_can_modify(self):
        return Ruta.find_first(models.Q(origen=self) | models.Q(destino=self)) is None

    @classmethod
    def _get_field_cleaners(cls):
        return (
            ('ciudad', 'la ciudad ingresada', cls.__clean_ciudad),
            ('provincia', 'la provincia ingresada', cls.__clean_provincia)
        )
    
    @classmethod
    def _get_unique_check(cls, fields):
        return models.Q(ciudad=fields['ciudad']) & models.Q(provincia=fields['provincia'])
    
    @classmethod
    def __clean_ciudad(cls, post):
        return cls._clean_name_alpha(post['ciudad'])
    
    @classmethod
    def __clean_provincia(cls, post):
        return cls._clean_select(post['provincia'], cls.PROVINCIAS)


class Ruta(BaseModel):
    origen = models.ForeignKey(Lugar, on_delete=models.SET_NULL, null=True, related_name='lugar_origen_set')
    destino = models.ForeignKey(Lugar, on_delete=models.SET_NULL, null=True, related_name='lugar_destino_set')
    combi = models.ForeignKey(Combi, on_delete=models.SET_NULL, null=True)
    distancia = models.FloatField(default=0)
    duracion = models.DurationField()

    def __str__(self):
        return f'{self.origen} -> {self.destino} ({self.combi})'
    
    def get_context(self):
        return {
            'lugares': Lugar.find_all(),
            'combis': Combi.find_all(),
            'horas': '0' if self.duracion is None else int(self.duracion.total_seconds() // 3600),
            'minutos': '0' if self.duracion is None else int(self.duracion.total_seconds() // 60 % 60)
        }
    
    def _get_cant_modify_message(self):
        return f'No se puede modificar la ruta \'{self}\' ya que existe al menos un viaje que la contiene.'

    def _get_not_unique_message(self, other):
        return f'Ya existe una ruta con origen \'{self.origen}\', destino \'{self.destino}\' y combi \'{self.combi}\'.'

    def _get_creation_message(self):
        return f'Se creó la ruta \'{self}\' con éxito.'
    
    def _get_modification_message(self):
        return f'Se modificó la ruta con éxito.'
    
    def _check_can_modify(self):
        return Viaje.find_first(models.Q(ruta=self)) is None
    
    @classmethod
    def _get_field_cleaners(cls):
        return (
            ('origen', 'el origen ingresado', cls.__clean_origen),
            ('destino', 'el destino ingresado', cls.__clean_destino),
            ('combi', 'la combi ingresada', cls.__clean_combi),
            ('distancia', 'la distancia ingresada', cls.__clean_distancia),
            ('duracion', 'la duracion ingresada', cls.__clean_duracion)
        )
    
    @classmethod
    def _get_unique_check(cls, fields):
        return models.Q(origen=fields['origen']) & models.Q(destino=fields['destino']) & models.Q(combi=fields['combi'])
    
    def _do_extra_validations(self):
        if self.origen == self.destino:
            raise ValidationError('El origen y el destino ingresados no pueden ser iguales.')

    @classmethod
    def __clean_origen(cls, post):
        return cls._clean_object_ref(post['origen'], Lugar)
    
    @classmethod
    def __clean_destino(cls, post):
        return cls._clean_object_ref(post['destino'], Lugar)
    
    @classmethod
    def __clean_combi(cls, post):
        return cls._clean_object_ref(post['combi'], Combi)
    
    @classmethod
    def __clean_distancia(cls, post):
        return cls._clean_float_positive(post['distancia'])

    @classmethod
    def __clean_duracion(cls, post):
        try:
            horas = cls._clean_integer(post['horas'])
        except ValidationError:
            raise ValidationError('las horas debe ser un número válido')

        try:
            minutos = cls._clean_integer(post['minutos'])
        except ValidationError:
            raise ValidationError('los minutos debe ser un número válido')

        if horas < 0:
            raise ValidationError('las horas debe ser un número positivo')

        if minutos < 0:
            raise ValidationError('los minutos debe ser un número positivo')
        if minutos > 59:
            raise ValidationError('los minutos no pueden ser mayores que 59')

        return datetime.timedelta(seconds=((horas * 60 + minutos) * 60))


class Viaje(BaseModel):
    ruta             = models.ForeignKey(Ruta, on_delete=models.SET_NULL, null=True)
    fecha_de_salida  = models.DateTimeField()
    hora_de_salida   = models.TimeField()
    precio           = models.FloatField(default=0)
    pasajes_vendidos = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default='Pendiente')

    def __str__(self):
        return f'{self.ruta} ({str(self.fecha_de_salida.day) +"/"+ str(self.fecha_de_salida.month) +"/"+ str(self.fecha_de_salida.year)} {self.hora_de_salida})'
    
    @property
    def pasajes(self):
        return Pasaje.find_all(models.Q(viaje=self))
    
    def get_context(self):
        if self.fecha_de_salida:
            fds = self.fecha_de_salida
        else:
            fds = datetime.date.today()

        if self.hora_de_salida:
            hds = self.hora_de_salida
        else:
            hds = datetime.datetime.strptime('00:00', '%H:%M')

        return {'rutas': Ruta.find_all(), 'fecha_de_salida': fds.strftime('%Y-%m-%d'), 'hora_de_salida': hds.strftime('%H:%M')}

    def _get_cant_modify_message(self):
        return f'No se puede modificar el viaje \'{self}\' ya que tiene uno o mas pasajes vendidos.'

    def _get_not_unique_message(self, other):
        return f'Ya existe un viaje con la ruta \'{self.ruta}\' y fecha de salida \'{self.fecha_de_salida}\'.'

    def _get_creation_message(self):
        return f'Se creó el viaje \'{self}\' con éxito.'
    
    def _get_modification_message(self):
        return f'Se modificó el viaje con éxito.'
    
    def _check_can_modify(self):
        return self.pasajes_vendidos == 0

    @classmethod
    def _get_field_cleaners(cls):
        return (
            ('ruta', 'la ruta ingresada', cls.__clean_ruta),
            ('fecha_de_salida', 'la fecha de salida ingresada', cls.__clean_fecha_de_salida),
            ('hora_de_salida', 'la hora de salida ingresada', cls.__clean_hora_de_salida),
            ('precio', 'el precio ingresado', cls.__clean_precio)
        )
    
    @classmethod
    def _get_unique_check(cls, fields):
        return models.Q(ruta=fields['ruta']) & models.Q(fecha_de_salida=fields['fecha_de_salida'])
    
    def _do_extra_validations(self):
        otros_viajes = Viaje.find_all(models.Q(fecha_de_salida=self.fecha_de_salida))
        for viaje in otros_viajes:
            if viaje != self and viaje.ruta.combi == self.ruta.combi:
                raise ValidationError('La combi perteneciente a la ruta seleccionada se encuentra asociada a otro viaje en la misma fecha.')
    
    @classmethod
    def __clean_ruta(cls, post):
        return cls._clean_object_ref(post['ruta'], Ruta)

    @classmethod
    def __clean_fecha_de_salida(cls, post):
        return cls._clean_date_in_future(post['fecha_de_salida'])

    @classmethod
    def __clean_hora_de_salida(cls, post):
        return cls._clean_hour(post['hora_de_salida'])
    
    @classmethod
    def __clean_precio(cls, post):
        return cls._clean_float_positive(post['precio'])

    @property
    def esta_disponible(self):
        return self.estado == "Pendiente"

    @classmethod
    def get_viajes_disponibles(cls, origen, destino, fecha_de_salida):
        viajes = Viaje.find_all()
        viajes_disponibles = []

        #Formateo la fecha de salida ingresada en el HTML
        year = fecha_de_salida.split("-")[0]
        month = fecha_de_salida.split("-")[1]
        day = fecha_de_salida.split("-")[2]
        fechaFormateada = (day + "/" + month + "/" + year + " 00:00:00.000000")
        fecha = datetime.datetime.strptime(fechaFormateada, '%d/%m/%Y %H:%M:%S.%f')

        for viaje in viajes:

            #Formateo la fecha del viaje actual para que tenga el mismo formato que la ingresada, y así poder compararlas
            fds = str(viaje.fecha_de_salida)
            year = fds[0] + fds[1] + fds[2] + fds[3]
            month = fds[5] + fds[6]
            day = fds[8] + fds[9]
            fecha_formateada = (day + "/" + month + "/" + year + " 00:00:00.000000")
            fecha_actual = datetime.datetime.strptime(fecha_formateada, '%d/%m/%Y %H:%M:%S.%f')

            if viaje.ruta.origen.pk == origen and viaje.ruta.destino.pk == destino and \
               fecha_actual == fecha and viaje.pasajes_vendidos < viaje.ruta.combi.asientos and viaje.esta_disponible:
                viajes_disponibles.append(viaje)

        return viajes_disponibles

    @property
    def get_asientos_disponibles(self):
        return self.ruta.combi.asientos - self.pasajes_vendidos

    def reembolsar(self):
        self.pasajes_vendidos -= 1
        self.save()

    def finalizar(self):
        self.estado = "Finalizado"
        self.save()
        responseData = {
            'result': 'OK',
            'message': f'Se finalizó el viaje \'{self.ruta}\' de forma exitosa.'
        }
        return responseData

    def iniciar(self):
        self.estado = "Iniciado"
        self.save()
        responseData = {
            'result': 'OK',
            'message': f'Se inició el viaje \'{self.ruta}\' de forma exitosa.'
        }
        return responseData

    def cancelar(self):
        self.estado = "Cancelado"
        self.save()
        if self.pasajes_vendidos > 0:
            responseData = {
                'result': 'OK',
                'message': f'Se cancelo el viaje de forma exitosa y se reembolzaron {self.pasajes_vendidos} pasajes.'
            }
        else:
            responseData = {
                'result': 'OK',
                'message': f'El viaje \'{self.ruta}\' ha sido cancelado de forma exitosa.'
            }
        return responseData

    def delete(self):
        if self.estado == "Finalizado" or self.estado == "Cancelado":
            responseData = {
                'result': 'OK',
                'message': 'Se ha eliminado el viaje  de forma exitosa.'
            }
            super(Viaje, self).delete()
            return responseData

        elif self.pasajes_vendidos > 0:
            responseData = {
                'result': 'Error',
                'message': 'No se puede eliminar el viaje seleccionado dado que ya se vendieron pasajes para el mismo'
            }
            return responseData
        else:
            responseData = {
                'result': 'OK',
                'message': 'Se ha eliminado el viaje  de forma exitosa.'
            }
            super(Viaje, self).delete()
            return responseData

class Pasaje(BaseModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    viaje = models.ForeignKey(Viaje, on_delete=models.SET_NULL, null=True)
    precio = models.FloatField(default=0)
    estado = models.CharField(max_length=100, default="Pendiente")

    @property
    def get_estado(self):
        #Estados propios posibles de un pasaje, sin contar los estados posibles de un viaje
        print(self.viaje.estado)
        print(self.estado)
        if self.viaje.estado in ('Iniciado', 'Finalizado') and self.estado == 'Aceptado':
            return self.viaje.estado
        estados = ["Ausente", "Rechazado", "Cancelado", "Aceptado"]
        if self.estado in estados:
            return self.estado
        return self.viaje.estado
    
    @property
    def ventas_de_insumos(self):
        return VentaInsumo.find_all(models.Q(pasaje=self))

    @property
    def get_precio_insumos_comestibles(self):
        total = 0
        for insumo in self.ventas_de_insumos:
            total += insumo.precio
        return total

    @classmethod
    def get_pasajes_de_cliente(cls, username):
        pasajes = Pasaje.find_all()
        pasajes_del_usuario = []

        for pasaje in pasajes:
            if not pasaje.viaje.habilitado:
                continue
            if pasaje.cliente and pasaje.cliente.get_username() == username:
                pasajes_del_usuario.append(pasaje)

        return pasajes_del_usuario

    @property
    def get_total_pagado(self):
        return self.precio + self.get_precio_insumos_comestibles

    @property
    def get_reembolso(self):
        fecha = self.viaje.fecha_de_salida
        hora = self.viaje.hora_de_salida
        fecha = datetime.datetime(fecha.year, fecha.month, fecha.day, hour=hora.hour, minute=hora.minute)
        now = datetime.datetime.now()
        anticipacion = abs(((now - fecha).total_seconds() / 3600))
        print(fecha)
        print(now)
        print(anticipacion)

        # Si se cancela la compra con 48 horas de anticipación no va a tener recargo.
        # Se le devuelve el monto total del viaje.
        if anticipacion > 48:
            return self.get_total_pagado

        # Si lo hace 24 horas antes se le devuelve el 50%.
        if 24 < anticipacion <= 48:
            return self.get_total_pagado / 2

        # Si se cancela el mismo día no se le devuelve nada.
        return 0

    def reembolsar(self):
        total_a_reembolsar = self.get_reembolso

        self.viaje.reembolsar()

        self.estado = 'Cancelado'
        self.save()

        responseData = {
            'result': 'OK',
            'message': 'Se canceló el pasaje de forma exitosa. Se reembolsaron $' + str(total_a_reembolsar)
        }

        return responseData

    def registrar_ausencia(self):
        self.estado = "Ausente"
        self.save()

    @property
    def puede_registrar_sintomas_o_marcar_ausente(self):
        return self.estado == "Pendiente" and self.estado != "Ausente"

    @classmethod
    def get_pasajes_pendientes(cls, obj_id):
        return Pasaje.find_all(models.Q(viaje=obj_id) & models.Q(estado='Pendiente')).count() > 0

    @classmethod
    def get_pasajes_aceptados(cls, obj_id):
        return Pasaje.find_all(models.Q(viaje=obj_id) & models.Q(estado='Aceptado')).count() > 0

    def aceptar(self):
        print(self.estado)
        self.estado = "Aceptado"
        print(self.estado)
        self.save()
    
    def rechazar(self):
        self.estado = "Rechazado"
        c = Cliente.find_first(models.Q(pk=self.cliente))
        c.bloquear_cuenta()
        testeo = TesteoCovidPositivo()
        testeo.cliente = c
        testeo.fecha_bloqueo = datetime.datetime.now()
        testeo.save()
        self.save()

class VentaInsumo(BaseModel):
    pasaje = models.ForeignKey(Pasaje, on_delete=models.SET_NULL, null=True)
    insumo = models.ForeignKey(InsumoComestible, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField(default=0)

    @property
    def precio(self):
        return self.insumo.precio * self.cantidad


class Comentario(BaseModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    texto = models.CharField(max_length=280)
    fecha = models.DateTimeField()
    hora = models.TimeField()
    editado = models.BooleanField(default=False)

    @classmethod
    def create_comentario(cls, cliente, texto):
        comentario = Comentario()
        comentario.cliente = cliente
        comentario.texto = texto
        comentario.fecha = datetime.datetime.today()
        comentario.hora = datetime.datetime.today().time()
        comentario.save()

    def editar(self, texto):
        self.texto = texto
        self.editado = True
        self.fecha = datetime.datetime.today()
        self.hora = datetime.datetime.today().time()
        self.save()

    @property
    def get_nombre_usuario(self):
        return self.cliente.last_name + ", " + self.cliente.first_name

class TesteoCovidPositivo(BaseModel):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    fecha_bloqueo = models.DateTimeField(default=None, null=True)