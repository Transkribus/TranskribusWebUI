import requests
#workaround for insecure platform warnings...
#http://stackoverflow.com/questions/29099404/ssl-insecureplatform-error-when-using-requests-package
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
#TODO sudo pip install 'requests[security]'
#Possibly check for openssl-devel python-devel libffi-devel (yum)

#import urllib2
import xmltodict
import dicttoxml
#from lxml import objectify
from django.http import HttpResponseRedirect
from django.conf import settings
import sys
import json
import re

#TODO rationalise this code
# - lots of repitition
# - possible to find or create (UIBK to create) more efficient ways of getting data
# - epecially t_collection (which calls t_document in loop)

s = requests.Session()

def t_register(request):

    url = settings.TRP_URL+'user/register'

    sys.stdout.write("### IN t_register: %s   \r\n" % (url) )
    sys.stdout.flush()

    params = {'user': request.POST.get('user'),
                'pw': request.POST.get('pw'),
                'firstName': request.POST.get('firstName'),
                'lastName': request.POST.get('lastNaame'),
#               'email': request.POST.get('email'),
#               'gender': request.POST.get('gender'),
#               'orcid':request.POST.get('orcid'),
                'token': request.POST.get('g-recaptcha-response'),
                'application': "TSX"}
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    sys.stdout.write("### [POST REQUEST] t_register POST to: %s with %s \r\n" % (url,params) )
    sys.stdout.flush()
    r = s.post(url, params=params, verify=False, headers=headers)
    sys.stdout.write("### t_register response STATUS_CODE: %s  \r\n" % (r.status_code) )
    sys.stdout.write("### t_register response CONTENT: %s  \r\n" % (r.content) )
    sys.stdout.flush()
    if r.status_code != requests.codes.ok:
        raise ValueError("Transkribus registration error",str(r.status_code),r.content)
        return None

    user_xml = r.text

    t_user=xmltodict.parse(user_xml)

    return t_user['trpUserLogin']

def t_login(user, pw):
    url = settings.TRP_URL+'auth/login'

    sys.stdout.write("### IN t_login: %s   \r\n" % (url) )
    sys.stdout.flush()

    params = {'user': user, 'pw': pw}
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    #TODO check wadl and use json (it is throwing a 415 at if just switching in the content-type)
#    headers = {'content-type': 'application/json'}

    sys.stdout.write("### [POST REQUEST] t_login POST to: %s with %s \r\n" % (url,'credentials') )
    sys.stdout.flush()
    r = s.post(url, params=params, verify=False, headers=headers)
    sys.stdout.write("### t_login response STATUS_CODE: %s  \r\n" % (r.status_code) )
    sys.stdout.flush()
    if r.status_code != requests.codes.ok:
        return None
    user_xml = r.text

    t_user=xmltodict.parse(user_xml)

    return t_user['trpUserLogin']

#refresh transkribus session (called by t_login_required decorator to test persistence/validity of transkribus session)
def t_refresh():
    url = settings.TRP_URL+'auth/refresh'

    sys.stdout.write("### [POST REQUEST] t_refresh will POST: %s   \r\n" % (url) )
    sys.stdout.flush()

    r = s.post(url, verify=False)

    sys.stdout.write("### t_refresh response STATUS_CODE: %s   \r\n" % (r.status_code) )
    sys.stdout.flush()

    if r.status_code != requests.codes.ok:
        return None
    else:
        return True

def t_collections():

    url = settings.TRP_URL+'collections/list'

    sys.stdout.write("### IN t_collectionssss: %s   \r\n" % (url) )
    sys.stdout.flush()

    headers = {'content-type': 'application/json'}
    params = {}

    sys.stdout.write("### [GET REQUEST] t_collectionssss will GET: %s with %s \r\n" % (url,params) )
    sys.stdout.flush()
    r = s.get(url, params=params, verify=False, headers=headers)
    if r.status_code != requests.codes.ok:
        sys.stdout.write("ERROR CODE: %s \r\n ERROR: %s" % (r.status_code, r.content) )
        sys.stdout.flush()
        return None

    collections_json=r.text
    collections = json.loads(collections_json)

    #use common param 'key' for ids
    for col in collections:
        col['key'] = col['colId']

    return collections

