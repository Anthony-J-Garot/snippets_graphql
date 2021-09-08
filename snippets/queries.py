import graphene

from django.db.models import Q
from django.conf import settings
from django.contrib.auth import get_user_model

from . import whoami
from .models import Snippet
from .types import SnippetType, UserType


# https://docs.graphene-python.org/projects/django/en/latest/queries/
class Query(graphene.ObjectType):
    all_snippets = graphene.List(SnippetType)

    def resolve_all_snippets(self, info, **kwargs):
        """
Resolver to show all snippets, i.e. no filter.
This is OK for an administrator but not for a regular user or AnonymousUser.
But while I am still testing and debugging, I want to be able to see a raw
list regardless of who I am at the moment.
        """
        return Snippet.objects.all()

    # ---

    limited_snippets = graphene.List(SnippetType)

    def resolve_limited_snippets(self, info, **kwargs):
        """
Resolver to show snippets that the specified user can see.
Rules:
1. All users (including Anonymous) can see Public snippets.
2. All users can see their own snippets regardless of Public/Private.
        """

        # See who I am based upon the web token
        jwt_username = str(whoami(info))
        username = str(info.context.user)
        if jwt_username != username:
            # Different usernames? Shouldn't be.
            print(f"LIMITED: whoami [{jwt_username}] != [{username}]")
            return Snippet.objects.filter(private=False)
        elif jwt_username == 'AnonymousUser':
            # Same, but anonymous
            print(f"LIMITED: Confirmed to be AnonymousUser")
            return Snippet.objects.filter(private=False)

        if settings.DEBUG:
            print(f"LIMITED: Authenticated and acknowledged to be [{username}]")

        if info.context.user.is_authenticated:
            # It's good to be the king
            if info.context.user.is_superuser:
                print("Super user sees all")
                return Snippet.objects.all()

            # Otherwise, the user gets to see Public and their own records
            return Snippet.objects.filter(Q(private=False) | Q(owner=username))
        else:
            print("AnonymousUser sees less")
            return Snippet.objects.filter(private=False)

    # ---

    # I think this needs to be a String because Django models dictate so.
    snippet_by_id = graphene.Field(SnippetType, id=graphene.String())

    def resolve_snippet_by_id(self, info, id):
        """Resolver to get a record by a particular ID"""
        return Snippet.objects.get(pk=id)

    # ---
    snippets_by_owner = graphene.List(SnippetType)

    def resolve_snippets_by_owner(self, info):
        """Resolver for filtering records by the owner of those records"""

        if settings.DEBUG:
            print("OWNER: You are currently user [{}]".format(info.context.user))

        if not info.context.user.is_authenticated:
            # AnonymousUser doesn't own squat
            print("You are not authenticated so you own no records")
            return Snippet.objects.none()
        else:
            # Authenticated users get set of the records they own
            return Snippet.objects.filter(owner=info.context.user)

    def resolve_snippets_by_private(self, info):
        """
Resolver for filtering records by private flag
        """

        if settings.DEBUG:
            print("PRIVATE: You are currently user [{}]".format(info.context.user))

        if info.context.user.is_authenticated:
            if info.context.user.is_superuser:
                print("Super user sees all")
                return Snippet.objects.filter(private=True)
            else:
                # Authenticated users sees their own
                return Snippet.objects.filter(private=True, owner=info.context.user)
        else:
            # AnonymousUser gets nothing
            return Snippet.objects.none()

    # ---

    # These go with JWT
    # https: // www.howtographql.com / graphql - python / 4 - authentication /
    me = graphene.Field(UserType)
    users = graphene.List(UserType)

    def resolve_users(self, info):
        """
Returns all Django users.
        """
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')

        return get_user_model().objects.all()

    def resolve_me(self, info):
        """
Returns all Django user information if s/he is logged in.
        """
        user = info.context.user

        # Because this system allows for an AnonymousUser, just mention
        # the user is not logged in. Do not raise an exception.
        if user.is_anonymous:
            print('Not logged in!')
            return None
            # raise Exception('Not logged in!')

        return user
