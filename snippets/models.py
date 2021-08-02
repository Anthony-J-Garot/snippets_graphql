from django.db import models


# Define a single Django model for use in the tutorial.
class Snippet(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)  # Primary Key
    title = models.CharField(max_length=100, help_text='Title of article, blog entry, etc.')
    body = models.TextField()
    owner = models.CharField(max_length=20, help_text='Owner of snippet. Generally the author.')
    private = models.BooleanField(default=True,
                                  help_text='Private requires authenticated user (any) to see. If this is False, anyone can see it.')
    created = models.DateTimeField(auto_now_add=True)

    # Handy display of title from the object itself
    def __str__(self):
        return self.title

    @property
    def body_preview(self):
        return self.body[:50]
