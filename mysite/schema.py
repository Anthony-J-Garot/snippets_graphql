# This is the application level schema.py

import graphene
from datetime import datetime
from mysite.settings import GRAPHQL_JWT

from snippets.queries import Query as snippets_query
from snippets.mutations import Mutation as snippets_mutation
from snippets.subscriptions import Subscription as snippets_subscription


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
    origIat = int((now-datetime(1970,1,1)).total_seconds())
    expiration = now + GRAPHQL_JWT['JWT_EXPIRATION_DELTA']
    exp_seconds = int((expiration-datetime(1970,1,1)).total_seconds())
    print(f"origIat [{origIat}] exp [{exp_seconds}]")

    payload = {
        user.USERNAME_FIELD: username,
        'user_id': user.id,
        'email': user.email,
        'phone': '415-555-1212',
        'exp': exp_seconds,
        'origIat': origIat
    }
    return payload


# Already set all parms in app, so just pass.
# You can put any number of Query definitions within the parens.
class Query(snippets_query):
    pass


class Mutation(snippets_mutation):
    pass


class Subscription(snippets_subscription):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
