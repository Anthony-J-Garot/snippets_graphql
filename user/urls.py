from django.urls import re_path
from . import views

app_name = 'user'

urlpatterns = [
    # Home
    re_path(r'^$', views.sign_in, name='sign_in'),

    # Reverse keys off the name
    re_path(r'signin/$', views.sign_in, name='sign_in'),
    re_path(r'signout/$', views.sign_out, name='sign_out'),
    re_path(r'register/$', views.register, name='register'),
]