def t_collection(request,collId):

    url = '{!s}collections/{!s}/list'.format(settings.TRP_URL, collId)
    sys.stdout.write("### IN t_collectionnnn: %s   \r\n" % (url) )
    sys.stdout.flush()

    #we will keep the current collection in the session to decrease the number of calls transkribus.eu
    if "collection" in request.session :
        if request.session.get('collection')[0].get('cache_url') == url :
            sys.stdout.write("### [HAVE CACHE] t_collection HAS CACHED collection for: %s \r\n" % (url) )
            sys.stdout.flush()
            return request.session['collection']

    headers = {'content-type': 'application/json'}
    params = {}

    sys.stdout.write("### [GET REQUEST] t_collectionnnnn will GET: %s with %s \r\n" % (url,params) )
    sys.stdout.flush()
    r = s.get(url, params=params, verify=False, headers=headers)
    if r.status_code != requests.codes.ok:
        sys.stdout.write("ERROR CODE: %s%% \r\n ERROR: %s%%" % (r.status_code, r.content) )
        sys.stdout.flush()
        return r.status_code

    # collection_json=r.content
    collection_json = r.text
    t_collection = json.loads(collection_json)

    #Cache this to reduce calls on subsequent lower level web-pages
    t_collection[0]['cache_url'] = url
    sys.stdout.write("### [CAHCING] t_collection CACHING collection with ref : %s   \r\n" % (t_collection[0].get('cache_url')) )
    sys.stdout.flush()
    request.session['collection'] = t_collection

    return t_collection

def t_document(request, collId, docId, nrOfTranscripts=None):

    url = settings.TRP_URL+'collections/'+collId+'/'+str(docId)+'/fulldoc'
    sys.stdout.write("### IN t_document: %s   \r\n" % (url) )
    sys.stdout.flush()

     # doc caching turned off as was causing the transcript counts to be wrong TODO reinstate in a less crap way
     # we will keep the current document in the session to decrease the number of calls transkribus.eu
#    if "doc" in request.session :
#       if request.session.get('doc').get('cache_url') == url :
#            sys.stdout.write("### [HAVE CACHE] t_doc HAS CACHED doc for: %s \r\n" % (url) )
#           sys.stdout.flush()
#            return request.session['doc']

    headers = {'content-type': 'application/json'}

    params = {}
    if not nrOfTranscripts is None:
        params['nrOfTranscripts'] = nrOfTranscripts

    sys.stdout.write("### [GET REQUEST] t_document will GET %s with %s \r\n" % (url,params) )
    sys.stdout.flush()
    r = s.get(url, params=params, verify=False, headers=headers)
    if r.status_code != requests.codes.ok:
        return None

    doc_json = r.text
    t_doc = json.loads(doc_json)

    pages = t_doc.get("pageList").get("pages")
    for x  in pages:
        x['key'] = x.get('pageNr') #I'm aware this will replacce the legitimate key....

    #Cache this to reduce calls on subsequent lower level web-pages
    t_doc['cache_url'] = url
    sys.stdout.write("### [CAHCING] t_doc CACHING doc with ref : %s   \r\n" % (t_doc.get('cache_url')) )
    sys.stdout.flush()
    request.session['doc'] = t_doc

    return t_doc

#returns a list of transcripts for a page, no page metadata...
def t_page(request,collId, docId, page, nrOfTranscripts=None):

    #list of transcripts for this page
    url = settings.TRP_URL+'collections/'+collId+'/'+str(docId)+'/'+str(page)+'/list'

    sys.stdout.write("### IN t_page: %s   \r\n" % (url) )
    sys.stdout.flush()

    #we will keep the current page in the session to decrease the number of calls to transkribus
    if "page" in request.session :
        if request.session.get('page')[0].get('cache_url') == url :
            sys.stdout.write("### [HAVE CACHE] t_page HAS CACHED page for: %s \r\n" % (url) )
            sys.stdout.flush()
            return request.session['page']

    headers = {'content-type': 'application/json'}
    params = {}

    sys.stdout.write("### [GET REQUEST] t_page will GET %s with %s \r\n" % (url,params) )
    sys.stdout.flush()
    r = s.get(url, params=params, verify=False, headers=headers)
    if r.status_code != requests.codes.ok:
        return None

    # page_json = r.content
    page_json = r.text
    t_page = json.loads(page_json)

    #TODO would prefer a pageId rather than "page" which is a the page number
    for x  in t_page:
        #key is used already for transcripts, however using key is handy for jquery things like fancy tree...
        x['key'] = x.get('tsId')

    #Cache this to reduce calls on subsequent lower level web-pages
    #t_page is a list of objects, so where shall we keep the url.... in the first object I guess
    t_page[0]['cache_url'] = url
    sys.stdout.write("### [CAHCING] t_page CACHING page with ref : %s   \r\n" % (t_page[0].get('cache_url')) )
    sys.stdout.flush()
    request.session['page'] = t_page

    return t_page

