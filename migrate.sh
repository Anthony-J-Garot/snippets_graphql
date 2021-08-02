#!/bin/bash

# Run this after you change a model in the models.py file.
#
# If he doesn't come right away:
#
#	$ rm snippets/migrations/*.py
#	$ sqlite3 db.sqlite3
#	> delete from django_migrations where app = 'snippets';
#	> drop table snippets_snippet;
#	.quit
#
#	$ ./migrate
#	$ python3 manage.py loaddata fixtures.json


PYTHON=/usr/bin/python3
APP=snippets

$PYTHON manage.py makemigrations $APP
if [[ $? -eq 0 ]]; then
    $PYTHON manage.py migrate
fi
