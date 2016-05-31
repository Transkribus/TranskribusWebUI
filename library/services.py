import requests
#import urllib2
import xmltodict
#from lxml import objectify
from django.http import HttpResponseRedirect
from django.conf import settings
import sys
import json

s = requests.Session()

def t_login(user, pw):
    url = settings.TRP_URL+'auth/login' 
    sys.stdout.write("### IN t_login: %s%%   \r\n" % (url) )
    sys.stdout.flush()

    params = {'user': user, 'pw': pw}
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    #TODO check wadl and use json (it is throwing a 415 at if just switching in the content-type)
#    headers = {'content-type': 'application/json'}

    #for no connection 
    if settings.OFFLINE:
	if settings.ADMIN_PASSWORD == pw:
		user_xml = settings.TEST_USER_XML
	else:
		return None
    #for connection 
    else:
    	r = s.post(url, params=params, verify=False, headers=headers)
        sys.stdout.write("AUTH RESPONSE OBJ: %s  \r\n" % (r.status_code) )
        sys.stdout.flush()
    	if r.status_code != requests.codes.ok:
        	return None
    	user_xml = r.content

#    sys.stdout.write("RETURN FROM JSON AUTH REQ: %s  \r\n" % (user_xml) )
#    sys.stdout.flush()

    t_user=xmltodict.parse(user_xml)

#    sys.stdout.write("trpUserLogin: %s%%   \r\n" % (t_user['trpUserLogin']) )
#    sys.stdout.flush()

    return t_user['trpUserLogin']

#refresh transkribus session (called by t_login_required decorator to test persistence/validity of transkribus session)
def t_refresh():
    url = settings.TRP_URL+'auth/refresh' 
    sys.stdout.write("### IN t_refresh: %s%%   \r\n" % (url) )
    sys.stdout.flush()


    r = s.post(url, verify=False)

    sys.stdout.write("STATUS CODE: %s%%   \r\n" % (r.status_code) )
    sys.stdout.flush()

    if r.status_code != requests.codes.ok:
        return None
    else:
	return True

def t_collections():

    url = settings.TRP_URL+'collections/list'

    sys.stdout.write("### IN t_collectionssss: %s%%   \r\n" % (url) )
    sys.stdout.flush()

    headers = {'content-type': 'application/json'}
    params = {} 
    #for no connection:
    if settings.OFFLINE:
	collections_json = settings.TEST_COLLECTIONS_JSON
    #for connection 
    else:
    	r = s.get(url, params=params, verify=False, headers=headers)
	if r.status_code != requests.codes.ok:
	   sys.stdout.write("ERROR CODE: %s%% \r\n ERROR: %s%%" % (r.status_code, r.content) )
	   sys.stdout.flush()
	   return None
	collections_json=r.content

    collections = json.loads(collections_json) 

    #use common param 'key' for ids
    for col in collections:
	col['key'] = col['colId']

#    sys.stdout.write("Collections data: %s%%   \r\n" % (collections) )
#    sys.stdout.flush()
#    sys.stdout.write("User: %s%%   \r\n" % (request.user) )
#    sys.stdout.flush()

    return collections

def t_collection(collId):

    url = settings.TRP_URL+'collections/'+unicode(collId)+'/list'
    sys.stdout.write("### IN t_collectionnnn: %s%%   \r\n" % (url) )
    sys.stdout.flush()

    headers = {'content-type': 'application/json'}
    params = {} 
    #for no connection:
    if settings.OFFLINE:
	collection_json = settings.TEST_COLLECTION_JSON
    #for connection 
    else:
    	r = s.get(url, params=params, verify=False, headers=headers)
	if r.status_code != requests.codes.ok:
	   sys.stdout.write("ERROR CODE: %s%% \r\n ERROR: %s%%" % (r.status_code, r.content) )
	   sys.stdout.flush()
	   return r.status_code
	collection_json=r.content

    collection = json.loads(collection_json)

    for doc in collection:
        doc['collId'] = collId
	doc['key'] = doc['docId']
	doc['folder'] = 'true'
	#fetch full document data with no transcripts for pages
	fulldoc  = t_document(collId, doc['docId'], 0)
	doc['children'] = fulldoc.get('pageList').get("pages")
        for x in doc['children']:
	   x['title']=x['imgFileName'] 
	   x['collId']=collId

    return collection

