from django.contrib import admin
from django.urls import path, include, re_path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from .schema import schema

from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

from graphql.backend import GraphQLCoreBackend


# Define a CustomCoreBackend to get around the following message:
# "Subscriptions are not allowed. You will need to either use the subscribe 
# function or pass allow_subscriptions=True"
# https://github.com/eamigo86/graphene-django-subscriptions/issues/7
class GraphQLCustomCoreBackend(GraphQLCoreBackend):
    def __init__(self, executor=None):
        # type: (Optional[Any]) -> None
        super().__init__(executor)
        self.execute_params['allow_subscriptions'] = True


urlpatterns = [
    # This example didn't have a root file, so just go to the playground.
    #re_path('^$', RedirectView.as_view(url='/graphql/')),
    re_path('^$', RedirectView.as_view(url='/snippets/')),

    # The App's routes. These are Django views and such.
    path('snippets/', include('snippets.urls', namespace='snippets')),

    # User pages, i.e. login, logout, etc.
    path('user/', include('user.urls', namespace='user')),

    # This is the route for built-in Django administration pages
    path('admin/', admin.site.urls),

    # This pest
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('images/favicon.ico'))),

    # This is the graphQL route. It might be used by the front-end to request data
    # from the API. It is NOT, however, used for subscriptions. That's handled
    # through WebSockets.
    #
    # See curltest.sh for additional details about csrf_exempt().
    # Can turn off access to graphiql by setting to False, which basicall makes this
    # just a dumb endpoint -- I think.
    path('graphql/', csrf_exempt(GraphQLView.as_view(
        graphiql=True, 
        schema=schema, 
        backend=GraphQLCustomCoreBackend()
    ))),
]
