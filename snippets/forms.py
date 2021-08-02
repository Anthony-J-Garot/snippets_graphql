from django.forms import ModelForm, Textarea, TextInput

from .models import Snippet


class SnippetForm(ModelForm):
    class Meta:
        model = Snippet
        fields = "__all__"
        #fields = ['title', 'body', 'private']

        # https://docs.djangoproject.com/en/3.2/ref/forms/widgets/
        widgets = {
            'body': Textarea(attrs={'rows': 5, 'cols': 50}),
            'title': TextInput(attrs={'size': 50})
        }
