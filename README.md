# Candy Delivery App
## Description
An entrance test project for passing the selection to the Yandex backend development school.

## Installation
You will need to go through the following steps to install this application:
1. Install PostgreSQL.
2. Create the database.
3. Create a python virtual environment (optional, but recommended).
4. Install python dependencies.

### 1. PostgreSQL installation
Install PostgreSQL on Ubuntu:
```
sudo apt-get install postgresql postgresql-contrib
```
### 2. Database creation
Create user:
```
sudo -u postgres createuser YOUR_USERNAME
```
Create the database:
```
sudo -u YOUR_USERNAME createdb DATABASE_NAME
```
To set password you may run
```
sudo -u postgres psql
alter user YOUR_USERNAME with encrypted password 'YOUR_PASSWORD';
```
Enter `\q` or press _Ctrl+D_ to exit psql.

In order to access the database you may run the following command:
```
psql -U YOUR_USERNAME -d DATABASE_NAME
```
You may run `\conninfo` to check the postgres port number (default is 5432)

### 3. Virtual environment creation
Install python virtualenv package:
```
pip install virtualenv
```
Now go to the project folder and create virtual environment using
```
virtualenv env
```
Activate virtual environment by running
```
source env/bin/activate
```
### 4. Installing python dependencies
Having _requirements.txt_ in current working directory, run
```
pip install -r requirements.txt
```
## Running
### Setting environment variables.
You will need to provide Flask some additional information through environment variables.

First, you will need to set Flask _secret key_. For that, run python and then
enter following commands:
```
>>> import secrets
>>> secrets.token_hex(16)
```
You will see something like this:
```
>>> import secrets
>>> secrets.token_hex(16)
'597afd24a7f2d486acb01e20277598b1'
```
Copy the generated string and exit python with `exit()` command.
Then set secret key by pasting the copied string into the corresponding environment variable
like in the example below:
```
export SECRET_KEY="597afd24a7f2d486acb01e20277598b1"
```
To set variables related to database, enter the following commands by substituting the
values with those set during installation stage.
```
export DB_USERNAME="YOUR_USERNAME"
export DB_PASSWORD="YOUR_PASSWORD"
export DB_NAME="DATABASE_NAME"
```
### Making migrations.
Now we need to initialize the database and make migrations by running the following:
```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```
