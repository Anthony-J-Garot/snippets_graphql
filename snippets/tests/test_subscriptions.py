from graphene_django.utils.testing import GraphQLTestCase
from django.core.asgi import get_asgi_application
import channels_graphql_ws
import channels_graphql_ws.testing

import json
import uuid
import channels
import django
import graphene

from django.conf import settings

from snippets.mutations import Mutation
from snippets.subscriptions import Subscription

import asyncio

"""
Run subscription unit tests through unittest.

These unit tests were originally written in pytest and were derived from
the DjangoChannelsGraphqlWs package.

"""


# ./runtests.sh test_subscriptions
class SnippetsTestCase(GraphQLTestCase):
    # Do this in setUpClass()
    # fixtures = ['fixtures.json', ]

    # setUpClass must be a class method!
    # This is run before all tests in the given class.
    @classmethod
    def setUpClass(cls):

        # The test runner normally sets DEBUG to False.
        # This can be set using the --debug-mode flag on manage.py.
        # It can also be set here; which overrides the test runner --debug-mode flag.
        # settings.DEBUG = True

        # Load fixture data here instead of allowing Django to do it;
        # otherwise, you will get a message:
        # 'database table is locked: snippets_snippet'
        from django.core.management import call_command
        call_command('loaddata', 'fixtures.json')

        # Then call the super to load the fixture data (the old way) and
        # set up the tearDown class.
        super(SnippetsTestCase, cls).setUpClass()

        print()
        print("----> START unittest output below <----")
        print()

    # Run before each test
    def setUp(self):
        print()
        print()

    # ./runtests.sh test_subscriptions test_snippet_create_subscription
    async def test_snippet_create_subscription(self):
        """
A basic unit test to ensure the creation of a subscription.
        """
        print("Establish WebSocket GraphQL connections with subscription confirmation.")

        # print(event_loop)
        # Can't do this or the update will falter
        # event_loop.set_debug(True

        # Get the client from the generator backend
        mygql = next(gql(django.db))
        client = mygql(
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
        if settings.DEBUG:
            print(json.dumps(resp, indent=4))
        assert resp["data"]["updateSnippet"]["ok"] is True

        # Wait for a "complete" message too.
        # This is more of an internal thing. Don't expect a groovy response.
        await client.receive(assert_id=mut_op_id, assert_type="complete", raw_response=False)

        print("Check that subscription notification received.")

        resp = await client.receive(assert_id=sub_op_id, assert_type="data", raw_response=False)
        if settings.DEBUG:
            print(json.dumps(resp, indent=4))
        assert resp["data"]["onSnippetNoGroup"]["ok"] is True

        await client.assert_no_messages(
            "Unexpected message received at the end of the test!"
        )

        await client.finalize()

    # ./runtests.sh test_subscriptions test_snippet_create_subscription_alternate
    #
    # Here's another way to write the create subscription unit test via this article:
    # https://jacobbridges.github.io/post/unit-testing-with-asyncio/
    #
    # - I like that the async designation isn’t on the test definition itself but under an internal function.
    # - There is a logic to this, but it adds a bit more code to access the event_loop, which doesn’t enhance
    # readability.
    # - This guy shows, yet again, that pytest has the cleanest construction overall for async tests.
    def test_snippet_create_subscription_alternate(self):
        print("Establish WebSocket GraphQL connections with subscription confirmation.")

        # print(event_loop)
        # Can't do this or the update will falter
        # event_loop.set_debug(True

        # Get the client from the generator backend
        mygql = next(gql(django.db))
        client = mygql(
            mutation=Mutation,
            subscription=Subscription,
            consumer_attrs={"strict_ordering": True, "confirm_subscriptions": True},
        )

        event_loop = asyncio.get_event_loop()

        async def run_test():
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
            if settings.DEBUG:
                print(json.dumps(resp, indent=4))
            assert resp["data"]["updateSnippet"]["ok"] is True

            # Wait for a "complete" message too.
            # This is more of an internal thing. Don't expect a groovy response.
            await client.receive(assert_id=mut_op_id, assert_type="complete", raw_response=False)

            print("Check that subscription notification received.")

            resp = await client.receive(assert_id=sub_op_id, assert_type="data", raw_response=False)
            if settings.DEBUG:
                print(json.dumps(resp, indent=4))
            assert resp["data"]["onSnippetNoGroup"]["ok"] is True

            await client.assert_no_messages(
                "Unexpected message received at the end of the test!"
            )

            await client.finalize()

        # Run the async test
        event_loop.run_until_complete(run_test())
        event_loop.close()

    # ./runtests.sh test_subscriptions test_confirmation_disabled
    async def test_confirmation_disabled(self):
        print("Establish WebSocket GraphQL connections w/o a subscription confirmation.")

        # Get the client from the generator backend
        mygql = next(gql(django.db))
        client = mygql(
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
        if settings.DEBUG:
            print(json.dumps(resp, indent=4))
        assert resp["data"]["updateSnippet"]["ok"] is True

        # Wait for a "complete" message too.
        # This is more of an internal thing. Don't expect a groovy response.
        await client.receive(assert_id=mut_op_id, assert_type="complete", raw_response=False)

        print("Check that subscription notification received.")

        resp = await client.receive(assert_id=sub_op_id, assert_type="data", raw_response=False)
        if settings.DEBUG:
            print(json.dumps(resp, indent=4))
        assert resp["data"]["onSnippetNoGroup"]["ok"] is True

        await client.assert_no_messages(
            "Unexpected message received at the end of the test!"
        )

        await client.finalize()

    # ./runtests.sh test_subscriptions test_custom_confirmation_message
    async def test_custom_confirmation_message(self):
        print("Establish WebSocket GraphQL connections with a custom confirmation message.")

        expected_data = uuid.uuid4().hex
        expected_error = RuntimeError(uuid.uuid4().hex)
        if settings.DEBUG:
            print("expected_data [{}] expected_error [{}]".format(expected_data, expected_error))

        # Get the client from the generator backend
        mygql = next(gql(django.db))
        client = mygql(
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
        if settings.DEBUG:
            print(json.dumps(resp, indent=4))
        assert resp["data"]["updateSnippet"]["ok"] is True

        # Wait for a "complete" message too.
        # This is more of an internal thing. Don't expect a groovy response.
        await client.receive(assert_id=mut_op_id, assert_type="complete", raw_response=False)

        print("Check that subscription notification received.")

        resp = await client.receive(assert_id=sub_op_id, assert_type="data", raw_response=False)
        if settings.DEBUG:
            print(json.dumps(resp, indent=4))
        assert resp["data"]["onSnippetNoGroup"]["ok"] is True

        await client.assert_no_messages(
            "Unexpected message received at the end of the test!"
        )

        await client.finalize()


# gql originally came from conftest.py, a pytest thing, which contains
# auxiliary files for use in testing. gql is a generator (because of the
# yield), which necessitates the use of next() in the tests.
#
# I wanted to get rid of the pytest dependence as much as possible.
#
# db = Pytest fixture - Require a django test database.
# request = https://docs.pytest.org/en/6.2.x/reference.html#std-fixture-request
def gql(db):
    """
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
    #
    # ANTHONY NOTE: This line doesn't actually do anything; i.e. the
    # tests still pass without it.
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
        ), f"Test has left connected client: !"
