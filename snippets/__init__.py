"""
I was thinking it would be nice to capture GraphQL used in the App here.
I may decide to put them into a separate file, or keep separate from unit tests.
"""


VERIFY_JWT_TOKEN_MUTATION = '''
mutation mutVerifyJWT($token: String!) {
  verifyToken(token: $token) {
    payload
  }
}
'''

