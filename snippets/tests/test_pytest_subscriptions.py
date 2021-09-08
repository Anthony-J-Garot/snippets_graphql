"""
Adapted from pytest unit tests found in DjangoChannelsGraphqlWs package.
I've ported these to unittest in test_subscriptions.py. Leaving this file
around as an example of how tests might be written in pytest.

These tests are NOT invoked through the runtests.sh test runner.

I should have maybe looked more at `1.14.2  Using pytest` of
https://readthedocs.org/projects/graphene-django/downloads/pdf/stable/

# pytest --capture=no snippets/tests/test_pytest_subscriptions.py
# -or-
# poetry run pytest --capture=no snippets/tests/test_pytest_subscriptions.py

"""

# NOTE: In this file we use `strict_ordering=True` to simplify testing.

import uuid
import json

import channels
import django
import graphene
import pytest

import channels_graphql_ws
import channels_graphql_ws.testing
from django.core.asgi import get_asgi_application

from mysite.schema import Mutation, Subscription

from django.core.management import call_command


# How to populate fixture data in Django using pytest
# https://flowfx.de/blog/populate-your-django-test-database-with-pytest-fixtures/
# and this has a very similar example as below:
# https://pytest-django.readthedocs.io/en/latest/database.html
@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'fixtures.json')
        print()
        print("__ FIXTURES LOADED __")


# gql originally came from conftest.py, a pytest thing, which
# contained auxiliary files for use in testing.
#
# I wanted to get rid of the pytest dependence as much as possible.
#
# db = Pytest fixture - Require a django test database.
# request = https://docs.pytest.org/en/6.2.x/reference.html#std-fixture-request
@pytest.fixture
def gql(db, request):
    """
    PyTest fixture for testing GraphQL WebSocket backends.

    The fixture provides a method to setup GraphQL testing backend for
    the given GraphQL schema (query, mutation, and subscription). In
    particular: it sets up an instance of `GraphqlWsConsumer` and an
    instance of `GraphqlWsClient`. The former one is returned
    from the function.

    Syntax:
        gql(
            *,
            query=None,
            mutation=None,
            subscription=None,
            consumer_attrs=None,
            communicator_kwds=None
        ):

    Args:
        query: Root GraphQL query. Optional.
        mutation: Root GraphQL subscription. Optional.
        subscription: Root GraphQL mutation. Optional.
        consumer_attrs: `GraphqlWsConsumer` attributes dict. Optional.
        communicator_kwds: Extra keyword arguments for the Channels
            `channels.testing.WebsocketCommunicator`. Optional.

    Returns:
        An instance of the `GraphqlWsClient` class which has many
        useful GraphQL-related methods, see the `GraphqlWsClient`
        class docstrings (in channels_graphql_ws) for details.

    Use like this:
    ```
    def test_something(gql):
        client = gql(
            # GraphQl schema.
            query=MyQuery,
            mutation=MyMutation,
            subscription=MySubscription,
            # `GraphqlWsConsumer` settings.
            consumer_attrs={"strict_ordering": True},
            # `channels.testing.WebsocketCommunicator` settings.
            communicator_kwds={"headers": [...]}
        )
        ...
    ```

    """
    # NOTE: We need Django DB to be initialized each time we work with
    # `GraphqlWsConsumer`, because it uses threads and sometimes calls
    # `django.db.close_old_connections()`.

    # Anthony - turns out this line isn't needed.
    del db

    issued_clients = []

    def client_constructor(
            *,
            query=None,
            mutation=None,
            subscription=None,
            consumer_attrs=None,
            communicator_kwds=None,
    ):
        """Setup GraphQL consumer and the communicator for tests."""

        class ChannelsConsumer(channels_graphql_ws.GraphqlWsConsumer):
            """Channels WebSocket consumer for GraphQL API."""

            schema = graphene.Schema(
                query=query,
                mutation=mutation,
                subscription=subscription,
                auto_camelcase=True,  # ANTHONY - I wonder why he set this?
            )

        # Set additional attributes to the `ChannelsConsumer`.
        if consumer_attrs is not None:
            for attr, val in consumer_attrs.items():
                setattr(ChannelsConsumer, attr, val)

        application = channels.routing.ProtocolTypeRouter(
            {
                "http": get_asgi_application(),  # ANTHONY - to get rid of warning

                "websocket": channels.routing.URLRouter(
                    [django.urls.path("graphql/", ChannelsConsumer.as_asgi())]
                )
            }
        )

        transport = channels_graphql_ws.testing.GraphqlWsTransport(
            application=application,
            path="graphql/",
            communicator_kwds=communicator_kwds,
        )

        client = channels_graphql_ws.testing.GraphqlWsClient(transport)
        issued_clients.append(client)
        return client

    # ANTHONY - so it appears that we return the inner function. Thus
    # dbq() is called a closure factory function.
    yield client_constructor

    # Assert all issued client are properly finalized.
    for client in reversed(issued_clients):
        assert (
            not client.connected
        ), f"Test has left connected client: {request.node.nodeid}!"


