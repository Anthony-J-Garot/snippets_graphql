from django.forms import ModelForm
from .models import Snippet

class SnippetForm(ModelForm):
    class Meta:
        model = Snippet
        fields = "__all__"
