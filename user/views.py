from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm


def index(request):
    return render(request, 'user/index.html')


# The underscore is to make it unique
def sign_in(request):
    form = AuthenticationForm()

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Log the person in
            login(request, form.get_user())

            # Note the colon, which designates namespace
            target_url = redirect(reverse('snippets:owner_list'))
            print("target_url is [{}]".format(target_url))
            return target_url
        else:
            print(form.errors)

    return render(request, 'user/signin.html', {
        'form': form
    })


# The underscore is to make it unique
def sign_out(request):
    logout(request)
    return redirect(reverse('user:sign_in'))


def register(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('user:sign_in'))
        else:
            print(form.errors)

    return render(request, 'user/register.html', {'form': form})
