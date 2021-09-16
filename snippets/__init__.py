import graphql_jwt.exceptions
from django.conf import settings


def whoami(info):
    """
Determines who the user is based upon the passed header token.
If there is no HTTP_AUTHORIZATION header, default to back end user value.
    """

    VERIFY_JWT_QUERY = '''
mutation mutVerifyJWT($token: String!) {
  verifyToken(token: $token) {
    payload
  }
}
'''

    # default value from the back end; could be AnonymousUser
    user = info.context.user
    user_id = user.id
    username = user.username

    # The token comes in through the headers prefaced with JWT
    if 'HTTP_AUTHORIZATION' in info.context.META:
        auth_string = info.context.META['HTTP_AUTHORIZATION']

        if auth_string.startswith('JWT '):
            # It's a JSON Web Token
            print(f"Splitting auth_string [{auth_string}]")
            jwt, token = auth_string.split(' ')

            # Hold the old values
            user_id_hold = user_id
            username_hold = username

            # Pass the token back to get the authenticated username.
            # Note the import within the function else bad things happen:
            #       raise AppRegistryNotReady("Apps aren't loaded yet.")
            from mysite import schema
            result = schema.schema.execute(
                VERIFY_JWT_QUERY,
                context=info.context,
                variables={"token": token}
            )

            if result.data['verifyToken'] is not None:
                payload = result.data['verifyToken']['payload']
                user_id = payload['user_id']
                from django.contrib.auth.models import User
                user = User.objects.get(pk=payload['user_id'])
                if settings.DEBUG:
                    print(f"whoami(): User from mutVerifyJWT [{user_id}][{payload['username']}]")
                    print(f"whoami(): User from info.context.user [{user_id_hold}][{username_hold}]")
                    print("")

    return user