#returns the current transcript for a page
def t_current_transcript(request,collId, docId, page):

    #list of transcripts for this page
    url = settings.TRP_URL+'collections/'+collId+'/'+str(docId)+'/'+str(page)+'/curr'

    sys.stdout.write("### IN t_current_transcript: %s   \r\n" % (url) )
    sys.stdout.flush()

    #we will keep the current page in the session to decrease the number of calls to transkribus
    if "current_transcript" in request.session :
        if request.session.get('current_transcript').get('cache_url') == url :
            sys.stdout.write("### [HAVE CACHE] t_current_transcript HAS CACHED current_transcript for: %s \r\n" % (url) )
            sys.stdout.flush()
            return request.session['current_transcript']

    headers = {'content-type': 'application/json'}
    params = {}

    sys.stdout.write("### [GET REQUEST] t_current_transcript will GET %s with %s \r\n" % (url,params) )
    sys.stdout.flush()
    r = s.get(url, params=params, verify=False, headers=headers)
    if r.status_code != requests.codes.ok:
        return None

    transcript_json = r.text
    t_transcript = json.loads(transcript_json)

    t_transcript['key'] = t_transcript.get('tsId')

    #Cache this to reduce calls on subsequent lower level web-pages
    #t_page is a list of objects, so where shall we keep the url.... in the first object I guess
    t_transcript['cache_url'] = url
    sys.stdout.write("### [CAHCING] t_current_transcript CACHING current_transcript with ref : %s   \r\n" % (t_transcript.get('cache_url')) )
    sys.stdout.flush()
    request.session['current_transcript'] = t_transcript

    return t_transcript

def t_transcript(request,transcriptId,url):

    #transcript metadata for this page ie the pageXML
#    sys.stdout.write("### IN t_transcript: %s   \r\n" % (url) )
#    sys.stdout.flush()

    # we will keep the current transcript in the session to decrease the number of calls to retirve and parse pageXML
    if "transcript" in request.session :
        if request.session.get('transcript').get('cache_url') == url :
            sys.stdout.write("### [HAVE CACHE] t_transcript HAS CACHED transcript for: %s \r\n" % (url) )
            sys.stdout.flush()
            return request.session['transcript']

    page_xml = t_transcript_xml(request,transcriptId,url)
    t_transcript=xmltodict.parse(page_xml)

    t_transcript['tsId'] = transcriptId

    #Cache this to reduce calls on subsequent lower level web-pages
    t_transcript['cache_url'] = url
    sys.stdout.write("### [CAHCING] t_transcript CACHING transcript with ref : %s   \r\n" % (t_transcript.get('cache_url')) )
    sys.stdout.flush()
    request.session['transcript'] = t_transcript

    return t_transcript

# TODO Decide what not to duplicate.
def t_transcript_xml(request,transcriptId,url):
    if "transcript_xml" in request.session: # TODO Remove this? The xml is only used when saving after which the cache must be refreshed anyway...
        if request.session.get('transcript_xml').get('cache_url') == url :
            return request.session['transcript_xml']

    headers = {'content-type': 'application/xml'}
    params = {}
    r = s.get(url, params=params, verify=False, headers=headers)

    if r.status_code != requests.codes.ok:
        return None
    return r.text

# Saves transcripts. TODO Statuses...
def t_save_transcript(request, transcript_xml, collId, docId, page):
    params = {"status": "NEW"}
    headers = {"content-type": "application/xml"}

    url = settings.TRP_URL+'collections/'+collId+'/'+str(docId)+'/'+str(page)+'/text'
    r = s.post(url, verify=False, headers=headers, params=params, data=transcript_xml)

    # Remove the old version from cache.
    del request.session['current_transcript']

    return None

