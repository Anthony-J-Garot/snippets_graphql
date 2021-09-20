import binascii
import os

from datetime import datetime
from mysite.settings import GRAPHQL_JWT

# https://github.com/flavors/django-graphql-jwt/blob/main/graphql_jwt/utils.py
from graphql_jwt.utils import get_user_by_payload
from graphql_jwt.utils import jwt_decode as graphql_jwt_decode
# from graphql_jwt.utils import jwt_payload as graphql_jwt_payload
from jwt import MissingRequiredClaimError, InvalidTokenError


class InvalidJwtIdError(InvalidTokenError):
    pass


# https://github.com/waiting-for-dev/devise-jwt#revocation-strategies
# JTI = JWT ID, and it is a standard claim meant to uniquely identify a token.
def generate_jti():
    jti = binascii.hexlify(os.urandom(32)).decode()
    print(f"Generated JTI {jti}")
    return jti


# Custom payload
def jwt_custom_payload_handler(user, context=None):
    """
Custom payload to return additional User settings.
This was because I cannot key off the username directly.
    """
    username = user.get_username()

    #         "origIat": 1631652535
    #         "exp":     1632516535,
    now = datetime.now()
    origIat = int((now - datetime(1970, 1, 1)).total_seconds())
    expiration = now + GRAPHQL_JWT['JWT_EXPIRATION_DELTA']
    exp_seconds = int((expiration - datetime(1970, 1, 1)).total_seconds())
    print(f"origIat [{origIat}] exp [{exp_seconds}] JTI [{user.jti}]")

    payload = {
        user.USERNAME_FIELD: username,
        'user_id': user.id,
        'email': user.email,
        'phone': '415-555-1212',
        'exp': exp_seconds,
        'origIat': origIat,
        'jti': user.jti
    }
    return payload


def jwt_custom_decode_handler(token, context=None):
    print("jwt_custom_decode_handler Entered")

    payload = graphql_jwt_decode(token, context)
    user = get_user_by_payload(payload)
    _validate_jti(payload, user)
    return payload


# Our own validation server side.
# Should just pass through.
def _validate_jti(payload, user):
    if not user.is_authenticated:
        print("_validate_jti(): User not authenticated")
        return
    if user.jti is None:
        print("_validate_jti(): JTI is None")
        return
    if "jti" not in payload:
        print("_validate_jti(): JTI not in payload")
        raise MissingRequiredClaimError("jti")
    if payload["jti"] != user.jti:
        print("_validate_jti(): Invalid JWT id")
        raise InvalidJwtIdError("Invalid JWT id")
