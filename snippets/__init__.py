from django.conf import settings
from django.contrib.auth import get_user_model


def whoami(info):
    """
Determines who the user is based upon the passed header token.
If there is no HTTP_AUTHORIZATION header, default to back end user value.
    """

    # Note the import within the function else bad things happen:
    #       raise AppRegistryNotReady("Apps aren't loaded yet.")
    from django.contrib.auth.models import User

    VERIFY_JWT_QUERY = '''
mutation mutVerifyJWT($token: String!) {
  verifyToken(token: $token) {
    payload
  }
}
'''

    # Assume Noop user (unauthenticated user in Users table) until proven authenticated.
    # See README.md note for why this is the case.
    user = get_user_model().objects.get(pk=3)

    # An authenticated user must have a JWT Token.
    # No token = no way José!
    # The token comes in through the headers prefaced with 'JWT'.
    if 'HTTP_AUTHORIZATION' in info.context.META:
        # Get a copy for convenience
        auth_string = info.context.META['HTTP_AUTHORIZATION']

        if auth_string.startswith('JWT '):
            # It's a JSON Web Token
            print(f"Splitting auth_string [{auth_string}]")
            jwt, token = auth_string.split(' ')

            # Pass the token back to get the authenticated username.
            from mysite import schema
            result = schema.schema.execute(
                VERIFY_JWT_QUERY,
                context=info.context,
                variables={"token": token}
            )

            if result.data['verifyToken'] is not None:
                payload = result.data['verifyToken']['payload']
                user_id = payload['user_id']

                # Get the actual User record
                user = get_user_model().objects.get(pk=payload['user_id'])
                if settings.DEBUG:
                    print(f"whoami(): User from mutVerifyJWT [{user_id}][{payload['username']}]")
                    print("")

    return user
