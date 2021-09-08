from django.conf import settings


def whoami(info):
    """
Determines who the user is based upon the passed header token.
    """

    query = '''
mutation mutVerifyJWT($token: String!) {
  verifyToken(token: $token) {
    payload
  }
}
'''

    # The token comes in through the headers prefaced with JWT
    username = info.context.user  # default value; could be AnonymousUser
    auth_string = info.context.META['HTTP_AUTHORIZATION']
    if auth_string.startswith('JWT '):
        print(f"Splitting auth_string [{auth_string}]")
        jwt, token = auth_string.split(' ')

        # Pass the token back to get the authenticated username.
        # Note the import within the function else bad things happen:
        #       raise AppRegistryNotReady("Apps aren't loaded yet.")
        from mysite import schema
        result = schema.schema.execute(
            query,
            context=info.context,
            variables={"token": token}
        )
        username = result.data['verifyToken']['payload']['username']
        if settings.DEBUG:
            print(f"Username from mutVerifyJWT [{username}]")
            print(f"Username from info.context.user [{info.context.user}]")
            print("")

    return username