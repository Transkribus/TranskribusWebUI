
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import RegisterForm
from .forms import IngestMetsUrlForm
 
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .decorators import t_login_required

import services
import navigation
import json
import sys
import re

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
    collection = services.t_collection(collId)
    if(collection == 403): #no access to requested collection
       sys.stdout.write("403 referrer: %s%% \r\n" % (request.META.get("HTTP_REFERER")) )
       sys.stdout.flush()
       return HttpResponseRedirect('/library/collection_noaccess/'+collId)
#    if(re.match(/\d+/, collection)):

    collections = request.session.get("collections");
    nav = navigation.up_next_prev("collection",collId,collections)

    return render(request, 'libraryapp/collection.html', {
		'collId': collId, 
		'documents': collection,
		'documents_json': json.dumps(collection),
		'up': nav['up'], 
		'next': nav['next'],
		'prev': nav['prev'],
		})

@t_login_required
def document(request, collId, docId, page=None):
    collection = services.t_collection(collId)
    full_doc = services.t_document(collId, docId,-1)
    nav = navigation.up_next_prev("document",docId,collection,[collId])

    return render(request, 'libraryapp/document.html', {
		'metadata': full_doc.get('md'), 
		'pageList': full_doc.get('pageList'),
		'collId': int(collId),
		'up': nav['up'],
		'next': nav['next'],
		'prev': nav['prev'],
		})

@t_login_required
def page(request, collId, docId, page):
    #call t_document with noOfTranscript=-1 which will return no transcript data
    full_doc = services.t_document(collId, docId, -1)
    # big wodge of data from full doc includes data for each page and for each page, each transcript...
    index = int(page)-1
    #extract page data from full_doc (may be better from a  separate page data request)
    pagedata = full_doc.get('pageList').get('pages')[index]
    transcripts = pagedata.get('tsList').get('transcripts')
    # the way xmltodict parses multiple instances of tags means that if there is one <transcripts> we get a dict, 
    # if there is > 1 we get a list. Solution: put dict in list if dict (or get json from transkribus which is
    # parsed better, but not yet available)
    if isinstance(transcripts, dict):
	transcripts = [transcripts]

    nav = navigation.up_next_prev("page",page,full_doc.get("pageList").get("pages"),[collId,docId])

    return render(request, 'libraryapp/page.html', {
		'pagedata': pagedata,
		'transcripts': transcripts,
		'up': nav['up'],
		'next': nav['next'],
		'prev': nav['prev'],
		'collId': collId,
		'docId': docId,
		})

@t_login_required
def transcript(request, collId, docId, page, transcriptId):
    #t_page returns an array of the transcripts for a page
    pagedata = services.t_page(collId, docId, page) 
    nav = navigation.up_next_prev("transcript",transcriptId,pagedata,[collId,docId,page])

    pageXML_url = None;
    for x in pagedata:
	sys.stdout.write("x in pagedata: %s == %s\r\n" % (x.get("tsId"),transcriptId) )
        sys.stdout.flush()
	if int(x.get("tsId")) == int(transcriptId):
	     pageXML_url = x.get("url")
	     break
    if pageXML_url:
	transcript = services.t_transcript(transcriptId,pageXML_url)

    regions=transcript.get("PcGts").get("Page").get("TextRegion");

    if isinstance(regions, dict):
	regions = [regions]

    sys.stdout.write("Transcript MD: %s \r\n" % (transcript) )
    sys.stdout.flush()


    return render(request, 'libraryapp/transcript.html', {
		'transcript' : transcript,
		'regions' : regions,
		'up': nav['up'],
		'next': nav['next'],
		'prev': nav['prev'],
		'collId': collId,
		'docId': docId,
		'pageId': page, #NB actually the number for now
		})

@t_login_required
def region(request, collId, docId, page, transcriptId, regionId):
    # We need to be able to target a transcript (as mentioned elsewhere)
    # here there is no need for anything over than the pageXML really
    # we could get one transcript from ...{page}/curr, but for completeness would 
    # rather use transciptId to target a particular transcript
    pagedata = services.t_page(collId, docId, page) 
    #we are only using the pagedata to get the pageXML for a particular
    pageXML_url = None;
    for x in pagedata:
	if int(x.get("tsId")) == int(transcriptId):
	    pageXML_url = x.get("url")
	    break
 
    if pageXML_url:
	transcript = services.t_transcript(transcriptId,pageXML_url)

    regions=transcript.get("PcGts").get("Page").get("TextRegion");
    if isinstance(regions, dict):
	regions = [regions]

    for x in regions:
	x['key'] = x.get("@id")
	if(unicode(regionId) == unicode(x.get("@id"))):
	    region = x

    nav = navigation.up_next_prev("region",regionId,regions,[collId,docId,page,transcriptId])

#    sys.stdout.write("REGION: %s\r\n" % (region) )
#    sys.stdout.flush()

    lines = region.get("TextLine")
    if isinstance(lines, dict):
        lines = [lines]
    #parse metadata
    for x in lines:
	x['md'] = services.t_metadata(x.get("@custom"))

    return render(request, 'libraryapp/region.html', {
		'region' : region,
		'lines' : lines,
		'up': nav['up'],
		'next': nav['next'],
		'prev': nav['prev'],
		'collId': collId,
		'docId': docId,
		'pageId': page, #NB actually the number for now
		'transcriptId': transcriptId,
		})

