from django.urls import path

from .consumer import MyGraphqlWsConsumer

websocket_urlpatterns = [

    # No leading slash
    path("graphql/", MyGraphqlWsConsumer.as_asgi())

]