def t_document(collId, docId, nrOfTranscripts=None):

    url = settings.TRP_URL+'collections/'+collId+'/'+unicode(docId)+'/fulldoc'
    headers = {'content-type': 'application/xml'}
    params = {}
    if not nrOfTranscripts is None:
	params['nrOfTranscripts'] = nrOfTranscripts
	
    #for no connection:
    if settings.OFFLINE:
	doc_xml = settings.TEST_FULL_DOC_XML
	doc_json = settings.TEST_FULL_DOC_JSON
    #for connection 
    else:
    	r = s.get(url, params=params, verify=False, headers=headers)
    	if r.status_code != requests.codes.ok:
        	return None
#    	doc_xml = r.content
    	doc_json = r.content

    t_doc = json.loads(doc_json)
    pages = t_doc.get("pageList").get("pages")
    for x  in pages:
	x['key'] = x.get('pageNr') #I'm aware this will replacce the legitimate key....

    return t_doc

def t_page(collId, docId, page, nrOfTranscripts=None):

    #TODO get page metadata 
#    url = settings.TRP_URL+'collections/'+collId+'/'+unicode(docId)+'/'+unicode(page) #??

    #list of transcripts for this page
    url = settings.TRP_URL+'collections/'+collId+'/'+unicode(docId)+'/'+unicode(page)+'/list'
    sys.stdout.write("### IN t_page: %s%%   \r\n" % (url) )
    sys.stdout.flush()

    headers = {'content-type': 'application/json'}
    params = {}
	
    #for no connection:
    if settings.OFFLINE:
	page_json = settings.TEST_PAGE_JSON
    #for connection 
    else:
    	r = s.get(url, params=params, verify=False, headers=headers)
    	if r.status_code != requests.codes.ok:
        	return None
    	page_json = r.content

    t_page = json.loads(page_json)

    #TODO would prefer a pageId rather than "page" which is a the page number
    for x  in t_page:
	#key is used already for transcripts, however using key is handy for jquery things like fancy tree... maybe some neat namespace trickis called for
	x['key'] = x.get('tsId')
    return t_page

def t_transcript(transcriptId,url):

    #transcript metadata for this page ie the pageXML
    sys.stdout.write("### IN t_transcript: %s   \r\n" % (url) )
    sys.stdout.flush()

    headers = {'content-type': 'application/xml'}
    params = {}
	
    #for no connection:
    if settings.OFFLINE:
	page_json = settings.TEST_TRANSCRIPT
    #for connection 
    else:
    	r = s.get(url, params=params, verify=False, headers=headers)
    	if r.status_code != requests.codes.ok:
            return None
    	page_xml = r.content #this just returns the pageXML...

    t_transcript=xmltodict.parse(page_xml)
    t_transcript.tsId = transcriptId

    return t_transcript

def t_ingest_mets_url(collId, mets_url):
    
    url = settings.TRP_URL+'collections/' + collId + '/createDocFromMetsUrl'
    params = {'fileName': mets_url}#, 'checkForDuplicateTitle': 'false'}# Perhaps this won't work even for testing! TODO Resolve!
    r = s.post(url, params=params, verify=False)
    
    sys.stdout.write("Ingesting document from METS XML file: %s%%   \r\n" % (mets_url) )
    sys.stdout.flush()
    
    if r.status_code != requests.codes.ok:
        sys.stdout.write("ERROR CODE: %s%% \r\n ERROR: %s%%" % (r.status_code, r.content) )
        sys.stdout.flush()
        return None
    # TODO What to do when we're successful?'
