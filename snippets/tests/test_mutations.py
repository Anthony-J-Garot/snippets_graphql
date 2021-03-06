from graphene_django.utils.testing import GraphQLTestCase  # This has some documentation embedded
import json
from django.conf import settings
from . import authenticate_jwt, login_tokenless


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
    # ./runtests.sh test_mutations test_model_form_authenticated_user_create_mutation
    def test_model_form_authenticated_user_create_mutation(self):

        # First we need a non-Anonymous user. Login using JWT authToken.
        authentication_payload = {
            "username": "john.smith",
            "password": "withscores4!"
        }

        token = authenticate_jwt(self, authentication_payload)
        print(f"User [{authentication_payload['username']}] authenticated with token [{token}]")

        # NOTE! The owner passed-in is AnonymousUser. After creation, the owner
        # should be john.smith.
        snippet_payload = {
            "title": "This is a new snippet",
            "body": "Homer simpsons was here",
            "private": True,
            "owner": "AnonymousUser"
        }

        # Here I request back only those items specified in the snippet_payload
        # for the ease of the unit test.
        response = self.query(
            '''
mutation mutFormCreateSnippet($input: FormCreateSnippetMutationInput!) {
  createFormSnippet(input: $input) {
    snippet {
      title
      body
      private
      owner
    }
    ok
  }
}
            ''',
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
            snippet_payload['owner'],
            content['data']['createFormSnippet']['snippet']['owner'],
            "The owner should not be AnonymousUser for this test"
        )

    # ./runtests.sh test_mutations test_login_mutation
    def test_login_mutation(self):

        # First test with valid user credentials
        payload = {
            "input": {
                "username": "john.smith",
                "password": "withscores4!"
            }
        }

        is_valid = login_tokenless(self, payload)
        self.assertTrue(is_valid, "User [{}] did not authenticate".format(payload['input']['username']))

        # See what happens with invalid credentials
        payload = {
            "input": {
                "username": "john.smith",
                "password": "BAD PASSWD!"
            }
        }

        is_valid = login_tokenless(self, payload)

        # Ensure BAD
        self.assertFalse(
            is_valid,
            "Authentication should NOT have occurred for username [{}]".format(payload['input']['username'])
        )

    # ./runtests.sh test_mutations test_logout_mutation
    def test_logout_mutation(self):

        # First test with valid user credentials
        payload = {
            "input": {
                "username": "john.smith",
                "password": "withscores4!"
            }
        }

        is_valid = login_tokenless(self, payload)
        self.assertTrue(is_valid, "User [{}] did not authenticate".format(payload['input']['username']))

        # Now logout the user
        response = self.query(
            '''
mutation mutLogout {
  logout {
    ok
  }
}
            ''',
            op_name='mutLogout',
            variables={}
        )

        content = json.loads(response.content)
        if settings.DEBUG:
            print(json.dumps(content, indent=4))

        # This validates the status code and if there are errors
        self.assertResponseNoErrors(response)

        is_valid = content['data']['logout']['ok']
        print(f"is_valid [{is_valid}]")

        self.assertTrue(
            is_valid,
            "Username [{}] should have been logged out".format(payload['input']['username'])
        )

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
