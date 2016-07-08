from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import RegisterForm, IngestMetsUrlForm, MetsFileForm
 
from django.utils import translation

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.utils.translation import ugettext_lazy as _

from .decorators import t_login_required
#from profiler import profile #profile is a decorator, but things get circular if I include it in decorators.py so...

import settings
import services
import navigation
import json
import sys
import re
import random
from django.template.loader import render_to_string

#import urllib2
#import xmltodict
#from django.apps import apps

def register(request):
#TODO this is generic guff need to extend form for extra fields, send reg data to transkribus and authticate (which will handle the user creation)

    if request.user.is_authenticated(): #shouldn't really happen but...
            return HttpResponseRedirect('/library/')
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
	sys.stdout.write("### IN t_register \r\n" )
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
	    sys.stdout.write("### IN form is valid \r\n" )

            # user = User.objects.create_user(form.cleaned_data['username'],password=form.cleaned_data['password'],email=form.cleaned_data['email'],first_name=form.cleaned_data['given_name'],last_name=form.cleaned_data['family_name'])
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            try: 
            	services.t_register(request)
            	return HttpResponseRedirect('/library/profile')
		#tried out modal here and it is noce (but not really for registration)
#	        messages.info(request, _('Registration requested please check your email.'))
#                return HttpResponse(json.dumps({'RESET': 'true', 'MESSAGE': render_to_string('libraryapp/message_modal.html', request=request)}), content_type='text/plain')
	    except ValueError as err:
		sys.stdout.write("### t_register response ERROR RAISED: %s  \r\n" % (err) )
#		return render(request, 'registration/register.html', {'register_form': form} )
		#Why the f**k won't this redirect?!? TODO fix or try another method
		return HttpResponseRedirect('/library/error')
    
    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegisterForm()

    #Recpatch errors are not properly dislpayed by bootstrap-form... hmph
    return render(request, 'registration/register.html', {'register_form': form} )

def index(request):
    return render(request, 'libraryapp/homepage.html' )


#/library/collections
#view that lists available collections for a user
#@profile("collections.prof")
@t_login_required
def collections(request):
    collections = request.session.get("collections");
    return render(request, 'libraryapp/collections.html', {'collections': collections} )

#/library/collection/{colId}
#view that 
# - lists documents
# - also lists pages for documents
#@profile("collection.prof")
@t_login_required
def collection(request, collId):
    #this is actually a call to collections/{collId}/list and returns only the document objects for a collection
    docs = services.t_collection(request,collId)
    if(docs == 403): #no access to requested collection
       sys.stdout.write("403 referrer: %s%% \r\n" % (request.META.get("HTTP_REFERER")) )
       sys.stdout.flush()
       return HttpResponseRedirect('/library/collection_noaccess/'+collId)

    collections = request.session.get("collections");
    #there is currently no transkribus call for collections/{collId} on its own to fetch just data for collection
    # so we'll loop through collections and pick out collection level metadata freom there 
    # The same could be achieved using the list of documents (ie pick first doc match collId with member of colList)
    collection = None
    for x in collections:
        if unicode(x.get("colId")) == unicode(collId):
	    collection = x
        
    nav = navigation.up_next_prev("collection",collId,collections)

    #collection view goes down two levels (ie documents and then pages)
    # data prepared fro fancytree.js representation
    for doc in docs:
        doc['collId'] = collId
	doc['key'] = doc['docId']
	doc['folder'] = 'true'
	#fetch full document data with no transcripts for pages //TODO avoid REST request in loop?
	fulldoc  = services.t_document(request, collId, doc['docId'], 0)
	doc['children'] = fulldoc.get('pageList').get("pages")
        for x in doc['children']:
	   x['title']=x['imgFileName'] 
	   x['collId']=collId

    return render(request, 'libraryapp/collection.html', {
        'collId': collId, 
        'collection': collection,
        'documents': docs,
        'documents_json': json.dumps(docs),
        'up': nav['up'], 
        'next': nav['next'],
        'prev': nav['prev'],
        })

