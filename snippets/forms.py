from django.forms import ModelForm, Textarea, TextInput

from .models import Snippet


class SnippetForm(ModelForm):
    class Meta:
        model = Snippet
        # fields = ['title', 'body', 'private']
        exclude = ['owner', 'created']

        # https://docs.djangoproject.com/en/3.2/ref/forms/widgets/
        widgets = {
            'title': TextInput(attrs={'size': 50}),
            'body': Textarea(attrs={'rows': 5, 'cols': 50}),
        }
