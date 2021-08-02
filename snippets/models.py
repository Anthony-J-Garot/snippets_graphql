from django.db import models


# Define a single Django model for use in the tutorial.
class Snippet(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)  # Primary Key
    title = models.CharField(max_length=100)
    body = models.TextField()
    owner = models.TextField(max_length=20, default='admin')
    private = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    # Handy display of title from the object itself
    def __str__(self):
        return self.title

    @property
    def body_preview(self):
        return self.body[:50]
