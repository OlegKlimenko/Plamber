service nginx stop
service gunicorn stop

git pull
pip install -r requirements.txt

python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate

service nginx start
service gunicorn start