#/library/document/{colId}/{docId}
# view that lists pages in doc and some doc level metadata
#@profile("document.prof")
@t_login_required
def document(request, collId, docId, page=None):
    collection = services.t_collection(request, collId)
    full_doc = services.t_document(request, collId, docId,-1)
    nav = navigation.up_next_prev("document",docId,collection,[collId])

    return render(request, 'libraryapp/document.html', {
        'metadata': full_doc.get('md'), 
        'pageList': full_doc.get('pageList'),
        'collId': int(collId),
        'up': nav['up'],
        'next': nav['next'],
        'prev': nav['prev'],
        })

#/library/document/{colId}/{docId}/{page}
# view that lists transcripts in doc and some page level metadata
#@profile("page.prof")
@t_login_required
def page(request, collId, docId, page):
    #call t_document with noOfTranscript=-1 which will return no transcript data
    full_doc = services.t_document(request, collId, docId, -1)
    # big wodge of data from full doc includes data for each page and for each page, each transcript...
    index = int(page)-1
    #extract page data from full_doc (may be better from a  separate page data request)
    pagedata = full_doc.get('pageList').get('pages')[index]
    transcripts = pagedata.get('tsList').get('transcripts')

#    sys.stdout.write("############## PAGEDATA: %s\r\n" % ( pagedata ) )

    # the way xmltodict parses multiple instances of tags means that if there is one <transcripts> we get a dict, 
    # if there is > 1 we get a list. Solution: put dict in list if dict (or get json from transkribus which is
    # parsed better, but not yet available)
    if isinstance(transcripts, dict):
        transcripts = [transcripts]

#    sys.stdout.write("############## PAGEDATA.TRANSCRIPTS: %s\r\n" % ( transcripts ) )

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

#/library/transcript/{colId}/{docId}/{page}/{tsId}
# view that lists regions in transcript and some transcript level metadata
@t_login_required
def transcript(request, collId, docId, page, transcriptId):
    #t_page returns an array of the transcripts for a page
    pagedata = services.t_page(request, collId, docId, page) 
    nav = navigation.up_next_prev("transcript",transcriptId,pagedata,[collId,docId,page])

    pageXML_url = None;
    for x in pagedata:
	if int(x.get("tsId")) == int(transcriptId):
	     pageXML_url = x.get("url")
	     break
    sys.stdout.write("PAGEXML URL : %s \r\n" % (pageXML_url) )
    sys.stdout.flush()

    if pageXML_url:
	transcript = services.t_transcript(request,transcriptId,pageXML_url)

    regions=transcript.get("PcGts").get("Page").get("TextRegion");

    if isinstance(regions, dict):
	regions = [regions]

    if regions:
        for x in regions:
            sys.stdout.write("CUSTOM : %s \r\n" % (x.get("@custom")) )
            sys.stdout.flush()
	    x['md'] = services.t_metadata(x.get("@custom"))

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

#/library/transcript/{colId}/{docId}/{page}/{tsId}/{regionId}
# view that lists lines in region and some region level metadata
@t_login_required
def region(request, collId, docId, page, transcriptId, regionId):
    # We need to be able to target a transcript (as mentioned elsewhere)
    # here there is no need for anything over than the pageXML really
    # we could get one transcript from ...{page}/curr, but for completeness would 
    # rather use transciptId to target a particular transcript
    transcripts = services.t_page(request,collId, docId, page) 

    #To get the page image url we need the full_doc (we hope it's been cached)
    full_doc = services.t_document(request, collId, docId, -1)
    index = int(page)-1
    # and then extract the correct page from full_doc (may be better from a  separate page data request??)
    pagedata = full_doc.get('pageList').get('pages')[index]
    
    sys.stdout.write("############# PAGEDATA: %s\r\n" % pagedata )
    #we are only using the transcripts to get the pageXML for a particular transcript...
    pageXML_url = None;
    for x in transcripts:
	if int(x.get("tsId")) == int(transcriptId):
	    pageXML_url = x.get("url")
	    break
 
    if pageXML_url:
	transcript = services.t_transcript(request,transcriptId,pageXML_url)

    regions=transcript.get("PcGts").get("Page").get("TextRegion");
    if isinstance(regions, dict):
	regions = [regions]

    for x in regions:
	x['key'] = x.get("@id")
	if(unicode(regionId) == unicode(x.get("@id"))):
	    region = x

    if(region.get("Coords")):
	region['crop_str'] = crop(region.get("Coords").get("@points"))

    nav = navigation.up_next_prev("region",regionId,regions,[collId,docId,page,transcriptId])

