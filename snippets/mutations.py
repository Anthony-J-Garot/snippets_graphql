"""
A mutation is a special ObjectType that defines an input.
This mutation file sets up C.UD of CRUD for the snippets model.

https://docs.graphene-python.org/en/latest/types/mutations/
"""

import django
import graphene
import asgiref
from channels.auth import login

from .models import Snippet  # From this tutorial
from .types import SnippetType

from .subscriptions import OnSnippetTransaction  # one group name
from .subscriptions import OnSnippetNoGroup  # no group names


# The input arguments for a Snippets mutation.
# Obviously, ID isn't in there.
# TODO: assess if created should be updateable
class SnippetInput(graphene.InputObjectType):
    title = graphene.String()
    body = graphene.String()
    created = graphene.DateTime()
    private = graphene.Boolean()


# We can use a serializer to use Django CRUD or REST.
# But since I don't have that created . . . .
class CreateSnippetMutation(graphene.Mutation):
    snippet = graphene.Field(lambda: SnippetType)
    ok = graphene.Boolean()

    # You will see the arguments in GraphiQL
    class Arguments:
        # The input arguments for this mutation
        input = SnippetInput(required=True)

    @staticmethod
    def mutate(self, info, input=None):
        # snippet = Snippet(title=title, body=body, private=private)
        snippet = Snippet()
        snippet.title = input['title']
        snippet.body = input['body']
        snippet.private = input['private']
        snippet.save()

        # print(vars(snippet))

        # Notify subscribers.
        OnSnippetTransaction.snippet_event(broadcast_group="CREATE", sender="SENDER", snippet=snippet)
        OnSnippetNoGroup.snippet_event(trans_type="CREATE", sender="SENDER", snippet=snippet)

        # Notice we return an instance of this mutation
        return CreateSnippetMutation(snippet=snippet, ok=True)

class UpdateSnippetMutation(graphene.Mutation):
    # The class attributes define the response of the mutation
    snippet = graphene.Field(lambda: SnippetType)
    ok = graphene.Boolean()

    # You will see the arguments in GraphiQL
    class Arguments:
        id = graphene.ID(required=True)
        input = SnippetInput(required=True)

    @staticmethod
    def mutate(self, info, id, input=None):
        snippet = Snippet.objects.get(pk=id)

        # Loop over all the things
        for key, value in input.items():
            setattr(snippet, key, value)

        snippet.save()

        # Notify subscribers.
        OnSnippetTransaction.snippet_event(broadcast_group="UPDATE", sender="SENDER", snippet=snippet)
        OnSnippetNoGroup.snippet_event(trans_type="UPDATE", sender="SENDER", snippet=snippet)

        # Notice we return an instance of this mutation
        return UpdateSnippetMutation(snippet=snippet, ok=True)


class DeleteSnippetMutation(graphene.Mutation):
    # The class attributes define the response of the mutation
    ok = graphene.Boolean()

    # You will see the arguments in GraphiQL
    class Arguments:
        id = graphene.ID(required=True)

    @staticmethod
    def mutate(self, info, id):
        snippet = Snippet.objects.get(pk=id)
        snippet.delete()

        # Notify subscribers.
        OnSnippetTransaction.snippet_event(broadcast_group="DELETE", sender="SENDER", snippet=None)
        OnSnippetNoGroup.snippet_event(trans_type="DELETE", sender="SENDER", snippet=snippet)

        # Notice we return an instance of this mutation
        return DeleteSnippetMutation(ok=True)


# https://channels.readthedocs.io/en/stable/topics/authentication.html
class Login(graphene.Mutation, name="LoginPayload"):
    """
    Mutation that performs authentication.

    The user information is saved in the info.context and can be used
    to filter queries.
    """
    ok = graphene.Boolean(required=True)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    @staticmethod
    def mutate(self, info, username, password):
        # Ask Django to authenticate user.
        user = django.contrib.auth.authenticate(username=username, password=password)
        if user is None:
            return Login(ok=False)

        # breakpoint()

        # Use Channels to login, in other words to put proper data to
        # the session stored in the scope. The `info.context` is
        # practically just a wrapper around Channel `self.scope`, but
        # the `login` method requires dict, so use `_asdict`.
        # asgiref.sync.async_to_sync(login)(info.context._asdict(), user)
        asgiref.sync.async_to_sync(login)(info.context.__dict__, user)

        # Save the session because `channels.auth.login` does not do this.
        info.context.session.save()

        return Login(ok=True)


class Mutation(graphene.ObjectType):
    update_snippet = UpdateSnippetMutation.Field()
    create_snippet = CreateSnippetMutation.Field()
    delete_snippet = DeleteSnippetMutation.Field()
    login = Login.Field()
