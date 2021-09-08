# This is the application level schema.py

import graphene
from snippets.queries import Query as snippets_query
from snippets.mutations import Mutation as snippets_mutation
from snippets.subscriptions import Subscription as snippets_subscription


# Already set all parms in app, so just pass.
# You can put any number of Query definitions within the parens.
class Query(snippets_query):
    pass


class Mutation(snippets_mutation):
    pass


class Subscription(snippets_subscription):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