#    sys.stdout.write("REGION: %s\r\n" % (region) )
#    sys.stdout.flush()

    lines = region.get("TextLine")
    if isinstance(lines, dict):
        lines = [lines]
    #parse metadata
    if lines:
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
		'imageUrl' : pagedata.get("url"),
		})
def crop(coords):
    sys.stdout.write("############# COORDS: %s\r\n" % coords )
   # coords = region.get("Coords").get("@points")
    points = coords.split()	
    xmin=ymin=99999999 #TODO durh...
    xmax=ymax=0
    points = [map(int, point.split(',')) for point in points]
    #boo two loops! but I like this one above here...
    #TODO woops... I actually need this to x-off y-off widt and height...
    for point in points:
	if point[1] > ymax : ymax=point[1]
	if point[1] < ymin : ymin=point[1]
	if point[0] > xmax : xmax=point[0]
	if point[0] < xmin : xmin=point[0]
    crop = {'x':xmin, 'y':ymin, 'w':(xmax-xmin), 'h': (ymax-ymin)}
    crop_str = str(crop.get('x'))+"x"+str(crop.get('y'))+"x"+str(crop.get('w'))+"x"+str(crop.get('h'))

    return crop_str
#    sys.stdout.write("POINTS: %s\r\n" % (points) )
#    sys.stdout.write("CROP: %s\r\n" % (crop) )


#/library/transcript/{colId}/{docId}/{page}/{tsId}/{regionId}/{lineId}
# view that lists words in line and some line level metadata
@t_login_required
def line(request, collId, docId, page, transcriptId, regionId, lineId):
    # We need to be able to target a transcript (as mentioned elsewhere)
    # here there is no need for anything over than the pageXML really
    # we could get one transcript from ...{page}/curr, but for completeness would 
    # rather use transciptId to target a particular transcript
    transcripts = services.t_page(request,collId, docId, page) 
    #we are only using the transcripts to get the pageXML for a particular
    pageXML_url = None;
    for x in transcripts:
	if int(x.get("tsId")) == int(transcriptId):
	    pageXML_url = x.get("url")
	    break
 
    if pageXML_url:
	transcript = services.t_transcript(request,transcriptId,pageXML_url)

    #To get the page image url we need the full_doc (we hope it's been cached)
    full_doc = services.t_document(request, collId, docId, -1)
    index = int(page)-1
    # and then extract the correct page from full_doc (may be better from a  separate page data request??)
    pagedata = full_doc.get('pageList').get('pages')[index]

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

    if(line.get("Coords")):
	line['crop_str'] = crop(line.get("Coords").get("@points"))

    nav = navigation.up_next_prev("line",lineId,lines,[collId,docId,page,transcriptId,regionId])

#    sys.stdout.write("REGION: %s\r\n" % (region) )
#    sys.stdout.flush()

    words = line.get("Word")
    if isinstance(words, dict):
        words = [words]
    #parse metadata
    if words:
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
		'imageUrl' : pagedata.get("url"),
		})

