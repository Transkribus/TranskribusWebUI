# Synopsis of Transkribus library

This is a quick doc to assess how the current browsing of the transkribus document structure is traversed. The purpose is elucidation for other partners, but also to identify bottlenecks and other inefficincies.

## Approach

### Browse

In essence we have a view per level (ie collection, document, page, transcript, region, line, word) each with the metadata for that object and a list of child objects. A list of siblings is also used to build a navigation interface (up, next, prev), this can usually be obtained from cached data.

Views are probably a bit overloaded in some cases, but may be a useful illustration of what is needed to present a useful representation of a given part of the system to the user from a single page request. 

### A question to resolve. 

Whether to...

a. modify the transkribus web service to ensure delivery of the minimal '''necessary''' data with the smallest possible number of requests.
b. Delegate more of the request management to the client so we have user-triggered requests for data. This was the approach with TSX but that seemed to degrade performance, and would probably still require some modification of the web service anyway.

Below we describe each of the components, what they are for and provide profiling data for analysis.

## Extensions of django 

### library/backends.py/TranskribusBackend/authenticate

Class to override user authrntication, effectively out-sourcing it to the Transkribus web service. The default django user object is extended to store some additional user data from the web service. For django apps using this there is the potential here to combine the user of transkribus as the authentication authority *and* further extend the user object to include useful app related user data (eg crowd-sourcing rewards/badges etc)

### library/decorators.py/t_login_required

Version of django @login_required decorator and is applied to any view that requires authentication. This extends default functionality by adding a call to t_services.collections so that the list of permissable collections is available for any logged in user.

## Views

### library/collections

Displays the list of collections for the authenticated user. As collections are cached by t_login_required we just fetch that data from the cache and send to template.

### library/collection/{collId}

Displays the collection specified by {collId} and lists the documents *and* the page thumbnails, in that collection. 
Uses `services.t_collection` to collect `colList`, a list of documents (JSON) for given {collId}

 settings.TRP_URL/collections/collId/list

As there is currently no transkribus call that returns data for a single collection by ID (eg collection/{collId}). So we loop through the `collections` data (from cache) and pick out collection level metadata from there. The same could be achieved using the list of documents (ie pick first/random document data from `colList` which has collection data in it too). This may be a preferable approach, especially if there are lots of collections to loop through. A single call to retrieve collection level metadata seems to make more sense, but as we have a list of collections and a list of documents that have the necessary data in them, it may be a surplus request to the WS which we would want to avoid.

Then nav object is built from `collections` data.

Then we fetch thumbnails for each page in a document (overkill?). To do this loop through the documents (from `colList`) and for each document get the fulldoc data.

`settings.TRP_URL/collections/{collId}/{docId}/fulldoc?nrOfTranscripts=0`

This is done only to retrieve the imgFileName for thumbnails.

### library/document/{collId}/{docId}

Displays the document specified by {docId} and lists the pages in that document.

`services.t_collection` for list of docs for nav object
`services.t_document` for `fulldoc?nrOfTranscripts=-1`

### library/page/{collId}/{docId}/{pageNr}

Displays the page specified by {pageNr} and lists the transcripts for that page.

### library/transcript/{collId}/{docId}/{pageNr}/{transId}

Displays the transcript specified by {transId} and lists the regions of text for that transcript.

### library/region/{collId}/{docId}/{pageNr}/{transId}/{regionId}

Displays the region specified by {regionId} and lists the lines of text for that region.

### library/line/{collId}/{docId}/{pageNr}/{transId}/{regionId}/{lineId}

Displays the line specified by {lineId} and lists the words for that line.

### library/region/{collId}/{docId}/{pageNr}/{transId}/{regionId}/{lineId}/{wordId}

Displays the word specified by {wordId}.

### library/ingest_mets_url
### library/ingest_mets_xml
### library/collections_dropdown
### library/jobs_list
### library/jobs
### library/job_count
### library/changed_jobs_modal
### library/jobs_list_compact
### library/kill_job

