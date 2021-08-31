from django.forms import ModelForm, Textarea, TextInput

from .models import Snippet


class SnippetForm(ModelForm):
    class Meta:
        model = Snippet
        # fields = ['title', 'body', 'private', 'owner']

        # I had excluded 'owner' because this is superfluous for the GraphQL
        # mutation; however, it needed to be around for the Django form or
        # the value wouldn't go through.
        exclude = ['created']

        # https://docs.djangoproject.com/en/3.2/ref/forms/widgets/
        widgets = {
            'title': TextInput(attrs={'size': 50}),
            'body': Textarea(attrs={'rows': 5, 'cols': 50}),
        }