#/library/transcript/{colId}/{docId}/{page}/{tsId}/{regionId}/{lineId}/{wordId}
# view that shows some word level metadata
@t_login_required
def word(request, collId, docId, page, transcriptId, regionId, lineId, wordId):
    # booo hiss
    transcripts = services.t_page(request, collId, docId, page) 
    #we are only using the pagedata to get the pageXML for a particular
    pageXML_url = None;
    for x in transcripts:
	if int(x.get("tsId")) == int(transcriptId):
	    pageXML_url = x.get("url")
	    break
 
    if pageXML_url:
	transcript = services.t_transcript(request,transcriptId,pageXML_url)

    #To get the page image url we need the full_doc (we hope it's been cached)
    full_doc = services.t_document(request, collId, docId, -1)
    index = int(page)-1
    # and then extract the correct page from full_doc (may be better from a  separate page data request??)
    pagedata = full_doc.get('pageList').get('pages')[index]

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
		
    if(word.get("Coords")):
	word['crop_str'] = crop(word.get("Coords").get("@points"))

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
		'imageUrl' : pagedata.get("url"),
		})

# Randomly fetch region/line/word this gives us an awful lot of empty responses
# Ideally we want to filter out the transcripts that don't contain good qulity data
# This may be as simple as isPublished(), rather than any analysis on the content
@t_login_required
def rand(request, collId, element):
    collection = services.t_collection(request,collId)
    if(collection == 403): #no access to requested collection
       sys.stdout.write("403 referrer: %s%% \r\n" % (request.META.get("HTTP_REFERER")) )
       sys.stdout.flush()
       return HttpResponseRedirect('/library/collection_noaccess/'+collId)


    doc = random.choice(collection)


    collection = None
    for x in doc.get("collectionList").get("colList"):
        if unicode(x.get("colId")) == unicode(collId):
	    collection = x

    sys.stdout.write("RANDOM DOC: %s\r\n" % (doc.get("docId")) )
    sys.stdout.flush()
   
    pages  = services.t_document(request, collId, doc.get("docId"), 0)
    page = random.choice(pages.get("pageList").get("pages"))

    sys.stdout.write("RANDOM PAGE: %s\r\n" % (page.get("pageNr")) )
    sys.stdout.flush()

    #best to avoid a random transcript, so we'll go for the current in the hope that it is best....
    current_transcript = services.t_current_transcript(request, collId, doc.get("docId"), page.get("pageNr"))
    transcript = services.t_transcript(request, current_transcript.get("tsId"),current_transcript.get("url"))
 
    word = None
    line = None
    region = None

    regions = transcript.get("PcGts").get("Page").get("TextRegion")
    if isinstance(regions, dict):
        regions = [regions]

    if regions:
         region = random.choice(regions)
	 if element == "region" :
	    	sys.stdout.write("region I have\r\n" )
         lines = region.get("TextLine")
    else:
	if transcript.get("PcGts").get("Page").get("TextLine"):
	    # I don't think we ever get here.. need to check with UIBK if Page > TextLine is even possible
	    sys.stdout.write("I HAVE A LINE DIRECT IN PAGE\r\n" )
     	    sys.stdout.flush()
	    lines = transcript.get("PcGts").get("Page").get("TextLine")
	else:
    	    sys.stdout.write("NO TEXT IN REGION\r\n" )
    	    return render(request, 'libraryapp/random.html', {
			"level": element, 
			"text": {},
			"collection" : collection,
			"document" : doc,
			"page" : page,
			"transcript" : transcript,
			} )
    
    if isinstance(lines, dict):
        lines = [lines]

    if element in ['line', 'word'] :
	    if lines:
		line = random.choice(lines);
	    else:
		return render(request, 'libraryapp/random.html', {
				"level": element, 
				"text": {},
				"collection" : collection,
				"document" : doc,
				"page" : page,
				"transcript" : transcript,
				} )

	    sys.stdout.write("LINE: %s\r\n" % ( line ) )
	    if element == "word" :
		    words = line.get("Word")
		    if isinstance(words, dict):
			words = [words]

		    if words:
			word = random.choice(words);
		    else:
			return render(request, 'libraryapp/random.html', {
					"level": element, 
					"text": {},
					"collection" : collection,
					"document" : doc,
					"page" : page,
					"transcript" : transcript,
					} )

    switcher = {
        "region" : display_random(request,element,region,collection,doc,page),
        "line" : display_random(request,element,line,collection,doc,page),
        "word" : display_random(request,element,word,collection,doc,page),
    }

    return switcher.get(element, {})

