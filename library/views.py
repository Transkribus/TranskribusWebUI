#imports of python modules
import json
import sys
import re
import random

#Imports of django modules
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils import translation
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from read.utils import crop, t_metadata
#Imports pf read modules
from read.decorators import t_login_required
from read.services import *
#t_collection, t_register,

#Imports from app (library)
import library.settings
from . import navigation
from .forms import RegisterForm, IngestMetsUrlForm, MetsFileForm, QuickIngestMetsUrlForm

#from profiler import profile #profile is a decorator, but things get circular if I include it in decorators.py so...


def register(request):
#TODO this is generic guff need to extend form for extra fields, send reg data to transkribus and authticate (which will handle the user creation)

    if request.user.is_authenticated(): #shouldn't really happen but...
        return HttpResponseRedirect(request.build_absolute_url('/library/'))
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
                t_register(request)
                return HttpResponseRedirect(request.build_absolute_url('/library/profile'))
                #tried out modal here and it is noce (but not really for registration)
#               messages.info(request, _('Registration requested please check your email.'))
#                return HttpResponse(json.dumps({'RESET': 'true', 'MESSAGE': render_to_string('library/message_modal.html', request=request)}), content_type='text/plain')
            except ValueError as err:
                sys.stdout.write("### t_register response ERROR RAISED: %s  \r\n" % (err) )
