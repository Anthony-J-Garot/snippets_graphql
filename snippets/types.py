import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth import get_user_model
from .models import Snippet  # From this tutorial

# Define a type to bridge to graphene
class SnippetType(DjangoObjectType):
    class Meta:
        model = Snippet
        # I can limit the fields in a GraphQL query
        # https://docs.graphene-python.org/projects/django/en/latest/authorization/
        fields = "__all__"

    # Control filtering at the ObjectType level
    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_anonymous:
            return queryset.filter(private=True)

    # Can define additional fields at this level
    additional_magic = graphene.String()

    def resolve_additional_magic(self, info):
        return "Magic"

    body_preview = graphene.String()

    def resolve_body_preview(self, info):
        return self.body_preview


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
