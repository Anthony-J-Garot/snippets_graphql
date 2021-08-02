import graphene
from .models import Snippet  # From this tutorial
from .types import SnippetType  # From this tutorial

from django.conf import settings


# https://docs.graphene-python.org/projects/django/en/latest/queries/
class Query(graphene.ObjectType):
    all_snippets = graphene.List(SnippetType)

    # No filter; returns everything
    def resolve_all_snippets(self, info, **kwargs):
        # print(vars(Snippet))
        return Snippet.objects.all()

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
            print("You are currently user [{}]".format(info.context.user))

        if not info.context.user.is_authenticated:
            # AnonymousUser doesn't own squat
            print("You are not authenticated so you own no records")
            return Snippet.objects.none()
        else:
            # Authenticated users get set of the records they own
            return Snippet.objects.filter(owner=info.context.user)

    def resolve_snippets_by_private(self, info):
        """Resolver for filtering records by private flag"""

        if settings.DEBUG:
            print("You are currently user [{}]".format(info.context.user))

        if not info.context.user.is_authenticated:
            # AnonymousUser gets limited set
            return Snippet.objects.filter(private=False)
        else:
            # Authenticated users get choice set
            return Snippet.objects.filter(private=True)

    # ---

    extra_field = graphene.String()

    def resolve_extra_field(self, info):
        return "hello!"
