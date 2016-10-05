from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
#from django.contrib.auth.models import User

#from django.contrib.auth.decorators import login_required #for ajax reponses
from read.decorators import t_login_required, t_login_required_ajax

from read.services import *
from read.utils import t_log

from querystring_parser import parser


# dashboard/index is the dashboard for that logged in user. Will show actions, collections and metrics for that user
@t_login_required
def index(request):
    collections = t_collections(request)
    if isinstance(collections,HttpResponse): 
        return collections

    action_types = t_actions_info(request)
    if isinstance(action_types,HttpResponse): 
        return action_types

    return render(request, 'dashboard/homepage.html', {'collections': collections, 'action_types': action_types} )

# dashboard/{colID} is the dashboard for collection with ID colId. Will show actions, documents and metrics for that collection
@t_login_required
def d_collection(request,collId):
    documents = t_collection(request,collId)
    if isinstance(documents,HttpResponse): 
        return documents

    #Avoid this sort of nonsense if possible
    collection=None
    for col in documents[0].get("collectionList").get("colList"):
        if col.get("colId") == int(collId):
            collection = col
            break

    action_types = t_actions_info(request)
    if isinstance(action_types,HttpResponse): 
        return action_types
    return render(request, 'dashboard/collection.html', {'collection': collection, 'action_types': action_types, 'documents': documents} )

@t_login_required
def d_document(request,collId,docId):

    t_log("HERE")
    return HttpResponse("#TODO document level template...")

#######################################################
# handle common parameters for  paging (and filtering) data, the incoming params are expected to be as those for jquer.datatable.js
@t_login_required_ajax
def paged_data(request,list_name,collId=None,docId=None):

    #collect params from request into dict
    dt_params = parser.parse(request.GET.urlencode())
    t_log("DT PARAMS: %s" % dt_params)
    params = {}
    params['start'] = str(dt_params.get('start_date')) if dt_params.get('start_date') else None
    params['end'] = str(dt_params.get('end_date')) if dt_params.get('end_date') else None
    params['nValues'] = int(dt_params.get('length')) if dt_params.get('length') else read.settings.PAGE_SIZE_DEFAULT
    params['index'] = int(dt_params.get('start')) if dt_params.get('start') else 0
    params['sortColumn'] = int(dt_params.get('length')) if dt_params.get('length') else None
    params['sortDirection'] = int(dt_params.get('start')) if dt_params.get('start') else None

    if 'columns' in dt_params and list_name == "actions" and dt_params.get('columns').get(5).get('search').get('value'):
        params['typeId'] = int(dt_params.get('columns').get(5).get('search').get('value')) 

    if collId : params['collId'] = int(collId)

    t_log("SENT PARAMS: %s" % params)
    count=None
    if list_name != "actions":
        count = eval("t_"+list_name+"_count(request,params)")

    data = eval("t_"+list_name+"(request,params)")

    return (data,count)
   
#####################################################
# actions_data(request,collId=None,docId=None): Handles the request to 
# TS rest and any constraining params sent to it eg scope (user/collection/doc, dates, paging etc)
#@t_login_required_ajax #this version of the decorator will not redirect but pass the error back for the jscript to worry about
#def actions_data(request,collId=None,docId=None):
#
#    dt_params = parser.parse(request.GET.urlencode())
#
#    start_date = str(dt_params.get('start_date')) if dt_params.get('start_date') else ""
#    end_date = str(dt_params.get('end_date')) if dt_params.get('end_date') else ""
#    nValues = int(dt_params.get('length')) if dt_params.get('length') else 5
#    index = int(dt_params.get('start')) if dt_params.get('start') else 0
#
#    #TODO use columns names rather than index
#    params = {'start': start_date, 'end': end_date, 'collId' : collId, 'nValues': nValues, 'index': index}
#
#    # yuk at the moment
#    if 'columns' in dt_params and dt_params.get('columns').get(5).get('search').get('value'):
#        params['typeId'] = int(dt_params.get('columns').get(5).get('search').get('value')) 
#
#
#    actions=t_list_actions(request,params)
#  
#    return actions

@t_login_required_ajax
def actions_for_table_ajax(request,collId=None) :
#    actions = actions_data(request,collId)
    (actions,count) = paged_data(request,"actions",collId)

   #TODO pass back the error not the redirect and then process the error according to whether we have been called via ajax or not.... 
    if isinstance(actions,HttpResponse): 
        t_log("actions request has failed... %s" % actions)
        #For now this will do but there may be other reasons the transckribus request fails... (see comment above)
        return HttpResponse('Unauthorized', status=401)

    actions_filtered = filter_data(['time', 'colId', 'docId', 'pageId', 'userName', 'type'],actions)

    #When start/length come from TS we'll need to feed back from actions_data to here to datatables
    return JsonResponse({
            'recordsTotal': len(actions), 
            'recordsFiltered': len(actions), 
            'data': actions_filtered
        },safe=False)

@t_login_required_ajax
def actions_for_chart_ajax(request) :

#    actions = actions_data(request)
    actions = paged_data(request,"actions")

    #TODO When offset/limit params can be handled by TS we can move this up to actions_data
    dt_params = parser.parse(request.GET.urlencode())
    length = int(dt_params.get('length')) if dt_params.get('length') else 5
    start = int(dt_params.get('start')) if dt_params.get('start') else 0
    ##############################

   #TODO settle on a charting library and then present the data to that as appropriate

    return JsonResponse({},safe=False)

@t_login_required_ajax
def collections_for_table_ajax(request) :
    """
    dt_params = parser.parse(request.GET.urlencode())
    #TODO handle here when possible
    nValues = int(dt_params.get('length')) if dt_params.get('length') else 5
    index = int(dt_params.get('start')) if dt_params.get('start') else 0

    #TODO use columns names rather than index
    params = {'nValues': nValues, 'index': index}

    #TODO set sortColumn sort Direction
    t_log("SENT PARAMS: %s" % params)

    collections = t_collections(request,params)
    """
    (collections,count) = paged_data(request,"collections")

   #TODO pass back the error not the redirect and then process the error according to whether we have been called via ajax or not.... 
    if isinstance(collections,HttpResponse): 
        #For now this will do but there may be other reasons the transckribus request fails... (see comment above)
        return HttpResponse('Unauthorized', status=401)

    collections_filtered = filter_data(['colId', 'colName', 'description', 'role'],collections)

    #When start/length come from TS we'll need to feed back from actions_data to here to datatables
    return JsonResponse({
            'recordsTotal': count, 
            'recordsFiltered': count, 
            'data': collections_filtered
        },safe=False)


def filter_data(fields, data) : 

    #data tables requires a specific set of table columns so we filter down the actions
    filtered = []
    #I suspect some combination of filter/lambda etc could do this better...
    for datum in data:
        filtered_datum = {}
        for field in fields : 
            filtered_datum[field] = datum.get(field) if datum.get(field) else "n/a"
        filtered.append(filtered_datum)
    
    return filtered
