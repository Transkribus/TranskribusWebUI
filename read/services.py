import requests
#workaround for insecure platform warnings...
#http://stackoverflow.com/questions/29099404/ssl-insecureplatform-error-when-using-requests-package
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
#TODO sudo pip install 'requests[security]'
#Possibly check for openssl-devel python-devel libffi-devel (yum)

import xmltodict
import dicttoxml
from django.http import HttpResponseRedirect
from django.conf import settings
import sys #remove after switching to t_log
from .utils import t_log, t_gen_request_id
import json
import re

s = requests.Session()

###############################################################
# Helper functions to do request and data handling grunt work
###############################################################


#set default headers for requests
def t_set_default_headers(headers):

    if 'clientId' not in headers:
        headers['clientId'] = str(2)
    if 'content-type' not in headers:
        headers['content-type'] = 'application/json'

    return headers

#Check session cache in case we don't need to bother the transkribus REST service at all
def t_check_cache(request,t_id, url, params=None) :

    # t_id and url as identifer for cached data, Store with key "cache_url" and in first element if data is a list
    if t_id in request.session :
        request_id = t_gen_request_id(url,params)
        if request_id in request.session[t_id] :
            t_log("HAVE CACHE: %s " % request_id)
            return request.session[t_id][request_id]

#               #Have data  keyed with t_id in session, get the *request_id*
#               if isinstance(request.session.get(t_id), list) :
#                   cache_rid = request.session.get(t_id)[0].get('request_id')
#               else :
#                   cache_rid = request.session.get(t_id).get('request_id')

        #Do the urls match too?
#        t_log("FOR T_ID: %s" % (t_id))
#        t_log("CACHE_RID: %s == RID : %s" % (cache_rid, request_id ))

 #       if cache_rid == request_id:
 #           t_log("HAVE CACHE: %s " % request_id)
 #           return request.session[t_id]

    #no data cached for this t_id/url pair, return None
    return None

#Set the session cache after a successful request to transkribus REST service
def t_set_cache_value(request,t_id,data,url,params=None) :

    #Use the t_id as identifer for cached data, Store the url with key "cache_url" (in first element if data is a list)
    request_id = t_gen_request_id(url,params)
    #if isinstance(data, list):
    #    if not data or len(data) == 0:
    #        data = [{'request_id' : request_id}]
    #    else :
    #        data[0]['request_id']=request_id
    #else :
    #    data['request_id']=request_id

    t_log("### [CAHCING] CACHING %s with request_id : %s" % (t_id,request_id) )
    if t_id not in request.session : request.session[t_id] = {}
    request.session[t_id][request_id] = data

#Make a request for data (possibly) to the transkribus REST service make
#use of helper functions and calling the appropriate data handler when done
def t_request(request,t_id,url,params=None,method=None,headers=None,handler_params=None):

    #Check for cached value and return that #TODO override this on some occaisions
    cache_data = t_check_cache(request, t_id, url, params)
    if cache_data :
        t_log("FROM CACHE: %s" % url)
        return cache_data

    #Add default headers to *possibly* already defined header data
    if not headers : headers = {}
    headers = t_set_default_headers(headers)

    #Default method is GET
    t_log("TRANSKRIBUS REQUEST: %s" % url)
    if method == 'POST' :
        r = s.post(url, params=params, verify=False, headers=headers)

    r = s.get(url, params=params, verify=False, headers=headers)

    #Check to see if we are still authenticated...
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code not in (401, 403):
            raise e

        #no access to requested collection... if we are indeed requesting a collection (which we usually are)
        #FAFF collId needs passed in via handler_params... we could extract from url??
        if e.response.status_code == 403 : # and handler_params is not None and "collId" in handler_params):
            m = re.match(r'^.*/rest/[^/]+/(-?\d+)/.*', url)
            collId = m.group(1)
            if collId :
                return HttpResponseRedirect("/library/collection_noaccess/"+str(collId))
        #otherwise you get logged out...
        return HttpResponseRedirect("/logout/?next={!s}".format(request.get_full_path()))

    # Pass transkribus response to handler (NB naming convention is t_[t_id]_handler(r, handler_params)
    # handler_params are for things that we might need to pass through this t_request to the handler
    data = eval("t_"+t_id+"_handler(r,handler_params)")
    #We store the data in the sesison cache
    t_set_cache_value(request,t_id,data,url,params)
    #And return it too
    return data

