#!/bin/bash

# To create table in the database with Django is to create a django model 
# with all required fields and then create migrations and apply them.
# So:
# 	1. Alter snippets/models.py
#	2. Run this script 
#
# And if he doesn't come right away . . . .
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

# Give a command line option to actually load the data
if [[ "$1" -eq "load" ]]; then
	$PYTHON manage.py loaddata fixtures.json
else
	# Normal use is to make the migrations then migrate.
	$PYTHON manage.py makemigrations $APP
	if [[ $? -eq 0 ]]; then
		$PYTHON manage.py migrate
	fi
fi