# Improve output of `pytest -s` by adding EOL in the beginning.
# This should be the last pytest.fixture entry.
@pytest.fixture(scope="function", autouse=True)
def extra_print_in_the_beginning():
    print()
    print()
    print("----> START pytest -s output below <----")


# pytest --capture=no snippets/tests/test_pytest_subscriptions.py -k 'test_confirmation_enabled'
#
# Test that the subscription confirmation message is received when enabled.
@pytest.mark.asyncio
async def test_confirmation_enabled(gql, django_db_setup, event_loop):
    print("Establish WebSocket GraphQL connections with subscription confirmation.")

    print(event_loop)
    # Can't do this or the update will falter
    # event_loop.set_debug(True)

    # gql was defined in conftest.py, which is a pytest file
    client = gql(
        mutation=Mutation,
        subscription=Subscription,
        consumer_attrs={"strict_ordering": True, "confirm_subscriptions": True},
    )

    await client.connect_and_init()

    print("Subscribe & check there is a subscription confirmation message.")

    sub_op_id = await client.send(
        msg_type="start",
        payload={
            "query":
                '''
subscription subNoGroup {
  onSnippetNoGroup {
    sender
    snippet {
      id
      title
      private
      created
    }
    ok
  }
}
                ''',
            "operationName": "subNoGroup",
        },
    )

    resp = await client.receive(assert_id=sub_op_id, assert_type="data")
    assert resp == {"data": None}

    print("Trigger the subscription with a MUTATION.")

    mut_op_id = await client.send(
        msg_type="start",
        payload={
            "query":
                '''
mutation mutUpdateSnippet {
  updateSnippet(id: "2", input: {
        title: "Updated Title",
        body: "Homer simpson has left the building",
        private: false
  }) {
    snippet {
      title
      body
      private
    }
    ok
  }
}
                ''',
            "operationName": "mutUpdateSnippet",
        },
    )

    print("Receive back from the MUTATION")

    # See what's returned as far as data
    resp = await client.receive(assert_id=mut_op_id, assert_type="data", raw_response=False)
    print(json.dumps(resp, indent=4))
    assert resp["data"]["updateSnippet"]["ok"] is True

    # Wait for a "complete" message too.
    # This is more of an internal thing. Don't expect a groovy response.
    await client.receive(assert_id=mut_op_id, assert_type="complete", raw_response=False)

    print("Check that subscription notification received.")

    resp = await client.receive(assert_id=sub_op_id, assert_type="data", raw_response=False)
    print(json.dumps(resp, indent=4))
    assert resp["data"]["onSnippetNoGroup"]["ok"] is True

    await client.assert_no_messages(
        "Unexpected message received at the end of the test!"
    )

    await client.finalize()


