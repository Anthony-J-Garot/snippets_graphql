# Overview

This project stems from a [YouTube video](https://www.youtube.com/watch?v=-0uxxht4mko),
which gave a high level overview of Query and Mutations.

He had a [GitHub snippets project](https://github.com/TheDumbfounds/snippetproject-basic)
that I cloned initially, but then added subscriptions and a Django interface:

`$ git clone git@github.com:TheDumbfounds/snippetproject-basic.git`

## Overall hierarchy

- mysite/ ⇨ project directory
- snippets/ ⇨  App directory
  - queries.py
  - mutations.py
  - subscriptions.py
- static/ ⇨ static assets

## URL routes

- /snippets/ - Django forms and templates for displaying snippet content
- /user - user authentication pages
- /admin - Django administration pages
- /graphql - endpoint for graphQL

## Other Cool Stuff

- Various authentication methods are used, and the snippets shown to the user are based upon primitive ACL.
- The "Snippets Real-time" (subscription) code dumps the JSON right into a &lt;textarea&gt; that you can see. Also look at the Javascript console to see connection information, etc.
- Lots and lots of comments

# Where to Start

Run `./runserver.sh` to get the ASGI/Channels web server running.
Go to the link it spits out on port 4000 (for me, it's `http://192.168.2.99:4000/`),
and you should be slingshotted to the Python/Djano App with 
a nav-bar chock full of useful links.

# Deviations from the original "Snippets example"

Although GraphiQL was included here for testing, it didn't connect to 
the GraphQL endpoint via WebSockets. I therefore pulled websockets code
in from the [datadvance/ DjangoChannelsGraphqlWs](https://github.com/datadvance/DjangoChannelsGraphqlWs) example.

I first pulled a primitive version of Subscriptions to start. Then I
was able to beef-up the code to send the entire "SnippetType" object 
across as a payload.

Eventually I got GraphQL speaking over WebSockets from a front-end
page, which is what I wanted in the first place.

Finally I began digging into Python/Django form pages to build a full-featured App.
Of course, this App doesn't actually do anything meaningful. It's a 
fully functional proof of concept with Python/Django, Channels, 
unit tests, Subscriptions, and GraphQL over WebSockets.

## Updating the model

I added a field to this guy's model, and I realized that updating the model
code didn't translate into the db.sqlite3 database automatically. 

See the script: `migrate.sh` for the approach.

These are the steps:

- First make the changes to the model.py code
- Now make the migration
  - `$ python3 manage.py makemigrations snippets`
- Then you can run the migration
- `$ python3 manage.py migrate`

## Subscriptions

This is really the bread and butter of this example code.

I scapeled code from the example in the
[datadvance/ DjangoChannelsGraphqlWs](https://github.com/datadvance/DjangoChannelsGraphqlWs) 
repo. He used pytest for his unit tests, which worked once I 
figured out what I needed to make pytest run. However, I am
more familiar with unittest; and my existing tests for queries
and mutations were already in unittest.

## Unit Tests for Subscriptions

This was somewhat painful because I was not familiar with pytest
when I began, and asynchronous code can be tricky even on 
platforms with which you *are* familiar.

Eventually I was able to shape the unit tests from the 
django-channels-graphql-ws package to suit my own subscriptions.

Eventually I was able to port each of the pytest subscription tests to 
unittest. I will leave the original pytest tests around for posterity.
Also because I may transition to pytest in the future. It looks to be
a more robust testing platform.

# Authentication

## Tokenless GraphQL Mutation Login

See the Login mutation.

This works well enough, but didn't lend well to a React front-end.

## authToken through JWT

I set up the backend with [django-graphql-jwt](https://github.com/flavors/django-graphql-jwt).
What this means on this React front-end is:

1. Uses a mutation to request a token.
2. Sends back the token through a header.

# Useful links / resources

- [GitHub repo tutorial](https://github.com/alexisrolland/flask-graphene-sqlalchemy/wiki/Flask-Graphene-SQLAlchemy-Tutorial#schema_peoplepy)
  with a lot of usable example code. A pity I found this late in the game.
- [This article](https://www.fullstacklabs.co/blog/django-graphene-rest-graphql)
also had a tutorial. By going through it, I added much
to the original "snippets" tutorial above.
- [This article](https://morningpython.com/2019/12/20/how-to-build-graphql-api-with-django-7-steps/)
was reasonable. He did point out using GraphiQL.
- [Graphene Documentation](https://readthedocs.org/projects/graphene-django/downloads/pdf/stable/)