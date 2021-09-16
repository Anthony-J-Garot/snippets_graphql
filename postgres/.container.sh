#!/bin/bash

# This contains only settings specific to the app

# https://hub.docker.com/_/postgres

# Parameters are:
#	local:container

ROOT=/home/anthony/Django/snippets_graphql/

DOCKER=/usr/bin/docker
IMAGE='postgres:13.3-buster'
NAME=postgres
ENVIRONMENT="-e POSTGRES_PASSWORD=${POSTGRES_PASSWORD}"
PORT='-p 5432:5432'
SHELL=/bin/bash
# Data
VOLUME1="-v $ROOT/postgres/pg_data/:/var/lib/postgresql/data/"
# Infile? For now, no.
VOLUME2="-v $ROOT/infile:/infile"
VOLUME="$VOLUME1"