###########################################################################################
# Request/handler functions
# 1. Request specific bits of data from transkribus REST service
#    Set a url and t_id (ref dor data), set any specific headers or paramters, call request
# 2. Handle the response, do any datamungery before passing back to view
#    The handler must be named thus in order that t_request can find it: t_[t_id]_handler(r)
#    Recieves response from t_request, does stuff if necessary, returns data via 1. to view
#    TODO will probably need to pass through params in some cases to help mung the data
###########################################################################################


def t_register(request):

    url = settings.TRP_URL+'user/register'
    t_id = "user_data" # note we are using the same t_id as for t_login...
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
    return t_request(request,t_id,url,params,"POST",headers)

def t_login(user, pw):
    url = settings.TRP_URL+'auth/login'
    t_id = "user_data" # note we are using the same t_id as for t_register... This is OK because the data response will be the same... I think
    params = {'user': user, 'pw': pw}
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    #t_login is called from backend and doesn't have "request" so we don't call t_request or the handler
    r = s.post(url, params=params, verify=False, headers=headers)

    if r.status_code != requests.codes.ok:
        return None

    return xmltodict.parse(r.text).get('trpUserLogin')

def t_user_data_handler(r,params=None):
    return xmltodict.parse(r.text).get('trpUserLogin')

#refresh transkribus session (called by t_login_required decorator to test persistence/validity of transkribus session)
############## DEPRECATED ########################
def t_refresh():
    url = settings.TRP_URL+'auth/refresh'

    t_log("### [POST REQUEST] t_refresh will POST: %s" % (url) )

    r = s.post(url, verify=False)

    t_log("### t_refresh response STATUS_CODE: %s" % (r.status_code) )

    if r.status_code != requests.codes.ok:
        return None
    else:
        return True

#t_actions_info called to get lookup for action types for subsequent action list calls
def t_actions_info(request):
    #The url for the transkribus rest call
    url = settings.TRP_URL+'actions/info'
    #the id to use call the correct data handler and store the data
    t_id = "action_types"
    #Return the data from the request (via the handler, defined below)
    return t_request(request,t_id,url)
# Below is the simplest case imaginable
def t_action_types_handler(r,params=None):
    return json.loads(r.text)

#t_actions_count #NB this call is not yet available
def t_actions_count(request,params=None):
    url = settings.TRP_URL+'actions/count'
    t_id = "actions_count"
    return t_request(request,t_id,url,params)

def t_actions_count_handler(r,params=None):
    return json.loads(r.text)

#t_actions_list
def t_actions(request,params=None):
    url = settings.TRP_URL+'actions/list'
    t_id = "actions"

    return t_request(request,t_id,url,params)

def t_actions_handler(r,params=None):
    return json.loads(r.text)


#t_actions_info called to get lookup for action types for subsequent action list calls
def t_collection_recent(request,collId):
    url = settings.TRP_URL+'collections/'+str(collId)+'/list'
    t_id = "collection_recent"
    params = {'collId': collId}

    return t_request(request,t_id,url,"GET",params)

def t_collection_recent_handler(r,params=None):
    #t_log("collection_recent: %s " % r.text)
    return json.loads(r.text)

#t_collections_count
def t_collections_count(request,params=None):
    url = settings.TRP_URL+'collections/count'
    t_id = "collections_count"

    return t_request(request,t_id,url,params)

def t_collections_count_handler(r,params=None):
    return json.loads(r.text)

def t_collections(request,params=None):
    url = settings.TRP_URL+'collections/list'
    t_id = "collections"
    return t_request(request,t_id,url,params)

def t_collections_handler(r,params=None):
    t_collections = json.loads(r.text)
    t_log(str(t_collections))
    #use common param 'key' for ids (may yet drop...)
    for col in t_collections:
        col['key'] = col['colId']
    return t_collections

