from django.shortcuts import render

from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import RegisterForm
 
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .decorators import t_login_required

import services
import json
import sys


#import urllib2
#import xmltodict
#from django.apps import apps

def register(request):
#TODO this is generic guff need to extend form for extra fields, send reg data to transkribus and authticate (which will handle the user creation)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # user = User.objects.create_user(form.cleaned_data['username'],password=form.cleaned_data['password'],email=form.cleaned_data['email'],first_name=form.cleaned_data['given_name'],last_name=form.cleaned_data['family_name'])
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
#TODO	    services.t_register(form)
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'register_form': form} )

def index(request):
    return render(request, 'libraryapp/homepage.html')

@t_login_required
def collections(request):
    collections = request.session.get("collections");
    return render(request, 'libraryapp/collections.html', {'collections': collections} )

@t_login_required
def collection(request, collId):
    documents = services.t_collection(collId)
    return render(request, 'libraryapp/collection.html', {'documents': documents,'documents_json': json.dumps(documents)} )

@t_login_required
def document(request, collId, docId):
    pages = services.t_document(collId, docId)
    return render(request, 'libraryapp/document.html', {'pages': pages} )

@t_login_required
def page(request):
    return render(request, 'libraryapp/page.html')

@t_login_required
def search(request):
    return render(request, 'libraryapp/search.html')

def about(request):
    return render(request, 'libraryapp/about.html')

def user_guide(request):
    return render(request, 'libraryapp/user_guide.html')

@t_login_required
def profile(request):
    collections = request.session.get("collections");
    return render(request, 'libraryapp/profile.html', {'collections': collections})