def quote_value(m):
    return ':"'+m.group(1)+'",'

def quote_property(m):
    return '"'+m.group(1)+'":'

def t_metadata(custom_attr):

    #transcript metadata for this page ie the pageXML
    if not custom_attr:
        return None
    #CSS parsing (tinycss or cssutils) wasn't much cop so css => json by homemade regex (gulp!)

     #TODO rationalise steps
#    sys.stdout.write("### CSS: %s   \r\n" % (custom_attr) )
#    sys.stdout.flush()
    custom_json = re.sub(r' {', ': {', custom_attr)
#    sys.stdout.write("### JSON 0: %s   \r\n" % (custom_json) )
#    sys.stdout.flush()
    custom_json = re.sub(r'}', '},', custom_json)
#    sys.stdout.write("### JSON 1: %s   \r\n" % (custom_json) )
#    sys.stdout.flush()
    custom_json = re.sub(r':([^,{:]+);', quote_value, custom_json)
#    sys.stdout.write("### JSON 2: %s   \r\n" % (custom_json) )
#    sys.stdout.flush()
    custom_json = re.sub(r'([^,:{}\s]+):', quote_property, custom_json)
    custom_json = "{"+custom_json+"}"
#    sys.stdout.write("### JSON 3: %s   \r\n" % (custom_json) )
#    sys.stdout.flush()
    custom_json = re.sub(r',}', '}', custom_json)
#    sys.stdout.write("### JSON FINAL: %s   \r\n" % (custom_json) )
#    sys.stdout.flush()

    t_metadata = json.loads(custom_json)

    sys.stdout.write("### METADATA from CSS: %s   \r\n" % (t_metadata) )
    sys.stdout.flush()

    return t_metadata


def t_ingest_mets_xml(collId, mets_file):

    url = settings.TRP_URL+'collections/' + collId + '/createDocFromMets'
    files = {'mets':  mets_file}
    r = s.post(url, files=files, verify=False)

    if r.status_code != requests.codes.ok:
        sys.stdout.write("ERROR CODE: %s%% \r\n ERROR: %s%%" % (r.status_code, r.content) )
        sys.stdout.flush()
        return None
    # TODO What to do when we're successful?'

def t_ingest_mets_url(collId, mets_url):

    url = settings.TRP_URL+'collections/' + collId + '/createDocFromMetsUrl'
    params = {'fileName': mets_url}#, 'checkForDuplicateTitle': 'false'}# Perhaps this won't work even for testing! TODO Resolve!
    r = s.post(url, params=params, verify=False)

    sys.stdout.write("Ingesting document from METS XML file URL: %s%% \r\n" % (mets_url) )
    sys.stdout.flush()

    return r.status_code == requests.codes.ok

def t_create_collection(collection_name):
    url = settings.TRP_URL+'collections/createCollection'
    params = {'collName': collection_name}
    r = s.post(url, params=params, verify=False)

    sys.stdout.write("Response to create collection: %s  \r\n" % (r.status_code) )
    sys.stdout.flush()

    return r.status_code == requests.codes.ok

def t_jobs(status = ''):
    url = settings.TRP_URL+'jobs/list'
    params = {'status': status}
    r = s.get(url, params=params, verify=False)
    if r.status_code != requests.codes.ok:
        sys.stdout.write("Error getting jobs: %s \r\n ERROR: %s" % (r.status_code, r.content))
        sys.stdout.flush()
        return None
    jobs_json=r.text
    jobs = json.loads(jobs_json)
    return jobs

def t_job_count(status = ''):
    url = settings.TRP_URL+'jobs/count'
    params = {'status': status}
    r = s.get(url, params=params, verify=False)
    if r.status_code != requests.codes.ok:
        sys.stdout.write("Error getting job count: %s \r\n ERROR: %s" % (r.status_code, r.content))
        sys.stdout.flush()
        return None
    count=r.text
    return count

def t_kill_job(job_id):
    url = settings.TRP_URL + 'jobs/' + job_id + '/kill'
    r = s.post(url, verify=False)

    sys.stdout.write("Response to kill job: %s  \r\n" % (r.status_code) )
    sys.stdout.flush()

    return r.status_code == requests.codes.ok
