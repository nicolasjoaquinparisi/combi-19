
# Combi-19

  

**Combi-19** es un sitio web desarrollado para la materia Ingeniería de Software 2 de la carrera Licenciatura en Sistemas de la Facultad de Informática de la UNLP.

El objetivo principal de la aplicación es poder brindar la posibilidad de comprar pasajes de combis para realizar viajes de media y larga distancia.

  

Existen diferentes tipos de usuarios en la aplicación y cada uno de ellos con permisos específicos para poder llevar a cabo determinados requerimientos:

- Usuario no registrado o visitante: puede ver los viajes que estén dados de altas, ver si hay pasajes disponibles para comprar. Pueden darse de alta e iniciar sesión. En caso de querer comprar un pasaje, es necesario que se autentiquen en el sistema.

- Usuario registrado: puede iniciar/cerrar sesión, ver, comprar pasajes, ver su historial de viajes, modificar su perfil.

- Chofer: este usuario es dado de alta por el admin. Puede modificar los estados de los viajes, iniciándolos, finalizándolos, cancelándolos. Tiene disponible una opción para ver sus viajes asignados, ver quiénes han comprado pasajes para esos viajes, tomar una asistencia donde se realiza la consulta de si han tenido síntomas compatibles con COVID-19. En caso de no haber pasado este test, el chofer cancelará el pasaje de la persona en cuestión y no podrá viajar.

- Admin: puede dar de alta los lugares, rutas, combis, choferes, viajes. Puede ver también estadísticas como por ejemplo, la cantidad de personas que realizaron viajes entre dos fechas, como también la cantidad de personas que tuvieron síntomas compatibles con COVID-19.

  

## Notas

En caso de querer correr el servidor de forma local, es necesario crear una base de datos teniendo en cuenta la configuración del archivo settings.py ubicado en /sc19/settings.py.

Ejecutando el script `init.sh` se instalarán las dependencias necesarias. En este script se instalarán diferentes dependencias y también se realizarán las migraciones a la base de datos, es por esto que es necesario realizar el paso anterior.

Para la creación del admin ejecutar el comando: `python manage.py createsuperuser`

Para correr el servidor ejecutar el comando: `python manage.py runserver`

  

## Requerimientos

Para poder correr esta aplicación es necesario que tenga instalado:

- Python 3.9
- Django 4.0.3
- Postgresql 14.2-2

  

## Desarrolladores

 - Camino, David
 - Garofalo, Pedro
 - Parisi, Nicolás Joaquín
