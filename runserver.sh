#!/bin/bash

# I put this on port 4000 because I had been using 8000 for a lot of other
# projects. At present, I don't need anything more complex than Django's
# runserver for this project.

# Use 0.0.0.0 when using curl. I'm just hardcoding to .99 because then it 
# tells me the full URL when I run runserver.
#BIND=0.0.0.0
BIND=192.168.2.99
PORT=4000
PYTHON=/usr/bin/python3

$PYTHON manage.py runserver $BIND:$PORT