def display_random(request,level,data, collection, doc, page):
    text = None
    if not data :
	text = {}
    elif data.get("TextEquiv"):
	if data.get("TextEquiv").get("Unicode"):
	    text = unicode(data.get("TextEquiv").get("Unicode"))

    return render(request, 'libraryapp/random.html', {
		"level": level, 
		"text": text,
		"collection" : collection,
		"document" : doc,
		"page" : page,
	} )

@t_login_required
def search(request):
    return render(request, 'libraryapp/search.html')

def about(request):
    return render(request, 'libraryapp/about.html')

def message_modal(request):
    return render(request, 'libraryapp/message_modal.html')

def user_guide(request):
    return render(request, 'libraryapp/user_guide.html')

@t_login_required
def users(request, collId, userId):
    return render(request, 'libraryapp/users.html')

@t_login_required
def profile(request):
    collections = request.session.get("collections");
    return render(request, 'libraryapp/profile.html', {'collections': collections})

#error pages (where not handled by modals
def collection_noaccess(request, collId):
    if(request.get_full_path() == request.META.get("HTTP_REFERER") or re.match(r'^.*login.*', request.META.get("HTTP_REFERER"))):
        back = None
    else:
        back = request.META.get("HTTP_REFERER") #request.GET.get("back")

    return render(request, 'libraryapp/error.html', {
                'msg' : _("I'm afraid you are not allowed to access this collection"),
                'back' : back,
            })
def error(request):
    back = settings.APP_BASEURL+"/register"

    return render(request, 'libraryapp/error.html', {
                'msg' : messages,
                'back' : back,
            })

@t_login_required
def ingest_mets_xml(request):
    if request.method == 'POST':
        try: 
            #if ingest_mets_xml_file_form.is_valid(): #  TODO Check something for better error messages? And validate the file. Note: Django allows form submission, even if no file has been selected.
            services.t_ingest_mets_xml(request.POST.get('collection'), request.FILES['mets_file'])
            messages.info(request, 'File is being uploaded.')# TODO i18n,
            return HttpResponse(json.dumps({'RESET': 'true', 'MESSAGE': render_to_string('libraryapp/message_modal.html', request=request)}), content_type='text/plain')
        except:
            messages.error(request, 'Error!')# TODO i18n,
            return HttpResponse(json.dumps({'RESET': 'false', 'MESSAGE': render_to_string('libraryapp/message_modal.html', request=request)}), content_type='text/plain') 
    else:
        ingest_mets_xml_file_form = MetsFileForm()
        collections = request.session.get("collections")
        return render(request, 'libraryapp/ingest_mets_xml.html', {'ingest_mets_xml_form': ingest_mets_xml_file_form,  'collections': collections})

@t_login_required
def ingest_mets_url(request):
    if request.method == 'POST':
        # What should be checked here and what can be left up to Transkribus?
        if (services.t_ingest_mets_url(request.POST.get('collection'), request.POST.get('url'))):
            messages.info(request, 'URL is being processed.')# TODO i18n,
            return HttpResponse(json.dumps({'RESET': 'true', 'MESSAGE': render_to_string('libraryapp/message_modal.html', request=request)}), content_type='text/plain')
        else:
            messages.error(request, 'URL processing failed.')# TODO i18n,
            return HttpResponse(json.dumps({'RESET': 'false', 'MESSAGE': render_to_string('libraryapp/message_modal.html', request=request)}), content_type='text/plain')
    else:
        data = {'url': request.GET.get('metsURL', '')}
        ingest_mets_url_form = IngestMetsUrlForm(initial=data)
        collections = request.session.get("collections")
        return render(request, 'libraryapp/ingest_mets_url.html', {'ingest_mets_url_form': ingest_mets_url_form, 'collections': collections})

