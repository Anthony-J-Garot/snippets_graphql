#!/bin/bash

# Use this script to create fixture data.
# https://stackoverflow.com/questions/6153113/how-to-create-a-fixture-file
#
# To use the fixtures in unit tests, simply add to the top of the class:
#		fixtures = ['fixtures.json',]
# or whatever they're called.

PYTHON=/usr/bin/python3
PYTHON_ARGS=-Wa
APP=snippets
FIXTURES_FILE_ALL=fixtures.json
FLAGS="--natural-foreign --natural-primary -e contenttypes -e auth.Permission"

# Can pass in specific model, e.g. snippet


if [[ "$1" == "" ]]; then
    # Do all
    CMD="$PYTHON $PYTHON_ARGS manage.py dumpdata $FLAGS --indent 4 >$FIXTURES_FILE_ALL"
	echo $CMD
	eval $CMD
else
    # Do just the model requested.
    # I haven't actually used this, so it may need some adjustment.
    FIXTURES_DIR="./fixtures"
    if [[ ! -d $FIXTURES_DIR ]]; then
        mkdir $FIXTURES_DIR
    fi
    CMD="$PYTHON $PYTHON_ARGS manage.py dumpdata $APP.$1 $FLAGS --indent 4 >$FIXTURES_DIR/$1.json"
	echo $CMD
	eval $CMD
fi
