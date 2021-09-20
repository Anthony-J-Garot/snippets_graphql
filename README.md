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

This was the bread and butter of this example code because I 
could not find many online examples with fully functional code
and unit tests.

I scapeled code from the example in the
[datadvance/ DjangoChannelsGraphqlWs](https://github.com/datadvance/DjangoChannelsGraphqlWs) 
repo. He used pytest for his unit tests, which worked once I 
figured out what I needed to make pytest run. However, I am
more familiar with unittest; and my existing graphene tests 
for queries and mutations were already in unittest.

**Note:** There are two separate subscriptions within the App:

* OnSnippetTransaction (uses groups)
* OnSnippetNoGroup (used primarily through this example)

The first sends transactions to groups, and the second sends
transactions to everyone. Throughout the testing and front-end 
code, I used the no-group version because it was simpler.

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

This worked well enough, but didn't lend well to a React front-end.

**Note** I'm removing all Tokenless authentication. You can see that
code in v1.0 release. The reason is:

    Migrating to postgres, the unit tests fail for login:
    graphql.error.located_error.GraphQLLocatedError: connection already closed
    
    This is from create_cursor in psycop2.

    One suggestion is to pre-fetch data. I didn't chase that down.
    
    This guy has the same exact same issue:
    https://www.mail-archive.com/django-users@googlegroups.com/msg206235.html
    https://github.com/datadvance/DjangoChannelsGraphqlWs/issues/76

## authToken through JWT

I set up the backend with [django-graphql-jwt](https://github.com/flavors/django-graphql-jwt).
What this means on this React front-end is:

1. Uses a mutation to request a token.
2. Sends back the token through a header.

### Birth of the CustomUser model

I wanted everything in the User model, so I extended to the CustomUser
model and tacked on token. Thus I can check every transaction to see
if the user is still logged in and not rely on the front-end or token
expiration. That is, I can actually create a Logout function on the
back-end.

## GraphQL issue with User

Initially I had a text field "owner" to describe who created the
snippet. Then I changed this field to point to the auth_user table, 
i.e. a User model record.

A problem entered with the AnonymousUser, which isn't a real user in the database. Somewhere in DjangoModelFormMutation the "user" field is an ID!, which means required, despite the model being a ForeignKey with nulls expressly allowed. It turns out that I cannot send in null or 0 or any non-existent User user_id. The raised error comes from under the hood so I cannot readily intercept it. I decided to create a "noop" user with user_id 3. This will act as a real record for a Public User such that I can create records without being logged in.

# Migrating from sqlite3 to postgres

I'm running into the following error (again) while running the unit tests
in test_subscriptions/.

`django.db.utils.OperationalError: database table is locked: snippets_snippet`

I had that early into the project, and thought I had resolved it.
Apparently it will keep coming back until I switch to a better DB.

I will spin up a Docker instance of postgres. I've added some tooling
to make it easy to start. I didn't use a Dockerfile. 
Look in postgres/.container.sh for specifics.

## To start postgres server

```
$ cd postgres/
$ ./postgres.sh run
```

## Login to psql
``` 
$ ./postgres.sh shell
# psql -U postgres
```

## Build the snippets DB

```
Show databases
postgres=# \l

We need a DB owner
postgres=# CREATE USER django WITH PASSWORD '*************';

The Owner will create the DB and test DB
postgres=# CREATE DATABASE snippets WITH OWNER django ENCODING 'utf-8';
postgres=# CREATE DATABASE test_snippets WITH OWNER django ENCODING 'utf-8';

postgres=# ALTER USER django CREATEDB;    # NOTE below
```

NOTE: Per https://stackoverflow.com/a/63345849/4171820, I shouldn't 
give the django user CREATEDB permissions. But during development, 
if I add a user, it doesn't go into the test_snippets DB. Therefore, 
I AM giving the django user CREATEDB, and I can get rid of 
--keepdb in the test runner when I need to refresh the 
test_snippets DB.

## In Django

I put the postgres connection parameters into environment variables in 
~/.bash_profile for convenience. There are many ways to handle this, e.g.
AWS Secrets.

```
export POSTGRES_USER='django'
export POSTGRES_PASSWORD='****************'
```

## Migrate the data from SQLite3 to postgres

``` 
Get a full dump of all existing data in JSON format
$ ./create_fixtures.sh

Remove all migrations so we can have a single clean file
$ rm ./snippets/migrations/*

Build a migration script (based upon models.py)
$ python manage.py makemigrations

Now do the migration
$ python3 manage.py migrate

Not 100% sure what this does. :-D
$ python manage.py shell
In [1]: from django.contrib.contenttypes.models import ContentType
In [2]: ContentType.objects.all().delete()
Out[2]: (35, {'auth.Permission': 28, 'contenttypes.ContentType': 7})
In [3]: quit

Import all the things
$ python manage.py loaddata fixtures.json
```

Now look inside the DB using psql or PyCharm's Database
tool, and/or run some unit tests to see if everything is 
copasetic.

# Useful links / resources

- [GitHub repo tutorial](https://github.com/alexisrolland/flask-graphene-sqlalchemy/wiki/Flask-Graphene-SQLAlchemy-Tutorial#schema_peoplepy)
  with a lot of usable example code. A pity I found this late in the game.
- [This article](https://www.fullstacklabs.co/blog/django-graphene-rest-graphql)
also had a tutorial. By going through it, I added much
to the original "snippets" tutorial above.
- [This article](https://morningpython.com/2019/12/20/how-to-build-graphql-api-with-django-7-steps/)
was reasonable. He did point out using GraphiQL.
- [Graphene Documentation](https://readthedocs.org/projects/graphene-django/downloads/pdf/stable/)