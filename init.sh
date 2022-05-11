pip install django-clearcache
pip install psycopg2
pip install pytz
python -m pip install django-browser-reload

python -m pip install django-tailwind

docker-compose up

python manage.py makemigrations combiapp
python manage.py migrate
