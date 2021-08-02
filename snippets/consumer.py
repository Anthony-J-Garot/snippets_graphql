import graphene
import channels
import channels_graphql_ws
from snippets.mutations import Mutation
from snippets.subscriptions import Subscription

from django.conf import settings


# ----------------------------------------------------------- GRAPHQL WEBSOCKET CONSUMER

class MyGraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    """
    Channels WebSocket consumer which provides GraphQL API.
    The consumer maintains WebSocket connection with the client.
    """

    # Handle WebSocket connection event
    async def on_connect(self, payload):

        # Use auxiliary Channels function `get_user` to replace an
        # instance of `channels.auth.UserLazyObject` with a native
        # Django user object (user model instance or `AnonymousUser`)
        # It is not necessary, but it helps to keep resolver code
        # simpler. Because in both HTTP/WebSocket requests they can use
        # `info.context.user`, but not a wrapper. For example, objects of
        # type Graphene Django type `DjangoObjectType` does not accept
        # `channels.auth.UserLazyObject` instances.
        # https://github.com/datadvance/DjangoChannelsGraphqlWs/issues/23
        self.scope["user"] = await channels.auth.get_user(self.scope)

        # Which subprotocols are available?
        # For example, soap, wamp, or even json.
        # Subprotocols are additional restrictions and structure.
        subprotocols = self.scope['subprotocols']
        if settings.DEBUG and subprotocols:
            print("Available subprotocols: {}".format(self.scope['subprotocols']))

    schema = graphene.Schema(subscription=Subscription, mutation=Mutation)