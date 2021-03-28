# Candy Delivery App

## Installation
```
sudo apt-get update
sudo apt-get install postgresql libpq-dev postgresql-client postgresql-client-common
sudo -u postgres -i
   createuser vitaliy -P --interactive
   createdb delivery_dev
   psql delivery_t
? export PGPORT=5433
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```