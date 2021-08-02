#!/bin/bash

# This will only work if csrf_exempt() is used in the urls.py file
# around path 'graphql/'.

BIND=0.0.0.0
PORT=4000

curl \
	-X POST \
	-H "Content-Type: application/json" \
	--data '{ "query": "{ allSnippets { id } }" }' \
	http://$BIND:$PORT/graphql/


