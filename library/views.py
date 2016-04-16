from django.shortcuts import render

from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import RegisterForm

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

#import urllib2
#import xmltodict
#import sys
#from django.apps import apps

def register(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data['username'],password=form.cleaned_data['password'],email=form.cleaned_data['email'],first_name=form.cleaned_data['given_name'],last_name=form.cleaned_data['family_name'])
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'register_form': form} )

def index(request):
    return render(request, 'libraryapp/homepage.html')

@login_required
def collections(request):
    return render(request, 'libraryapp/collections.html')
#not sure about this one
@login_required
def documents(request):
    return render(request, 'libraryapp/documents.html')
#or this one
@login_required
def document(request):
    return render(request, 'libraryapp/document.html')

@login_required
def page(request):
    return render(request, 'libraryapp/page.html')

@login_required
def search(request):
    return render(request, 'libraryapp/search.html')

def about(request):
    return render(request, 'libraryapp/about.html')

def user_guide(request):
    return render(request, 'libraryapp/user_guide.html')

def profile(request):
    return render(request, 'libraryapp/profile.html')