@t_login_required
def collections_dropdown(request):
    collections = services.t_collections()
    return render(request, 'libraryapp/collections_dropdown.html', {'collections': collections})

@t_login_required
def create_collection_modal(request):
    if (services.t_create_collection(request.POST.get('collection_name'))):
        return HttpResponse("New collection created successfully!", content_type="text/plain")
    #else:
           # TODO Handle failures... 

@t_login_required           
def jobs_list(request):
    if ('true' == request.POST.get('only_unfinished')):# TODO Consider making a form instead for persistence?
        jobs = services.t_jobs('INCOMPLETE')
        only_unfinished = 'checked'
    else:
        jobs = services.t_jobs()
        only_unfinished = ''
    return render(request, 'libraryapp/jobs_list.html', {'jobs': jobs, 'only_unfinished': only_unfinished})

@t_login_required
def jobs(request):
    jobs = services.t_jobs('INCOMPLETE')
    only_unfinished = 'checked'
    return render(request, 'libraryapp/jobs.html', {'jobs': jobs, 'only_unfinished': only_unfinished})

@t_login_required
def job_count(request):# TODO Consider how much of a DOS risk these queries constitute.
    # I DO NOT KNOW why returning a JsonResponse or 'application/json' breaks the cookies. The uncommented response below is what works. HttpFox indicates that the only difference is text/plain vs. application/json (or just json, both fail).
    
    #sys.stdout.write("COOKIES: %s%% \r\n" % request.COOKIES)
    #sys.stdout.flush() 
    
    #return  JsonResponse({'CREATED': services.t_job_count('CREATED'), 'FAILED': services.t_job_count('FAILED'), 'FINISHED': services.t_job_count('FINISHED'),'WAITING': services.t_job_count('WAITING'), 'RUNNING': services.t_job_count('RUNNING'), 'CANCELED': services.t_job_count('CANCELED'), 'INCOMPLETE': services.t_job_count('INCOMPLETE')});
    #return HttpResponse(json.dumps({'CREATED': services.t_job_count('CREATED'), 'FAILED': services.t_job_count('FAILED'), 'FINISHED': services.t_job_count('FINISHED'),'WAITING': services.t_job_count('WAITING'), 'RUNNING': services.t_job_count('RUNNING'), 'CANCELED': services.t_job_count('CANCELED'), 'INCOMPLETE': services.t_job_count('INCOMPLETE')}), content_type='application/json')
    return HttpResponse(json.dumps({'CREATED': services.t_job_count('CREATED'), 'FAILED': services.t_job_count('FAILED'), 'FINISHED': services.t_job_count('FINISHED'),'WAITING': services.t_job_count('WAITING'), 'RUNNING': services.t_job_count('RUNNING'), 'CANCELED': services.t_job_count('CANCELED'), 'INCOMPLETE': services.t_job_count('INCOMPLETE')}), content_type='text/plain')

@t_login_required
def changed_jobs_modal(request):
    jobs = services.t_jobs()
    return render(request, 'libraryapp/changed_jobs_modal.html', {'jobs': jobs})

@t_login_required           
def jobs_list_compact(request):
    jobs = services.t_jobs()
    return render(request, 'libraryapp/jobs_list_compact.html', {'jobs': jobs})# TODO Decide what should be shown in the compact view. Only jobs which have changed since some "acknowledgement"? Since the last login? Since...?

@t_login_required
def kill_job(request):
    if (services.t_kill_job(request.POST.get('job_id'))):
        return jobs_list(request)
    else:
        return jobs_list(request) # test
    # Leave as is or return an error message? The javascript could also handle the error...
    