def t_collection(request,params):
    url = settings.TRP_URL+'collections/'+str(params.get('collId'))+'/list'
    t_id = "collection"
    return t_request(request,t_id,url,"GET",None,None,{"collId": params.get('collId')})
def t_collection_handler(r,params=None):
    collection_json=r.text
    return json.loads(r.text)

def t_collection_count(request,params):
    url = settings.TRP_URL+'collections/'+str(params.get('collId'))+'/count'
    t_id = "collection_count"

    return t_request(request,t_id,url,params)

def t_collection_count_handler(r,params=None):
    return json.loads(r.text)

#Alias t_documents > t_collection
def t_documents(request,collId):
    return t_collection(request,collId)

def t_documents_count(request,collId):
    return t_collection_count(request,collId)



def t_document(request, collId, docId, nrOfTranscripts=None):

    url = settings.TRP_URL+'collections/'+collId+'/'+str(docId)+'/fulldoc'
    t_id = "document"
    params = {}
    if not nrOfTranscripts is None:
        params['nrOfTranscripts'] = nrOfTranscripts
    return t_request(request,t_id,url)

def t_document_handler(r,params=None):
    t_doc = json.loads(r.text)
    pages = t_doc.get("pageList").get("pages")
    for x  in pages:
        x['key'] = x.get('pageNr') #I'm aware this will replacce the legitimate key....

    return t_doc

#returns a list of transcripts for a page, no page metadata...
def t_page(request,collId, docId, page):

    #list of transcripts for this page
    url = settings.TRP_URL+'collections/'+collId+'/'+str(docId)+'/'+str(page)+'/list'
    t_id = "page"
    return t_request(request,t_id,url)

def t_page_handler(r,params=None):

    t_page = json.loads(r.text)

    #TODO would prefer a pageId rather than "page" which is a the page number
    for x  in t_page:
        #key is used already for transcripts, however using key is handy for jquery things like fancy tree...
        x['key'] = x.get('tsId')

    return t_page

#returns the current transcript for a page
def t_current_transcript(request,collId, docId, page):

    #list of transcripts for this page
    url = settings.TRP_URL+'collections/'+collId+'/'+str(docId)+'/'+str(page)+'/curr'
    t_id="current_transcript"
    return t_request(request,t_id,url)

def t_current_transcript_handler(r,params=None):
    t_transcript = json.loads(r.text)
    t_transcript['key'] = t_transcript.get('tsId')
    return t_transcript

def t_transcript(request,transcriptId,url):

    t_id = "transcript"
    headers = {'content-type': 'application/xml'}
    params = {}
    return t_request(request,t_id,url,"GET",params,headers,{'transcriptId': transcriptId})

def t_transcript_handler(r,params=None):
    t_transcript=xmltodict.parse(r.text)
    t_transcript['tsId'] = params.get('transcriptId')
    return t_transcript

# t_metadata moved to utils

####################################
# Leave this for Matti
##################################

# Saves transcripts. TODO Statuses...
def t_save_transcript(request, transcript_xml, collId, docId, page):
    params = {"status": "NEW"}
    headers = {"content-type": "application/xml"}

    url = settings.TRP_URL+'collections/'+collId+'/'+str(docId)+'/'+str(page)+'/text'
    r = s.post(url, verify=False, headers=headers, params=params, data=transcript_xml)

    # Remove the old version from cache.
    del request.session['current_transcript']

    return None



def t_ingest_mets_xml(collId, mets_file):

    url = settings.TRP_URL+'collections/' + collId + '/createDocFromMets'
    files = {'mets':  mets_file}
    r = s.post(url, files=files, verify=False)

    if r.status_code != requests.codes.ok:
        sys.stdout.write("ERROR CODE: %s%% \r\n ERROR: %s%%" % (r.status_code, r.text) )
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
        sys.stdout.write("Error getting jobs: %s \r\n ERROR: %s" % (r.status_code, r.text))
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
        sys.stdout.write("Error getting job count: %s \r\n ERROR: %s" % (r.status_code, r.text))
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