#               return render(request, 'registration/register.html', {'register_form': form} )
                #Why the f**k won't this redirect?!? TODO fix or try another method
                return HttpResponseRedirect(request.build_absolute_url('/library/error'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegisterForm()

    #Recpatch errors are not properly dislpayed by bootstrap-form... hmph
    return render(request, 'registration/register.html', {'register_form': form} )

def index(request):
    return render(request, 'library/homepage.html' )


#/library/collections
#view that lists available collections for a user
#@profile("collections.prof")
@t_login_required
def collections(request):
    collections = t_collections(request)
    if isinstance(collections,HttpResponse):
        return collections
    return render(request, 'library/collections.html', {'collections': collections} )

#/library/collection/{colId}
#view that
# - lists documents
# - also lists pages for documents
#@profile("collection.prof")
@t_login_required
def collection(request, collId):
    #this is actually a call to collections/{collId}/list and returns only the document objects for a collection
    docs = t_collection(request,{'collId':collId})
    #probably a redirect if an HttpResponse
    if isinstance(docs,HttpResponse):
        return docs

    collections = t_collections(request)
    #there is currently no transkribus call for collections/{collId} on its own to fetch just data for collection
    # so we'll loop through collections and pick out collection level metadata freom there
    # The same could be achieved using the list of documents (ie pick first doc match collId with member of colList)
    collection = None
    for x in collections:
        if str(x.get("colId")) == str(collId):
            collection = x

    nav = navigation.up_next_prev("collection",collId,collections)

    #collection view goes down two levels (ie documents and then pages)
    # data prepared fro fancytree.js representation
    for doc in docs:
        doc['collId'] = collId
        doc['key'] = doc['docId']
        doc['folder'] = 'true'
        #fetch full document data with no transcripts for pages //TODO avoid REST request in loop?
#       fulldoc  = t_document(request, collId, doc['docId'], 0)
#       doc['children'] = fulldoc.get('pageList').get("pages")
#        for x in doc['children']:
#          x['title']=x['imgFileName']
#          x['collId']=collId

    return render(request, 'library/collection.html', {
        'collId': collId,
        'collection': collection,
        'documents': docs,
#        'documents_json': json.dumps(docs),
        'up': nav['up'],
        'next': nav['next'],
        'prev': nav['prev'],
        })

#/library/document/{colId}/{docId}
# view that lists pages in doc and some doc level metadata
#@profile("document.prof")
@t_login_required
def document(request, collId, docId, page=None):
    collection = t_collection(request, {'collId': collId})
    if isinstance(collection,HttpResponse):
        return collection
    full_doc = t_document(request, collId, docId,-1)
    if isinstance(full_doc,HttpResponse):
        return full_doc

    nav = navigation.up_next_prev("document",docId,collection,[collId])

    return render(request, 'library/document.html', {
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
    full_doc = t_document(request, collId, docId, -1)
    if isinstance(full_doc,HttpResponse):
        return full_doc
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

    return render(request, 'library/page.html', {
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
    pagedata = t_page(request, collId, docId, page)
    if isinstance(pagedata,HttpResponse):
        return pagedata

    nav = navigation.up_next_prev("transcript",transcriptId,pagedata,[collId,docId,page])

    pageXML_url = None;
    for x in pagedata:
        if int(x.get("tsId")) == int(transcriptId):
            pageXML_url = x.get("url")
            break
    sys.stdout.write("PAGEXML URL : %s \r\n" % (pageXML_url) )
    sys.stdout.flush()

    if pageXML_url:
        transcript = t_transcript(request,transcriptId,pageXML_url)
        if isinstance(transcript,HttpResponse):
            return transcript


    regions=transcript.get("PcGts").get("Page").get("TextRegion");

    if isinstance(regions, dict):
        regions = [regions]

    if regions:
        for x in regions:
            sys.stdout.write("CUSTOM : %s \r\n" % (x.get("@custom")) )
            sys.stdout.flush()
            x['md'] = t_metadata(x.get("@custom"))

    return render(request, 'library/transcript.html', {
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
    transcripts = t_page(request,collId, docId, page)
    if isinstance(transcripts,HttpResponse):
        return transcripts

    #To get the page image url we need the full_doc (we hope it's been cached)
    full_doc = t_document(request, collId, docId, -1)
    if isinstance(full_doc,HttpResponse):
        return full_doc

    index = int(page)-1
    # and then extract the correct page from full_doc (may be better from a  separate page data request??)
    pagedata = full_doc.get('pageList').get('pages')[index]

    t_log("############# TRANSCRIPTS: %s" % transcripts )

    #we are only using the transcripts to get the pageXML for a particular transcript...
    pageXML_url = None;
    for x in transcripts:
        if int(x.get("tsId")) == int(transcriptId):
            t_log("############# transcript id comp: %s" % x.get("tsId") )
            t_log("############# transcript id comp: %s" % transcriptId )
            pageXML_url = x.get("url")
            break

    t_log("############# PAGEXML_url: %s" % pageXML_url )

    if pageXML_url:
        transcript = t_transcript(request,transcriptId,pageXML_url)
        if isinstance(transcript,HttpResponse):
            return transcript

    regions=transcript.get("PcGts").get("Page").get("TextRegion");
    if isinstance(regions, dict):
        regions = [regions]

    for x in regions:
        x['key'] = x.get("@id")
        if(str(regionId) == str(x.get("@id"))):
            region = x

    if(region.get("Coords")):
        region['crop'] = crop(region.get("Coords").get("@points"),True)

    nav = navigation.up_next_prev("region",regionId,regions,[collId,docId,page,transcriptId])

#    sys.stdout.write("REGION: %s\r\n" % (region) )
#    sys.stdout.flush()

    lines = region.get("TextLine")
    if isinstance(lines, dict):
        lines = [lines]
    #parse metadata
    if lines:
        for x in lines:
            x['md'] = t_metadata(x.get("@custom"))

    return render(request, 'library/region.html', {
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


#/library/transcript/{colId}/{docId}/{page}/{tsId}/{regionId}/{lineId}
# view that lists words in line and some line level metadata
@t_login_required
def line(request, collId, docId, page, transcriptId, regionId, lineId):
    # We need to be able to target a transcript (as mentioned elsewhere)
    # here there is no need for anything over than the pageXML really
    # we could get one transcript from ...{page}/curr, but for completeness would
    # rather use transciptId to target a particular transcript
    transcripts = t_page(request,collId, docId, page)
    if isinstance(transcripts,HttpResponse):
        return transcripts
    #we are only using the transcripts to get the pageXML for a particular
    pageXML_url = None;
    for x in transcripts:
        if int(x.get("tsId")) == int(transcriptId):
            pageXML_url = x.get("url")
            break

    if pageXML_url:
        transcript = t_transcript(request,transcriptId,pageXML_url)
        if isinstance(transcript,HttpResponse):
            return transcript

    #To get the page image url we need the full_doc (we hope it's been cached)
    full_doc = t_document(request, collId, docId, -1)
    if isinstance(full_doc,HttpResponse):
        return full_doc

    index = int(page)-1
    # and then extract the correct page from full_doc (may be better from a  separate page data request??)
    pagedata = full_doc.get('pageList').get('pages')[index]

    #This now officially bonkers....
    regions=transcript.get("PcGts").get("Page").get("TextRegion");
    if isinstance(regions, dict):
        regions = [regions]

    for x in regions:
        if(str(regionId) == str(x.get("@id"))):
            region = x

    lines=region.get("TextLine");

    if isinstance(lines, dict):
        lines = [lines]


    for x in lines:
        x['key'] = x.get("@id")
        if(str(lineId) == str(x.get("@id"))):
            line = x

    if(line.get("Coords")):
        line['crop'] = crop(line.get("Coords").get("@points"),True)


    nav = navigation.up_next_prev("line",lineId,lines,[collId,docId,page,transcriptId,regionId])

#    sys.stdout.write("REGION: %s\r\n" % (region) )
#    sys.stdout.flush()

    words = line.get("Word")
    if isinstance(words, dict):
        words = [words]
    #parse metadata
    if words:
        for x in words:
            x['md'] = t_metadata(x.get("@custom"))

    return render(request, 'library/line.html', {
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
    transcripts = t_page(request, collId, docId, page)
    if isinstance(transcripts,HttpResponse):
        return transcripts
    #we are only using the pagedata to get the pageXML for a particular
    pageXML_url = None;
    for x in transcripts:
        if int(x.get("tsId")) == int(transcriptId):
            pageXML_url = x.get("url")
            break

    if pageXML_url:
        transcript = t_transcript(request,transcriptId,pageXML_url)
        if isinstance(transcript,HttpResponse):
            return transcript

    #To get the page image url we need the full_doc (we hope it's been cached)
    full_doc = t_document(request, collId, docId, -1)
    if isinstance(full_doc,HttpResponse):
        return full_doc

    index = int(page)-1
    # and then extract the correct page from full_doc (may be better from a  separate page data request??)
    pagedata = full_doc.get('pageList').get('pages')[index]

    #This now officially bonkers....
    regions=transcript.get("PcGts").get("Page").get("TextRegion");
    if isinstance(regions, dict):
        regions = [regions]

    for x in regions:
        if(str(regionId) == str(x.get("@id"))):
            region = x

    lines=region.get("TextLine");

    if isinstance(lines, dict):
        lines = [lines]

    for x in lines:
        if(str(lineId) == str(x.get("@id"))):
            line = x

    words = line.get("Word")
    if isinstance(words, dict):
        words = [words]


    #parse metadata
    for x in words:
        x['key'] = x.get("@id")
        if(str(wordId) == str(x.get("@id"))):
            x['md'] = t_metadata(x.get("@custom"))
            word = x

    if(word.get("Coords")):
        word['crop'] = crop(word.get("Coords").get("@points"),True)

    nav = navigation.up_next_prev("word",wordId,words,[collId,docId,page,transcriptId,regionId,lineId])

    return render(request, 'library/word.html', {
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
    collection = t_collection(request, {'collId': collId})

    if isinstance(collection,HttpResponse):
        return collection

    doc = random.choice(collection)

    collection = None
    for x in doc.get("collectionList").get("colList"):
        if str(x.get("colId")) == str(collId):
            collection = x

    pages  = t_document(request, collId, doc.get("docId"), 0)
    if isinstance(pages,HttpResponse):
        return pages
    page = random.choice(pages.get("pageList").get("pages"))

    sys.stdout.write("RANDOM PAGE: %s\r\n" % (page.get("pageNr")) )
    sys.stdout.flush()

    #best to avoid a random transcript, so we'll go for the current in the hope that it is best....
    current_transcript = t_current_transcript(request, collId, doc.get("docId"), page.get("pageNr"))
    transcript = t_transcript(request, current_transcript.get("tsId"),current_transcript.get("url"))

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
            return render(request, 'library/random.html', {
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
            return render(request, 'library/random.html', {
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
                return render(request, 'library/random.html', {
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
            text = str(data.get("TextEquiv").get("Unicode"))

    return render(request, 'library/random.html', {
                "level": level,
                "text": text,
                "collection" : collection,
                "document" : doc,
                "page" : page,
        } )

@t_login_required
def search(request):
    return render(request, 'library/search.html')

def about(request):
    return render(request, 'library/about.html')

def message_modal(request):
    return render(request, 'library/message_modal.html')

def user_guide(request):
    return render(request, 'library/user_guide.html')

@t_login_required
def users(request, collId, userId):
    return render(request, 'library/users.html')

@t_login_required
def profile(request):
    collections = t_collections(request)
    return render(request, 'library/profile.html', {'collections': collections})

#error pages (where not handled by modals
def collection_noaccess(request, collId):
    if(request.get_full_path() == request.META.get("HTTP_REFERER") or re.match(r'^.*login.*', request.META.get("HTTP_REFERER"))):
        back = None
    else:
        back = request.META.get("HTTP_REFERER") #request.GET.get("back")

    return render(request, 'library/error.html', {
                'msg' : _("I'm afraid you are not allowed to access this collection"),
                'back' : back,
            })
def error(request):
    back = settings.APP_BASEURL+"/register"

    return render(request, 'library/error.html', {
                'msg' : messages,
                'back' : back,
            })

@t_login_required
def ingest_mets_xml(request):
    if request.method == 'POST':
        try:
            #if ingest_mets_xml_file_form.is_valid(): #  TODO Check something for better error messages? And validate the file. Note: Django allows form submission, even if no file has been selected.
            t_ingest_mets_xml(request.POST.get('collection'), request.FILES['mets_file'])
            messages.info(request, 'File is being uploaded.')# TODO i18n,
            return HttpResponse(json.dumps({'RESET': 'true', 'MESSAGE': render_to_string('library/message_modal.html', request=request)}), content_type='text/plain')
        except:
            messages.error(request, 'Error!')# TODO i18n,
            return HttpResponse(json.dumps({'RESET': 'false', 'MESSAGE': render_to_string('library/message_modal.html', request=request)}), content_type='text/plain')
    else:
        ingest_mets_xml_file_form = MetsFileForm()
        collections = t_collections(request)
        if isinstance(collections,HttpResponse):
            return collections

        return render(request, 'library/ingest_mets_xml.html', {'ingest_mets_xml_form': ingest_mets_xml_file_form,  'collections': collections})

@t_login_required
def ingest_mets_url(request):
    if request.method == 'POST':
        # What should be checked here and what can be left up to Transkribus?
        if (t_ingest_mets_url(request.POST.get('collection'), request.POST.get('url'))):
            messages.info(request, 'URL is being processed.')# TODO i18n,
            return HttpResponse(json.dumps({'RESET': 'true', 'MESSAGE': render_to_string('library/message_modal.html', request=request)}), content_type='text/plain')
        else:
            messages.error(request, 'URL processing failed.')# TODO i18n,
            return HttpResponse(json.dumps({'RESET': 'false', 'MESSAGE': render_to_string('library/message_modal.html', request=request)}), content_type='text/plain')
    else:
        data = {'url': request.GET.get('metsURL', '')}
        ingest_mets_url_form = IngestMetsUrlForm(initial=data)
        collections = t_collections(request)
        if isinstance(collections,HttpResponse):
            return collections

        return render(request, 'library/ingest_mets_url.html', {'ingest_mets_url_form': ingest_mets_url_form, 'collections': collections})

@t_login_required
def quick_ingest_mets_url(request):
    if request.method == 'POST':
        if (t_ingest_mets_url(request.POST.get('collection'), request.POST.get('url'))):
            return render(request, 'library/redirect_from_quick_ingest.html', {'return_url': request.POST.get('return_url', '')})
        else:
            return render(request, 'library/redirect_from_quick_ingest.html', {'return_url': request.POST.get('return_url', '')})
    else:
        data = {'url': request.GET.get('metsURL', ''), 'return_url': request.GET.get('returnURL', '')}
        t_log('url %s' % data)
        quick_ingest_mets_url_form = QuickIngestMetsUrlForm(initial=data)
        collections = collections = t_collections(request)
        return render(request, 'library/quick_ingest_mets_url.html', {'quick_ingest_mets_url_form': quick_ingest_mets_url_form, 'collections': t_collections(request)})

@t_login_required
def collections_dropdown(request):
    collections = t_collections(request)
    if isinstance(collections,HttpResponse):
        return collections
    return render(request, 'library/collections_dropdown.html', {'collections': collections})

@t_login_required
def create_collection_modal(request):
    if (t_create_collection(request, request.POST.get('collection_name'))):
        return HttpResponse("New collection created successfully!", content_type="text/plain")
    else:
        t_log("couldn't create collection because (reasons?)")

@t_login_required
def jobs_list(request):
    if ('true' == request.POST.get('only_unfinished')):# TODO Consider making a form instead for persistence?
        jobs = t_jobs('INCOMPLETE')
        only_unfinished = 'checked'
    else:
        jobs = t_jobs()
        only_unfinished = ''
    return render(request, 'library/jobs_list.html', {'jobs': jobs, 'only_unfinished': only_unfinished})

@t_login_required
def jobs(request):
    jobs = t_jobs('INCOMPLETE')
    only_unfinished = 'checked'
    return render(request, 'library/jobs.html', {'jobs': jobs, 'only_unfinished': only_unfinished})

@t_login_required
def job_count(request):# TODO Consider how much of a DOS risk these queries constitute.
    # I DO NOT KNOW why returning a JsonResponse or 'application/json' breaks the cookies. The uncommented response below is what works. HttpFox indicates that the only difference is text/plain vs. application/json (or just json, both fail).

    #sys.stdout.write("COOKIES: %s%% \r\n" % request.COOKIES)
    #sys.stdout.flush()

    #return  JsonResponse({'CREATED': t_job_count('CREATED'), 'FAILED': t_job_count('FAILED'), 'FINISHED': t_job_count('FINISHED'),'WAITING': t_job_count('WAITING'), 'RUNNING': t_job_count('RUNNING'), 'CANCELED': t_job_count('CANCELED'), 'INCOMPLETE': t_job_count('INCOMPLETE')});
    #return HttpResponse(json.dumps({'CREATED': t_job_count('CREATED'), 'FAILED': t_job_count('FAILED'), 'FINISHED': t_job_count('FINISHED'),'WAITING': t_job_count('WAITING'), 'RUNNING': t_job_count('RUNNING'), 'CANCELED': t_job_count('CANCELED'), 'INCOMPLETE': t_job_count('INCOMPLETE')}), content_type='application/json')
    #try:
        #t_log("polling result: " + json.dumps({'CREATED': t_job_count('CREATED'), 'FAILED': t_job_count('FAILED'), 'FINISHED': t_job_count('FINISHED'),'WAITING': t_job_count('WAITING'), 'RUNNING': t_job_count('RUNNING'), 'CANCELED': t_job_count('CANCELED'), 'INCOMPLETE': t_job_count('INCOMPLETE')}))
    return HttpResponse(json.dumps({'CREATED': t_job_count('CREATED'), 'FAILED': t_job_count('FAILED'), 'FINISHED': t_job_count('FINISHED'),'WAITING': t_job_count('WAITING'), 'RUNNING': t_job_count('RUNNING'), 'CANCELED': t_job_count('CANCELED'), 'INCOMPLETE': t_job_count('INCOMPLETE')}), content_type='text/plain')
    #except:
       # t_log("exception when polling")
        #return HttpResponse(status=500)

@t_login_required
def changed_jobs_modal(request):
    jobs = t_jobs()
    return render(request, 'library/changed_jobs_modal.html', {'jobs': jobs})

@t_login_required
def jobs_list_compact(request):
    jobs = t_jobs()
    return render(request, 'library/jobs_list_compact.html', {'jobs': jobs})# TODO Decide what should be shown in the compact view. Only jobs which have changed since some "acknowledgement"? Since the last login? Since...?

@t_login_required
def kill_job(request):
    if (t_kill_job(request.POST.get('job_id'))):
        return jobs_list(request)
    else:
        return jobs_list(request) # test
    # Leave as is or return an error message? The javascript could also handle the error...