@t_login_required
def line(request, collId, docId, page, transcriptId, regionId, lineId):
    # We need to be able to target a transcript (as mentioned elsewhere)
    # here there is no need for anything over than the pageXML really
    # we could get one transcript from ...{page}/curr, but for completeness would 
    # rather use transciptId to target a particular transcript
    pagedata = services.t_page(collId, docId, page) 
    #we are only using the pagedata to get the pageXML for a particular
    pageXML_url = None;
    for x in pagedata:
	if int(x.get("tsId")) == int(transcriptId):
	    pageXML_url = x.get("url")
	    break
 
    if pageXML_url:
	transcript = services.t_transcript(transcriptId,pageXML_url)

    #This now officially bonkers....
    regions=transcript.get("PcGts").get("Page").get("TextRegion");
    if isinstance(regions, dict):
	regions = [regions]

    for x in regions:
	if(unicode(regionId) == unicode(x.get("@id"))):
	    region = x

    lines=region.get("TextLine");

    if isinstance(lines, dict):
	lines = [lines]

    for x in lines:
	x['key'] = x.get("@id")
	if(unicode(lineId) == unicode(x.get("@id"))):
	    line = x

    nav = navigation.up_next_prev("line",lineId,lines,[collId,docId,page,transcriptId,regionId])

#    sys.stdout.write("REGION: %s\r\n" % (region) )
#    sys.stdout.flush()

    words = line.get("Word")
    if isinstance(words, dict):
        words = [words]
    #parse metadata
    for x in words:
	x['md'] = services.t_metadata(x.get("@custom"))

    return render(request, 'libraryapp/line.html', {
		'line' : line,
		'words' : words,
		'up': nav['up'],
		'next': nav['next'],
		'prev': nav['prev'],
		'collId': collId,
		'docId': docId,
		'pageId': page, #NB actually the number for now
		'transcriptId': transcriptId,
		'regionId': regionId,
		'lineId': lineId,
		})

@t_login_required
def word(request, collId, docId, page, transcriptId, regionId, lineId, wordId):
    # booo hiss
    pagedata = services.t_page(collId, docId, page) 
    #we are only using the pagedata to get the pageXML for a particular
    pageXML_url = None;
    for x in pagedata:
	if int(x.get("tsId")) == int(transcriptId):
	    pageXML_url = x.get("url")
	    break
 
    if pageXML_url:
	transcript = services.t_transcript(transcriptId,pageXML_url)

    #This now officially bonkers....
    regions=transcript.get("PcGts").get("Page").get("TextRegion");
    if isinstance(regions, dict):
	regions = [regions]

    for x in regions:
	if(unicode(regionId) == unicode(x.get("@id"))):
	    region = x

    lines=region.get("TextLine");

    if isinstance(lines, dict):
	lines = [lines]

    for x in lines:
	if(unicode(lineId) == unicode(x.get("@id"))):
	    line = x

    words = line.get("Word")
    if isinstance(words, dict):
        words = [words]

    #parse metadata
    for x in words:
	x['key'] = x.get("@id")
	if(unicode(wordId) == unicode(x.get("@id"))):
		x['md'] = services.t_metadata(x.get("@custom"))
		word = x
		
    nav = navigation.up_next_prev("word",wordId,words,[collId,docId,page,transcriptId,regionId,lineId])

    return render(request, 'libraryapp/word.html', {
		'word' : word,
		'up': nav['up'],
		'next': nav['next'],
		'prev': nav['prev'],
		'collId': collId,
		'docId': docId,
		'pageId': page, #NB actually the number for now
		'transcriptId': transcriptId,
		'regionId': regionId,
		'lineId': lineId,
		})


@t_login_required
def search(request):
    return render(request, 'libraryapp/search.html')

def about(request):
    return render(request, 'libraryapp/about.html')

def user_guide(request):
    return render(request, 'libraryapp/user_guide.html')

@t_login_required
def users(request, collId, userId):
    return render(request, 'libraryapp/users.html')

@t_login_required
def profile(request):
    collections = request.session.get("collections");
    return render(request, 'libraryapp/profile.html', {'collections': collections})

#error pages
def collection_noaccess(request, collId):

    if(request.get_full_path() == request.META.get("HTTP_REFERER") or re.match(r'^.*login.*', request.META.get("HTTP_REFERER"))):
        back = None
    else:
        back = request.META.get("HTTP_REFERER") #request.GET.get("back")

    return render(request, 'libraryapp/error.html', {
                'msg' : "I'm afraid you are not allowed to access this collection",
                'back' : back,
            })
    
@t_login_required
def ingest_mets_url(request):
    if request.method == 'POST':
        # What should be checked here and what can be left up to Transkribus?
        #if ingest_mets_url_form.is_valid():
        services.t_ingest_mets_url(request.POST.get('collection'), request.POST.get('url'))  
        return HttpResponseRedirect('/thanks/')
    else:
        data = {'url': request.GET.get('metsURL', '')}
        ingest_mets_url_form = IngestMetsUrlForm(initial=data)
        collections = request.session.get("collections")
        return render(request, 'libraryapp/ingest_mets_url.html', {'ingest_mets_url_form': ingest_mets_url_form, 'collections': collections})

def collections_dropdown(request):
    collections = services.t_collections()
    return render(request, 'libraryapp/collections_dropdown.html', {'collections': collections})

def create_collection_modal(request):
    if (services.t_create_collection(request.POST.get('collection_name'))):
        return HttpResponse("New collection created successfully!", content_type="text/plain")
    #else:
           # TODO Handle failures... 
