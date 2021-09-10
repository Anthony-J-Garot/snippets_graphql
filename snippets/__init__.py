from django.conf import settings


def whoami(info):
    """
Determines who the user is based upon the passed header token.
If there is no HTTP_AUTHORIZATION header, default to back end user value.
    """

    query = '''
mutation mutVerifyJWT($token: String!) {
  verifyToken(token: $token) {
    payload
  }
}
'''

    # default value from the back end; could be AnonymousUser
    username = info.context.user

    # The token comes in through the headers prefaced with JWT
    if 'HTTP_AUTHORIZATION' in info.context.META:
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
                print(f"whoami(): Username from mutVerifyJWT [{username}]")
                print(f"whoami(): Username from info.context.user [{info.context.user}]")
                print("")

    return username