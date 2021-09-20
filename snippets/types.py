import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth import get_user_model
from .models import Snippet  # From this tutorial


# Define a type to bridge to graphene.
#
# NOTE 1: Any "extra" columns have to be defined here but populated in the model.
#
# NOTE 2: When you make changes here, or in the Query resolver, you may need to
# restart the server before pulling the schema, again, in either Insomnia or
# GraphiQL playground.
class SnippetType(DjangoObjectType):
    class Meta:
        model = Snippet
        # I can limit the fields in a GraphQL query
        # https://docs.graphene-python.org/projects/django/en/latest/authorization/
        fields = "__all__"

    # Control filtering at the ObjectType level.
    # I don't think I ever used this.
    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_anonymous:
            return queryset.filter(private=True)

    # Can define additional fields at this level
    additional_magic = graphene.String()

    def resolve_additional_magic(self, info):
        return "Magic"

    # A read-only short version of the body
    body_preview = graphene.String()

    def resolve_body_preview(self, info):
        return self.body_preview

    # The owner is the User.username
    owner = graphene.String()

    def resolve_owner(self, info):
        # print(info.context.user)
        return self.owner


class UserType(DjangoObjectType):
    class Meta:
        # This SHOULD get the CustomUser
        model = get_user_model()
