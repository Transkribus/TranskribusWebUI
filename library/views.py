
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import RegisterForm
from .forms import IngestMetsUrlForm
 
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
    return render(request, 'libraryapp/collection.html', {'collId': collId, 'documents': documents,'documents_json': json.dumps(documents)} )

@t_login_required
def document(request, collId, docId, page=None):
    full_doc = services.t_document(collId, docId)
    return render(request, 'libraryapp/document.html', {
		'metadata': full_doc.get('md'), 
		'pageList': full_doc.get('pageList'),
		'collId': collId} )

@t_login_required
def page(request, collId, docId, page):
    full_doc = services.t_document(collId, docId)
    # big wodge of data from full doc includes data for each page and for each page, each transcript...
    index = int(page)-1
    pagedata = full_doc.get('pageList').get('pages')[index]
    transcripts = pagedata.get('tsList').get('transcripts')
    # the way xmltodict parses multiple instances of tags means that if there is one <transcripts> we get a dict, 
    # if there is > 1 we get a list. Solution, but dict in list if dict (or get json from transkribus which is
    # parsed better, but not yet available)
    if isinstance(transcripts, dict):
	transcripts = [transcripts]
#    sys.stdout.write("Document metadata for doc #%s%%: %s%%   \r\n" % (len) )
#    sys.stdout.flush()

    return render(request, 'libraryapp/page.html', {
		'pagedata': pagedata,
		'transcripts': transcripts})

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

@t_login_required
def ingest_mets_url(request):
    if request.method == 'POST':
        # What should be checked here and what can be left up to Transkribus?
        #if ingest_mets_url_form.is_valid():
        services.t_ingest_mets_url(request.POST.get('collection_choice'), request.POST.get('url'))  
        #ingest_mets_url_form.cleaned_data['url'])
        return HttpResponseRedirect('/thanks/')
    else:
        data = {'url': request.GET.get('metsURL', '')}
        ingest_mets_url_form = IngestMetsUrlForm(initial=data, collections = request.session.get("collections"))
        return render(request, 'libraryapp/ingest_mets_url.html', {'ingest_mets_url_form': ingest_mets_url_form} )

