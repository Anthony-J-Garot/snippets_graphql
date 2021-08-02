from .models import Snippet
from django.views.generic import ListView, DetailView, TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import SnippetForm


# https://docs.djangoproject.com/en/dev/topics/auth/default/#user-objects
# from django.contrib.auth.models import User

class SnippetListView(ListView):
    """
    View a list of snippets.
    """
    model = Snippet
    template_name = 'snippets/snippet_list.html'
    title = 'Default'

    def get_queryset(self):
        if self.title == 'Public Snippets':
            # Anyone can view all the Public
            return Snippet.objects.filter(private=False)
        if self.title == 'All Snippets':
            if self.request.user.is_superuser:
                # SU can see anything
                return Snippet.objects.all()
            elif self.request.user.is_authenticated:
                # Show all public and this owner's records
                return Snippet.objects.filter(Q(private=False) | Q(owner=self.request.user.username))
            else:
                # Not logged in? Can still see Public records
                return Snippet.objects.filter(private=False)


# Note LoginRequiredMixin
class SnippetAuthenticatedListView(LoginRequiredMixin, ListView):
    """
    View a list of snippets for an authenticated user.
    """
    model = Snippet
    template_name = 'snippets/snippet_list.html'
    login_url = '/user/signin/'
    logout_url = '/user/signout/'
    redirect_field_name = 'redirect_to'
    title = 'Owner\'s Snippets'

    def get_queryset(self):
        if self.title == 'Private Snippets':
            if self.request.user.is_superuser:
                return Snippet.objects.filter(private=True)
            else:
                return Snippet.objects.filter(owner=self.request.user.username, private=True)
        if self.title == 'Owner Snippets':
            return Snippet.objects.filter(owner=self.request.user.username)


# Can't require a login because some are visible to public.
class SnippetDetailView(DetailView):
    """
    View a single snippet. Typically you'd click a link to get here.

    Example URL:
    http://192.168.2.99:4000/snippets/1/
    """
    model = Snippet
    template_name = 'snippets/snippet_detail.html'
    title = 'Snippet Detail'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Authenticated, so show it
            return Snippet.objects.filter(pk=self.kwargs['pk'])
        else:
            # Not authenticated, but might be OK to show
            return Snippet.objects.filter(pk=self.kwargs['pk'], private=False)


# This is an example of a class based view based upon a template.
# https://docs.djangoproject.com/en/3.2/topics/class-based-views/
class SnippetSubscriptionView(TemplateView):
    """
    Set up for a real-time subscription watcher.
    """
    template_name = 'snippets/snippet_subscription.html'


def create(request):
    """
Primitive form handling function until I get things sorted.
I might turn this into a class if that's possible for forms.
    """

    if request.method == "POST":

        # VALIDATE POST DATA
        # https://stackoverflow.com/questions/22210046/django-form-what-is-the-best-way-to-modify-posted-data-before-validating
        post = request.POST.copy()  # to make mutable
        post['owner'] = request.user.username

        # Transmogrify into form object
        form = SnippetForm(post)

        if form.is_valid():
            form.save()  # Persist the data

            # The benefit of a redirect is that a reload doesn't insert another row into the DB.
            # To send a notification message, I'd have to do it in the URL queryString.
            # This could do it: https://realpython.com/django-redirects/#passing-parameters-with-redirects
            return render(request, 'snippets/success.html', {'notice': 'Created just fine'})
        else:
            # Errors are typically trapped on the front-end, but just in case
            # something falls through, like a required field that isn't on the
            # form, send something to the log file.
            print(form.errors)
    else:
        form = SnippetForm()

    return render(request, 'snippets/create.html', {'form': form})