# pytest --capture=no snippets/tests/test_pytest_subscriptions.py -k 'test_confirmation_disabled'
#
# Test subscription confirmation message absent when disabled."""
@pytest.mark.asyncio
async def test_confirmation_disabled(gql, django_db_setup):
    print("Establish WebSocket GraphQL connections w/o a subscription confirmation.")

    # gql was defined in conftest.py, which is a pytest file
    client = gql(
        mutation=Mutation,
        subscription=Subscription,
        consumer_attrs={"strict_ordering": True, "confirm_subscriptions": False},
    )

    await client.connect_and_init()

    print("Subscribe & check there is no subscription confirmation message.")

    sub_op_id = await client.send(
        msg_type="start",
        payload={
            "query":
                '''
subscription subNoGroup {
  onSnippetNoGroup {
    sender
    snippet {
      id
      title
      private
      created
    }
    ok
  }
}
                ''',
            "operationName": "subNoGroup",
        },
    )

    await client.assert_no_messages("Subscribe responded with a message!")

    print("Trigger the subscription.")

    mut_op_id = await client.send(
        msg_type="start",
        payload={
            "query":
                '''
mutation mutUpdateSnippet {
  updateSnippet(id: "2", input: {
        title: "Updated Title",
        body: "Homer simpson has left the building",
        private: false
  }) {
    snippet {
      title
      body
      private
    }
    ok
  }
}
                ''',
            "operationName": "mutUpdateSnippet",
        },
    )

    # See what's returned as far as data
    resp = await client.receive(assert_id=mut_op_id, assert_type="data", raw_response=False)
    print(json.dumps(resp, indent=4))
    assert resp["data"]["updateSnippet"]["ok"] is True

    # Wait for a "complete" message too.
    # This is more of an internal thing. Don't expect a groovy response.
    await client.receive(assert_id=mut_op_id, assert_type="complete", raw_response=False)

    print("Check that subscription notification received.")

    resp = await client.receive(assert_id=sub_op_id, assert_type="data", raw_response=False)
    print(json.dumps(resp, indent=4))
    assert resp["data"]["onSnippetNoGroup"]["ok"] is True

    await client.assert_no_messages(
        "Unexpected message received at the end of the test!"
    )

    await client.finalize()


# pytest --capture=no snippets/tests/test_pytest_subscriptions.py -k 'test_custom_confirmation_message'
#
# Test custom confirmation message.
@pytest.mark.asyncio
async def test_custom_confirmation_message(gql, django_db_setup):
    print("Establish WebSocket GraphQL connections with a custom confirmation message.")

    expected_data = uuid.uuid4().hex
    print("expected_data [{}]".format(expected_data))
    expected_error = RuntimeError(uuid.uuid4().hex)

    # gql was defined in conftest.py, which is a pytest file
    client = gql(
        mutation=Mutation,
        subscription=Subscription,
        consumer_attrs={
            "strict_ordering": True,
            "confirm_subscriptions": True,
            "subscription_confirmation_message": {
                "data": expected_data,
                "errors": [expected_error],
            },
        },
    )
    await client.connect_and_init()

    print("Subscribe & check there is a subscription confirmation message.")

    sub_op_id = await client.send(
        msg_type="start",
        payload={
            "query":
                '''
subscription subNoGroup {
  onSnippetNoGroup {
    sender
    snippet {
      id
      title
      private
      created
    }
    ok
  }
}
                ''',
            "operationName": "subNoGroup",
        },
    )

    try:
        await client.receive(assert_id=sub_op_id, assert_type="data")
    except channels_graphql_ws.GraphqlWsResponseError as error:
        expected_errors = [
            {"message": f"{type(expected_error).__name__}: {expected_error}"}
        ]

        assert error.response['payload']['errors'] == expected_errors, "Wrong confirmation errors received!"
        assert error.response['payload'] == {
            "data": expected_data,
            "errors": expected_errors,
        }, "Wrong subscription confirmation message received!"

    print("Trigger the subscription.")

    mut_op_id = await client.send(
        msg_type="start",
        payload={
            "query":
                '''
mutation mutUpdateSnippet {
  updateSnippet(id: "2", input: {
        title: "Updated Title",
        body: "Homer simpson has left the building",
        private: false
  }) {
    snippet {
      title
      body
      private
    }
    ok
  }
}
                ''',
            "operationName": "mutUpdateSnippet",
        },
    )

    # See what's returned as far as data
    resp = await client.receive(assert_id=mut_op_id, assert_type="data", raw_response=False)
    print(json.dumps(resp, indent=4))
    assert resp["data"]["updateSnippet"]["ok"] is True

    # Wait for a "complete" message too.
    # This is more of an internal thing. Don't expect a groovy response.
    await client.receive(assert_id=mut_op_id, assert_type="complete", raw_response=False)

    print("Check that subscription notification received.")

    resp = await client.receive(assert_id=sub_op_id, assert_type="data", raw_response=False)
    print(json.dumps(resp, indent=4))
    assert resp["data"]["onSnippetNoGroup"]["ok"] is True

    await client.assert_no_messages(
        "Unexpected message received at the end of the test!"
    )

    await client.finalize()
