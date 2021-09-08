"""
A mutation is a special ObjectType that defines an input.
This mutation file sets up C.UD of CRUD for the snippets model.

https://docs.graphene-python.org/en/latest/types/mutations/
"""

import django
import graphene
import graphql_jwt
import asgiref
from channels.auth import login
from graphene_django.forms.mutation import DjangoModelFormMutation
import copy
from django.conf import settings

from django.contrib.auth import get_user_model

# Project imports
from .models import Snippet
from .types import SnippetType, UserType
from .forms import SnippetForm
from . import whoami

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


# Input arguments for authentication.
class LoginInput(graphene.InputObjectType):
    username = graphene.String()
    password = graphene.String()


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
        snippet.owner = info.context.user.username  # Set by the API only
        snippet.save()

        # print(vars(snippet))

        # Notify subscribers.
        OnSnippetTransaction.snippet_event(broadcast_group="CREATE", sender="SENDER", snippet=snippet)
        OnSnippetNoGroup.snippet_event(trans_type="CREATE", sender="SENDER", snippet=snippet)

        # Notice we return an instance of this mutation
        return CreateSnippetMutation(snippet=snippet, ok=True)


class FormCreateSnippetMutation(DjangoModelFormMutation):
    """
DjangoModelFormMutation will pull the fields from a ModelForm,
which basically means I don't have to specify an Arguments section
like I did in CreateSnippetMutation.

If the form is set up properly, this is, perhaps, a better approach
because of the inherent server-side form validation and ease of
coding the "save" action.
    """
    snippet = graphene.Field(lambda: SnippetType)
    ok = graphene.Boolean()

    class Meta:
        form_class = SnippetForm  # This is my ModelForm
        # input_field_name = 'data'
        # return_field_name = 'my_pet'

    # Per the docs:
    # Override this method to change how the form is saved or to return a different Graphene object type.
    # https://docs.graphene-python.org/projects/django/en/latest/mutations/
    def perform_mutate(form, info, *args):
        """
Runs (perform the mutation) only if the form is valid.
The owner is passed, but it is replaced with the authenticated username.
        """

        username = whoami(info)

        # shorthand to the model instance.
        # PyCharm complains, "Unresolved attribute reference 'instance' for class 'FormCreateSnippetMutation'",
        # but you can see it in pudb.
        # import pudb;pu.db
        snippet = form.instance
        # if settings.DEBUG:
        #     print(f"Snippet (form instance) [{snippet}]")

        # Now enforce our rule that the person logged in is the owner, not the passed
        # value through the form. If no user was logged in, AnonymousUser will pass thru.
        if settings.DEBUG:
            print(f"Passed owner from form was [{form['owner'].data}]")
            print(f"Forcing owner to [{username}]")
        snippet.owner = username  # Set by the API only; this is AnonymousUser when not authenticated

        # Various ways we can see all the things
        # print(vars(form))
        # print(form["private"].data)
        # print(form["body"].data)
        # print(form["owner"].data)
        # And, of course, viewing the Variables in pudb:
        # import pudb;pu.db

        snippet.save()  # Persist the data of this model instance

        # Notify subscribers.
        OnSnippetTransaction.snippet_event(broadcast_group="CREATE", sender="SENDER", snippet=snippet)
        OnSnippetNoGroup.snippet_event(trans_type="CREATE", sender="SENDER", snippet=snippet)

        return FormCreateSnippetMutation(snippet=snippet, ok=True)


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
        snippet_clone = copy.copy(snippet)
        snippet.delete()

        snippet_clone.id = id

        # Notify subscribers.
        OnSnippetTransaction.snippet_event(broadcast_group="DELETE", sender="SENDER", snippet=snippet_clone)
        OnSnippetNoGroup.snippet_event(trans_type="DELETE", sender="SENDER", snippet=snippet_clone)

        # Notice we return an instance of this mutation
        return DeleteSnippetMutation(ok=True)


# https://channels.readthedocs.io/en/stable/topics/authentication.html
class Login(graphene.Mutation, name="LoginPayload"):
    """
    Mutation that performs authenticatin.

    The user information is saved in the info.context and can be used
    to filter queries.
    """
    ok = graphene.Boolean(required=True)

    class Arguments:
        input = LoginInput(required=True)

    @staticmethod
    def mutate(self, info, input):
        # Ask Django to authenticate user.
        user = django.contrib.auth.authenticate(username=input.username, password=input.password)
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


# I can extend the JWT functionality by adding my own resolve.
class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        print(f"*** USER [{info.context.user}] AUTHENTICATED - MY OWN TOKENAUTH ***")
        return cls(user=info.context.user)


class Mutation(graphene.ObjectType):
    # Defined herein
    update_snippet = UpdateSnippetMutation.Field()
    create_snippet = CreateSnippetMutation.Field()
    delete_snippet = DeleteSnippetMutation.Field()

    # This uses Form fields rather than my own defined fields
    create_form_snippet = FormCreateSnippetMutation.Field()

    # This works well for the server side, but it's less useful for a
    # separate React front end because no security information is passed
    login = Login.Field()

    # These come from JWT native
    # https://buildmedia.readthedocs.org/media/pdf/django-graphql-jwt/stable/django-graphql-jwt.pdf
    # token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

    # But I can use my own if I add a class and resolve. (see above)i
    token_auth = ObtainJSONWebToken.Field()
