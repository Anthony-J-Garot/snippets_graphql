from django.urls import path

from . import views

app_name = 'snippets'

# These are standard routes using non-GraphQL.
# These routes start at <domainname>/snippets/*.
urlpatterns = [
    # These do not require authentication
    path('', views.SnippetListView.as_view(title='Public Snippets'), name='public_list'),
    path('all/', views.SnippetListView.as_view(title='All Snippets'), name='all_list'),
    path('subscription/', views.SnippetSubscriptionView.as_view(), name='subscription_all'),

    # These require authentication
    path('private/', views.SnippetAuthenticatedListView.as_view(title='Private Snippets'), name='private_list'),
    path('owner/', views.SnippetAuthenticatedListView.as_view(title='Owner Snippets'), name='owner_list'),
    path('<int:pk>/', views.SnippetDetailView.as_view(), name='detail'),

    # Form
    path('create/', views.create, name='create'),
]
