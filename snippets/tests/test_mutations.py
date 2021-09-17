import graphql_jwt.exceptions
from graphene_django.utils.testing import GraphQLTestCase  # This has some documentation embedded
import json
from django.conf import settings
from . import authenticate_jwt
from django.contrib.auth.models import User
from snippets import whoami


# ./runtests.sh test_mutations
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

    # This tests the "model form" version of create for an authenticated user.
    #
    # There is another test for the straight mutation based graphene create.
    # Not sure if I find that either is better than the other.
    # ./runtests.sh test_mutations test_snippet_create_model_auth_mutation
    def test_snippet_create_model_auth_mutation(self):

        # First we need a non-Anonymous user. Login using JWT authToken.
        authentication_payload = {
            "username": "john.smith",
            "password": "withscores4!"
        }

        token = authenticate_jwt(self, authentication_payload)
        print(f"TEST: User [{authentication_payload['username']}] authenticated with token [{token}]")

        # NOTE!
        # The owner passed-in is Admin (1) even though after
        # creation the owner should be john.smith (2). Why do I
        # pass in Admin? To prove that the code forces the owner
        # to the logged in (or AnonymousUser) regardless of who
        # is sent.
        snippet_payload = {
            "title": "This is a new snippet",
            "body": "Homer simpsons was here",
            "private": True,
            "user": 1
        }

        # Here I request back only those items specified in the snippet_payload
        # for the ease of the unit test.
        response = self.query(
            CREATE_SNIPPET_MODEL_MUTATION,
            op_name='mutFormCreateSnippet',
            variables={"input": snippet_payload},
            headers={"HTTP_AUTHORIZATION": f"JWT {token}"}
        )

        content = json.loads(response.content)
        if settings.DEBUG:
            print(json.dumps(content, indent=4))

        # This validates the status code and if there are errors
        self.assertResponseNoErrors(response)

        # Ensure OK
        self.assertTrue(
            content['data']['createFormSnippet']['ok'],
            "Record should have been created"
        )

        # Ensure values passed through
        self.assertNotEquals(
            snippet_payload['user'],
            content['data']['createFormSnippet']['snippet']['user'],
            "The owner should not be AnonymousUser for this test"
        )

    # This tests the "model form" version of create for the anonymous user.
    #
    # ./runtests.sh test_mutations test_snippet_create_model_anon_mutation
    def test_snippet_create_model_anon_mutation(self):

        # NOTE! The owner passed-in is Admin (1) even though
        # the resultant record will be owned by AnonymousUser.
        snippet_payload = {
            "title": "I gotta have more cowbell",
            "body": "THE Bruce Dickenson",
            "private": False,
            "user": 1
        }

        # Note the blank authorization header
        response = self.query(
            CREATE_SNIPPET_MODEL_MUTATION,
            op_name='mutFormCreateSnippet',
            variables={"input": snippet_payload},
            headers={"HTTP_AUTHORIZATION": ""}
        )

        content = json.loads(response.content)
        if settings.DEBUG:
            print(json.dumps(content, indent=4))

        # This validates the status code and if there are errors
        self.assertResponseNoErrors(response)

        # Ensure OK
        self.assertTrue(
            content['data']['createFormSnippet']['ok'],
            "Record should have been created"
        )

        # Ensure values passed through
        self.assertIsNone(
            content['data']['createFormSnippet']['snippet']['user'],
            "The owner should be AnonymousUser for this test"
        )

    # ./runtests.sh test_mutations test_logout_mutation
    def test_logout_mutation(self):

        # First test with valid user credentials
        payload = {
            "username": "john.smith",
            "password": "withscores4!"
        }

        token = authenticate_jwt(self, payload)

        # Now logout the user
        # TODO This needs to be handled better at the API level
        # https://github.com/flavors/django-graphql-jwt/issues/11#issuecomment-463148810

    # ./runtests.sh test_mutations test_snippet_create_mutation
    def test_snippet_create_mutation(self):
        payload = {'title': 'food', 'body': 'BODY', 'private': False}

        # Here I request back only those items specified in the payload
        # for the ease of the unit test.
        response = self.query(
            '''
mutation mutCreateSnippet($input: SnippetInput!) {
  createSnippet(input: $input) {
    snippet {
      title
      body
      private
    }
    ok
  }
}
            ''',
            op_name='mutCreateSnippet',
            variables={"input": payload}
        )

        content = json.loads(response.content)
        if settings.DEBUG:
            print(json.dumps(content, indent=4))

        # This validates the status code and if there are errors
        self.assertResponseNoErrors(response)

        # Ensure OK
        self.assertTrue(
            content['data']['createSnippet']['ok'],
            "Record should have been created"
        )

        # Ensure values passed through
        self.assertEquals(
            payload,
            content['data']['createSnippet']['snippet'],
            "Variables should have passed through"
        )

    # For update, let's change row 2's body to lorem ipsum.
    # ./runtests.sh test_mutations test_snippet_update_mutation
    def test_snippet_update_mutation(self):
        # Only set those fields that will change in the payload.
        payload = {
            "body": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "title": "Titles are for books",
            "created": "2012-04-23T18:25:43.511Z",
            "private": False
        }

        # Request several fields back from snippet for testing
        response = self.query(
            '''
mutation updateSnippet($id: ID!, $input: SnippetInput!) {
  updateSnippet(id: $id, input: $input) {
    snippet {
      title
      body
      private
      bodyPreview
    }
    ok
  }
}
            ''',
            op_name='updateSnippet',
            variables={"id": "2", "input": payload}
        )

        content = json.loads(response.content)
        if settings.DEBUG:
            print(json.dumps(content, indent=4))

        # This validates the status code and if there are errors
        self.assertResponseNoErrors(response)

        # Ensure I typed the alphabet correctly
        self.assertEquals(52, len(payload['body']), "Learn the alphabet!")

        # Ensure OK
        self.assertTrue(
            content['data']['updateSnippet']['ok'],
            "Record should have been updated"
        )

        # Ensure values passed through
        self.assertEquals(
            payload['body'],
            content['data']['updateSnippet']['snippet']['body'],
            "Body should have changed"
        )

        # The real litmus is if the body preview has changed
        self.assertEquals(
            payload['body'][:50],
            content['data']['updateSnippet']['snippet']['bodyPreview'],
            "Body Preview should be correct size"
        )

    # For delete, remove row 1 and ensure row 2 is still around.
    # ./runtests.sh test_mutations test_snippet_delete_mutation
    def test_snippet_delete_mutation(self):
        payload = {
            "id": "1"
        }

        # Request ok back
        response = self.query(
            '''
mutation deleteSnippet($id: ID!) {
  deleteSnippet(id: $id) {
    ok
  }
}
            ''',
            op_name='deleteSnippet',
            variables=payload
        )

        content = json.loads(response.content)
        if settings.DEBUG:
            print(json.dumps(content, indent=4))

        # This validates the status code and if there are errors
        self.assertResponseNoErrors(response)

        # Ensure OK
        self.assertTrue(
            content['data']['deleteSnippet']['ok'],
            "Record should have been deleted"
        )

    # ./runtests.sh test_mutations test_verify_token
    def test_verify_token(self):

        payload = {
            "username": "john.smith",
            "password": "withscores4!"
        }

        token = authenticate_jwt(self, payload)

        response = self.query(
            '''
            mutation mutVerifyJWT($token: String!) {
              verifyToken(token: $token) {
                payload
              }
            }
            ''',
            op_name='mutVerifyJWT',
            variables={"token": token}
        )

        content = json.loads(response.content)
        if settings.DEBUG:
            print(json.dumps(content, indent=4))

        # This validates the status code and if there are errors
        self.assertResponseNoErrors(response)

        # Ensure OK
        self.assertEquals(
            payload['username'],
            content['data']['verifyToken']['payload']['username'],
            "User should have been returned"
        )

    # ./runtests.sh test_mutations test_verify_token_expired
    def test_verify_token_expired(self):
        """
Tests that a stale token is properly trapped and handled.
        """

        # This token is good and stale. It expired many moons ago.
        token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImpvaG4uc21pdGgiLCJleHAiOjE2MzA0NDk0NjQsIm9yaWdJYXQiOjE2MzA0NDkxNjR9.8iOC1VuZtnHFeCc2YVxOMa9p77jeSIyF8aqELo6eZCU"

        self.query(
            '''
            mutation mutVerifyJWT($token: String!) {
              verifyToken(token: $token) {
                payload
              }
            }
            ''',
            op_name='mutVerifyJWT',
            variables={"token": token}
        )

        self.assertRaises(graphql_jwt.exceptions.JSONWebTokenExpired)

    # Whoami is a helper function, but it's based upon a mutation, so testing it here
    # ./runtests.sh test_mutations test_whoami
    def test_whoami(self):
        """
Tests that whoami helper function works.
        """

        # This token is good and stale. It expired many moons ago.
        token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImpvaG4uc21pdGgiLCJleHAiOjE2MzA0NDk0NjQsIm9yaWdJYXQiOjE2MzA0NDkxNjR9.8iOC1VuZtnHFeCc2YVxOMa9p77jeSIyF8aqELo6eZCU"

        info = lambda: None
        info.context = lambda: None
        info.context.META = {}
        info.context.META["HTTP_AUTHORIZATION"] = f"JWT {token}"
        info.context.user = User.objects.get(pk=2)

        user = whoami(info)

        self.assertRaises(graphql_jwt.exceptions.JSONWebTokenExpired)


CREATE_SNIPPET_MODEL_MUTATION = '''
mutation mutFormCreateSnippet($input: FormCreateSnippetMutationInput!) {
  createFormSnippet(input: $input) {
    snippet {
      title
      body
      private
      user { id, username, email }
    }
    ok
  }
}
'''
