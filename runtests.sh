#!/bin/bash

# HOWTO spread unit tests over multiple files
# https://stackoverflow.com/questions/6248510/how-to-spread-django-unit-tests-over-multiple-files

PYTHON=/usr/bin/python3
# Can't use IPython interpretter for running unit tests
#IPYTHON=/home/anthony/.local/bin/ipython
APP=snippets

# This allows me to simply put "breakpoint()" in code.
#export PYTHONBREAKPOINT="ipdb.set_trace"
export PYTHONBREAKPOINT="pudb.set_trace"

# NOTE: Not using -Wa because graphene has two deprecation warnings
# 		-Wa = tells python to display warnings (can get noisy)
#PYTHON_ARGS=-Wa
PYTHON_ARGS=

# MANAGE_OPTIONS
# 		--pattern="tests_*.py"
#		--keepdb = don't destroy test DB when done
#		--settings=path.to.settings
#		--debug-mode = sets settings.DEBUG to True (as long as not overwritten in setUpClass())
#		--debug-sql = dumps SQL transactions. Useful when relevant; otherwise, a lot of clutter.
#		--reverse = run tests in reverse order
#		-v [0-3] = verbose mode. I haven't seen much added benefit to this flag.
#		--pdb = runs ipdb; doesn't work with --debug-sql for some reason ???
MANAGE_OPTS="--keepdb --debug-mode --reverse --failfast -v 2"

if [[ "$1" == "" ]]; then
	# All the things!
	CMD="$PYTHON $PYTHON_ARGS manage.py test $MANAGE_OPTS $APP"
	echo $CMD
	eval $CMD
else
	if [[ "$2" == "" ]]; then
		# Specific file of tests, e.g. test_queries
		CMD="$PYTHON $PYTHON_ARGS manage.py test $MANAGE_OPTS $APP.tests.$1"
		echo $CMD
		eval $CMD

	else
		# Specific test within a file
		CMD="$PYTHON $PYTHON_ARGS manage.py test $MANAGE_OPTS $APP.tests.$1.SnippetsTestCase.$2"
		echo $CMD
		eval $CMD
	fi
fi


