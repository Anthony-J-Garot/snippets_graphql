from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


# Define a single Django model for use in the tutorial.
class Snippet(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)  # Primary Key
    title = models.CharField(max_length=100, help_text='Title of article, blog entry, etc.')
    body = models.TextField()
    # https://stackoverflow.com/questions/38748023/django-how-to-foreignkeyauth-user
    # owner = models.CharField(max_length=20, help_text='Owner of snippet. Generally the author.')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        help_text='Owner of snippet. Generally the author.',
        on_delete=models.SET_NULL
    )
    private = models.BooleanField(
        default=True,
        help_text='Private requires authenticated user (any) to see. If this is False, anyone can see it.'
    )
    created = models.DateTimeField(auto_now_add=True)

    # Handy display of title from the object itself
    def __str__(self):
        return self.title

    @property
    def body_preview(self):
        return self.body[:50]

    @property
    def owner(self):
        """
Returns the string version of user, which is the username, and what I wanted.
        """
        return self.user


# Taking token onto the AUTH_USER_MODEL.
class CustomUser(AbstractUser):
    # I think these are 259 bytes, so pad a little just in case
    token = models.CharField(null=True, max_length=270)
