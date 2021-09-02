import json
from django.conf import settings

"""
IPython is pretty powerful, and this gives a way to invoke the IPython shell from
a specific spot in the code.

To use this:
   from . import IPshell                    # In the test_nnnn.py file
   IPshell('Type %whos to see stuff')       # From somewhere in the code

After digging around a bit, I prefer to use breakpoint() to invoke puDB,
then press ! to invoke IPython.

So none of this is really necessary, but I will leave around for now in case I
find a use for it.
"""

from IPython.terminal.embed import InteractiveShellEmbed

IPshell = InteractiveShellEmbed(
    banner1=
    '''
    Use %kill_embedded to deactivate this embedded instance from firing again this session.
    Try %whos to get the lay of the land.
    '''
)

IPshell.dummy_mode = False  # Turn off all IPshell calls


# Separated this out for re-use
def authenticate_jwt(cls, payload):
    """
Used to authenticate a particular user.
Input: payload of username & password
Returns: token from mutation.
    """
    response = cls.query(
        '''
mutation mutSignonJWT($username: String!, $password: String!) {
  tokenAuth(username: $username, password: $password) {
    token
    payload
    refreshExpiresIn
  }
}
        ''',
        op_name='mutSignonJWT',
        variables=payload
    )

    content = json.loads(response.content)
    if settings.DEBUG:
        print(json.dumps(content, indent=4))

    # This validates the status code and if you get errors
    cls.assertResponseNoErrors(response)

    # Ensure OK
    cls.assertTrue(
        content['data']['tokenAuth']['payload']['username'],
        "Authentication should have occurred for username [{}]".format(payload['username'])
    )
    cls.assertTrue('token' in content['data']['tokenAuth'], "Token should have been found")

    # The token is what we're after
    return content['data']['tokenAuth']['token']


def authenticate_tokenless(cls, payload):
    """
Uses a mutation to request Django authentication.
Input: payload of username & password. *
Returns: Nunthin'. If the user is not authenticated, the unit test will fail.

* Slightly different from that of payload for JWT.
    """
    response = cls.query(
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
    cls.assertResponseNoErrors(response)

    # Ensure OK
    cls.assertTrue(
        content['data']['login']['ok'],
        "Authentication should have occurred for username [{}]".format(payload['input']['username'])
    )
