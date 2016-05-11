import requests
#import urllib2
import xmltodict
#from lxml import objectify
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
    #for no connection 
    if settings.OFFLINE:
	if settings.ADMIN_PASSWORD == pw:
		user_xml = settings.TEST_USER_XML
	else:
		return None
    #for connection 
    else:
    	r = s.post(url, params=params, verify=False, headers=headers)
    	if r.status_code != requests.codes.ok:
        	return None
    	user_xml = r.content

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

#    sys.stdout.write("Collections data: %s%%   \r\n" % (collections) )
#    sys.stdout.flush()
#    sys.stdout.write("User: %s%%   \r\n" % (request.user) )
#    sys.stdout.flush()

    return collections

def t_collection(collId):

    url = settings.TRP_URL+'collections/'+collId+'/list'
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
	   return None
	collection_json=r.content
    #may skip this and pass the json straight thru
    collection = json.loads(collection_json)

    for doc in collection:
	doc['key'] = doc['docId']
	doc['folder'] = 'true'
	#Infer enough to render a basic thumbnail grid... (will need images eventually)
	doc['children'] = [{'title': "Page "+str(x+1), 'key': str(doc['key'])+"_"+str(x+1), 'page': str(x+1)} for x in range(doc['nrOfPages'])]
    
  #  sys.stdout.write("Collection data: %s%%   \r\n" % (collection) )
   # sys.stdout.flush()
   # sys.stdout.write("User: %s%%   \r\n" % (request.user) )
   # sys.stdout.flush()

    return collection

# Shall we propose a streamlined json version of document metadata for pages where we want more than one doc displayed?
# or are we happy to proceed with derived page level metadata (see t_collection) regardless we use the big XML (or maybe big json)
# for 1 doc pages...
def t_document(collId, docId):

    url = settings.TRP_URL+'collections/'+collId+'/'+docId+'/fulldoc.xml'
    headers = {'content-type': 'application/xml'}
    params = {} 
    #for no connection:
    if settings.OFFLINE:
	doc_xml = settings.TEST_FULL_DOC_XML
    #for connection 
    else:
    	r = s.get(url, params=params, verify=False, headers=headers)
    	if r.status_code != requests.codes.ok:
        	return None
    	doc_xml = r.content

    sys.stdout.write("Document metadata XML: #%s%%   \r\n" % (doc_xml) )
    sys.stdout.flush()

    t_doc=xmltodict.parse(doc_xml)

#    sys.stdout.write("Document metadata for doc #%s%%: %s%%   \r\n" % (docId, t_doc) )
 #   sys.stdout.flush()

    return t_doc.get('trpDoc')
