# This has some documentation embedded. See
# ~/.local/lib/python3.8/site-packages/graphene_django/utils/testing.py
from graphene_django.utils.testing import GraphQLTestCase
import json
from django.conf import settings

# These two to trap stderr
import sys
from io import StringIO


# I'm probably not going to use IPshell this way.
# See note in __init__.py for details, but I will not likely
# from . import IPshell


# ./runtests.sh test_queries
# Your endpoint is set through the GRAPHQL_URL attribute on GraphQLTestCase.
# The default endpoint is GRAPHQL_URL = “/graphql/”.
class SnippetsTestCase(GraphQLTestCase):
    fixtures = ['fixtures.json', ]

    # setUpClass must be a class method!
    # This is run before all tests in the given class.
    @classmethod
    def setUpClass(cls):
        # The test runner normally sets DEBUG to False.
        # This can be set using the --debug-mode flag on manage.py.
        # It can also be set here; which overrides the test runner --debug-mode flag.
        # settings.DEBUG = True

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

    # ./runtests.sh test_queries test_snippets_query
    def test_snippets_query(self):
        """Test to returns all snippet records"""

        response = self.query(
            '''
query qryAllSnippets {
  allSnippets {
    id
    body
    created
    private
    owner
    __typename
  }
  __typename
}
            ''',
            op_name='qryAllSnippets'
        )

        # Note: the content is returned in bytes, which we can easily convert to
        # a dict containing json.
        content = json.loads(response.content)
        if settings.DEBUG:
            print(json.dumps(content, indent=4))

        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # How many rows returned?
        rowcount = len(content['data']['allSnippets'])
        self.assertEquals(5, rowcount, "Should have found 5 rows")

    # ./runtests.sh test_queries test_snippets_by_id
    def test_snippets_by_id(self):
        """Gets a snippet for a desired ID. Assumes the record exists or dumps a stack trace."""

        desired_id = "1"  # Note that it's a string

        response = self.query(
            '''
query snippetById($id: String!) {
  snippetById(id: $id) {
    id
    title
    body
    private
    owner
    created
    __typename
  }
}
            ''',
            op_name='snippetById',
            variables={"id": desired_id}
        )

        content = json.loads(response.content)
        if settings.DEBUG:
            print(json.dumps(content, indent=4))

        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        id = content['data']['snippetById']['id']
        self.assertEquals(desired_id, id, "Should have gotten id requested")

    # I don't want the whole system to bottom out.
    # ./runtests.sh test_queries test_snippets_query_nonexistent
    def test_snippets_query_nonexistent(self):
        """Test for a non-existent snippet. Pass in an ID that is NOT in the DB."""

        desired_id = "0"  # Note that it's a string

        # Trap stderr because resolve_or_error dumps a messy stack trace
        # when a record doesn't exist. Since I know it doesn't exist,
        # suppress the mess.
        old = sys.stderr
        sys.stderr = StringIO()

        response = self.query(
            '''
query snippetById($id: String!) {
  snippetById(id: $id) {
    id
    title
    body
    private
    owner
    created
    __typename
  }
}
            ''',
            op_name='snippetById',
            variables={"id": desired_id}
        )

        # We're good to go again
        sys.stderr = old

        content = json.loads(response.content)
        if settings.DEBUG:
            print(json.dumps(content, indent=4))

        id = content['data']['snippetById']
        # import pudb;pu.db
        self.assertIsNone(id, "Should have gotten null id")

    # ./runtests.sh test_queries test_snippets_by_owner
    def test_snippets_by_owner(self):
        """Tests that records are returned for an authenticated user name that matches owner field in the DB."""

        # First try the unauthenticated user
        response = self.query(
            '''
query qryByOwner {
  snippetsByOwner {
    id
    body
    private
    owner
    created
    __typename
  }
}
            ''',
            op_name='qryByOwner'
        )

        # Note: the content is returned in bytes, which we can easily convert to
        # a dict containing json.
        content = json.loads(response.content)
        if settings.DEBUG:
            print(json.dumps(content, indent=4))

        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # How many rows returned?
        rowcount = len(content['data']['snippetsByOwner'])
        self.assertEquals(0, rowcount, "Should have found 0 rows")

        # Now authenticate
        payload = {
            "input": {
                "username": "admin",
                "password": "withscores4!"
            }
        }

        response = self.query(
            '''
mutation mutLogin($input: LoginInput!) {
  login(input: $input) {
    ok
  }
}
            ''',
            op_name='mutLogin',
            variables=payload
        )

        content = json.loads(response.content)
        if settings.DEBUG:
            print(json.dumps(content, indent=4))

        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # Ensure OK
        self.assertTrue(
            content['data']['login']['ok'],
            "Authentication should have occurred for username [{}]".format(payload['input']['username'])
        )

        response = self.query(
            '''
query qryByOwner {
  snippetsByOwner {
    id
    body
    private
    owner
    created
    __typename
  }
}
            ''',
            op_name='qryByOwner'
        )

        # Note: the content is returned in bytes, which we can easily convert to
        # a dict containing json.
        content = json.loads(response.content)
        if settings.DEBUG:
            print(json.dumps(content, indent=4))

        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # How many rows returned?
        rowcount = len(content['data']['snippetsByOwner'])
        self.assertEquals(2, rowcount, "User [{}] should own 2 rows".format(payload['input']['username']))
