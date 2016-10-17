from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
#from django.contrib.auth.models import User
import datetime
import dateutil.parser

#from django.contrib.auth.decorators import login_required #for ajax reponses
from read.decorators import t_login_required, t_login_required_ajax
import read.settings
from read.services import *
from read.utils import t_log

from querystring_parser import parser

#######################
# Views for dashboard
######################

# index : overall view for a given user
#		- activities table for that user
#		- collections associated with that user
#		- charts:
#			- activity chart for that user (line, activities by time, activities==login/save/access/change)
#			- status for aggregated pages in *all* users' collections (pie, new/inprogress/done/final)
#			- bar... ?

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

# dashboard/{colID}
# d_collection : overall view for a given collection
#		-tables
#			- activities table for that collection
#			- documents belonging to that collection
#			- users associated with that collection
#		- charts:
#			- activity chart for that collection (line, activities by time, activities==login/save/access/change)
#			- status for aggregated pages in collection (pie, new/inprogress/done/final)
#			- bar for top 5 users by activity

@t_login_required
def d_collection(request,collId):
    documents = t_collection(request,{'collId': collId})
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
    return render(request, 'dashboard/collection.html', {'collection': collection, 'action_types': action_types, 'documents': documents} ) #nb documents only used to display length...

# dashboard/{colID}/{docId}
# d_collection : overall view for a given collection
#		-tables
#			- activities table for that document
#			- pages belonging to that document as thumbs
#			- users associated with that document (?collection)
#		- charts:
#			- activity chart for that document (line, activities by time, activities==login/save/access/change)
#			- status for aggregated pages in document (pie, new/inprogress/done/final)
#			- bar for top 5 users by activity


@t_login_required
def d_document(request,collId,docId):

    fulldoc = t_fulldoc(request,{'collId': collId, 'docId': docId})
    if isinstance(fulldoc,HttpResponse):
        return fulldoc

    action_types = t_actions_info(request)
    if isinstance(action_types,HttpResponse):
        return action_types
    return render(request, 'dashboard/document.html', {'document': fulldoc.get('md'), 
							'action_types': action_types, 
							'pages': fulldoc.get('pageList').get('pages')

	} )

##########
# Helpers
##########

# paged_data: 
#	- Handle common parameters for paging and filtering data
#	- Calls read.services.t_[list_name] requests
#	- Some params must be passed in params (eg ids from url, typeId from calling function)
#	- Some params are set directly from REQUEST, but can be overridden by params (eg nValues)

@t_login_required_ajax
def paged_data(request,list_name,params=None):#collId=None,docId=None):

    #collect params from request into dict
    dt_params = parser.parse(request.GET.urlencode())
#    t_log("DT PARAMS: %s" % dt_params)
    if params is None: params = {}
    params['start'] = str(dt_params.get('start_date')) if dt_params.get('start_date') else None 
    params['end'] = str(dt_params.get('end_date')) if dt_params.get('end_date') else None
    params['index'] = int(dt_params.get('start')) if dt_params.get('start') else 0

    #NB dataTables uses length, transkribus nValues
    if 'nValues' not in params :
        params['nValues'] = int(dt_params.get('length')) if dt_params.get('length') else read.settings.PAGE_SIZE_DEFAULT

#    params['sortColumn'] = int(dt_params.get('length')) if dt_params.get('length') else None
#    params['sortDirection'] = int(dt_params.get('start')) if dt_params.get('start') else None

    #this is the way that datatables passes things in when redrawing... may do something simpler for filtering if possible!!
    if 'columns' in dt_params and list_name == "actions" and dt_params.get('columns').get(5).get('search').get('value'):
        params['typeId'] = int(dt_params.get('columns').get(5).get('search').get('value'))

    #Get data
    t_log("SENT PARAMS: %s" % params)
    data = eval("t_"+list_name+"(request,params)")

    #Get count
    count=None
    #stupid awkward special cases don't have count calls (yet)
    if list_name not in ["actions", "fulldoc"]:    
        count = eval("t_"+list_name+"_count(request,params)")
    #In some cases we can derive count from data (eg pages from fulldoc)
    if list_name == "fulldoc" : #as we have the full page list in full doc for now we can use it for a recordsTotal
        count = data.get('md').get('nrOfPages')
    
    return (data,count)

######### Data views #########
# These return json for ajax
# pass back count as recordsTotal/recordsFiltered (would be nice to get real values for these)
# data as data, this is designed for consumption by dataTables.js

# NB scope for reducing repeated code ahoy...
# ... here goes


@t_login_required_ajax
def table_ajax(request,list_name,collId=None,docId=None) :

    t_list_name=list_name

    ####### EXCEPTION #######
    # list_name is pages we extract this from fulldoc
    if list_name == 'pages' : t_list_name = "fulldoc"
    #########################

    (data,count) = paged_data(request,t_list_name,{'collId': collId, 'docId': docId})

    ####### EXCEPTION #######
    # no actions/count
    if list_name == 'actions' : count = len(data)
    ###########################

   #TODO pass back the error not the redirect and then process the error according to whether we have been called via ajax or not....
    if isinstance(data,HttpResponse):
        t_log("data request has failed... %s" % data)
        #For now this will do but there may be other reasons the transckribus request fails... (see comment above)
        return HttpResponse('Unauthorized', status=401)

    filters = {
		'actions' : ['time', 'colId', 'colName', 'docId', 'docName', 'pageId', 'pageNr', 'userName', 'type'],
		'collections' : ['colId', 'colName', 'description', 'role'],
		'documents' : ['docId','title','author','uploadTimestamp','uploader','nrOfPages','language','status'],
#		'pages' : ['pageId','pageNr','thumbUrl','status', 'nrOfTranscripts'], #tables
		'pages' : ['pageId','pageNr','imgFileName','thumbUrl'], #thumbnails
              }

    ####### EXCEPTION #######
    # Do the extraction of pages from fulldoc
    if list_name == 'pages' :
        data = data.get('pageList').get('pages')
    #########################

    data_filtered = filter_data(filters.get(list_name),data)

    ####### EXCEPTION #######
    # We cannot request a paged list of pages by docid, so we must manage paging here
    if list_name == 'pages' :
        dt_params = parser.parse(request.GET.urlencode())
        nValues = int(dt_params.get('length')) if dt_params.get('length') else int(read.settings.PAGE_SIZE_DEFAULT)
        index = int(dt_params.get('start')) if dt_params.get('start') else 0
        #lame paging for pages for now...
        data_filtered = data_filtered[index:(index+nValues)]
    ##########################

    return JsonResponse({
            'recordsTotal': count,
            'recordsFiltered': count,
            'data': data_filtered
        },safe=False)
"""
# actions_for_table_ajax:
#	- return actions to be displayed in table

@t_login_required_ajax
def actions_for_table_ajax(request,collId=None,docId=None) :
    
    (actions,count) = paged_data(request,"actions",{'collId': collId})

   #TODO pass back the error not the redirect and then process the error according to whether we have been called via ajax or not....
    if isinstance(actions,HttpResponse):
        t_log("actions request has failed... %s" % actions)
        #For now this will do but there may be other reasons the transckribus request fails... (see comment above)
        return HttpResponse('Unauthorized', status=401)

    actions_filtered = filter_data(['time', 'colId', 'colName', 'docId', 'docName', 'pageId', 'pageNr', 'userName', 'type'],actions)

    #When start/length come from TS we'll need to feed back from actions_data to here to datatables
    return JsonResponse({
            'recordsTotal': len(actions),
            'recordsFiltered': len(actions),
            'data': actions_filtered
        },safe=False)

# collections_for_table_ajax:
#	- return collections to be displayed in table

@t_login_required_ajax
def collections_for_table_ajax(request) :
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

# documents_for_table_ajax:
#	- return collections to be displayed in table

@t_login_required_ajax
def documents_for_table_ajax(request,collId) :
    (documents,count) = paged_data(request,"documents",{'collId': collId})

   #TODO pass back the error not the redirect and then process the error according to whether we have been called via ajax or not....
    if isinstance(documents,HttpResponse):
        #For now this will do but there may be other reasons the transckribus request fails... (see comment above)
        return HttpResponse('Unauthorized', status=401)

    documents_filtered = filter_data(['docId','title','author','uploadTimestamp','uploader','nrOfPages','language','status'],documents)

    #When start/length come from TS we'll need to feed back from actions_data to here to datatables
    return JsonResponse({
            'recordsTotal': count,
            'recordsFiltered': count,
            'data': documents_filtered
        },safe=False)

# pages_for_table_ajax:
#	- return pages to be displayed in table
# NB not currently used in view (see thumbnails_for_ajax)

@t_login_required_ajax
def pages_for_table_ajax(request,collId,docId) :
    (fulldoc,count) = paged_data(request,"fulldoc",{'collId': collId,'docId': docId})

    #TODO pass back the error not the redirect and then process the error according to whether we have been called via ajax or not....
    if isinstance(fulldoc,HttpResponse):
        #For now this will do but there may be other reasons the transckribus request fails... (see comment above)
        return HttpResponse('Unauthorized', status=401)
     
    pages_filtered = filter_data(['pageId','pageNr','thumbUrl','status', 'nrOfTranscripts'],fulldoc.get('pageList').get('pages'))

    #TODO UIBK We cannot get a paged list of pages by docid, so have to load full list of pages here :(
    dt_params = parser.parse(request.GET.urlencode())
    nValues = int(dt_params.get('length')) if dt_params.get('length') else int(read.settings.PAGE_SIZE_DEFAULT)
    index = int(dt_params.get('start')) if dt_params.get('start') else 0
    ####################################################################################################

    #When start/length come from TS we'll need to feed back from actions_data to here to datatables
    return JsonResponse({
            'recordsTotal': fulldoc.get('md').get('nrOfPages'),
            'recordsFiltered': fulldoc.get('md').get('nrOfPages'),
            'data': pages_filtered[index:(index+nValues)]
        },safe=False)


@t_login_required_ajax
def thumbnails_ajax(request,collId,docId) :
    (fulldoc,count) = paged_data(request,"fulldoc",{'collId': collId,'docId': docId})

    #TODO pass back the error not the redirect and then process the error according to whether we have been called via ajax or not....
    if isinstance(fulldoc,HttpResponse):
        #For now this will do but there may be other reasons the transckribus request fails... (see comment above)
        return HttpResponse('Unauthorized', status=401)
     
    pages_filtered = filter_data(['pageId','pageNr','imgFileName','thumbUrl'],fulldoc.get('pageList').get('pages'))

    #TODO UIBK We cannot get a paged list of pages by docid, so have to load full list of pages here :(
    dt_params = parser.parse(request.GET.urlencode())
    nValues = int(dt_params.get('length')) if dt_params.get('length') else int(read.settings.PAGE_SIZE_DEFAULT)
    index = int(dt_params.get('start')) if dt_params.get('start') else 0
    ####################################################################################################

    #When start/length come from TS... until then:
    return JsonResponse({
            'recordsFiltered': count,
            'recordsTotal': count,
            'data': pages_filtered[index:(index+nValues)]
        },safe=False)

"""

@t_login_required_ajax
def actions_for_chart_ajax(request,collId=None) :

    # When requesting data for chart we do not want this paged so nValues=-1
    # Other constraint params can be used (ids, dates etc)
    (actions,count) = paged_data(request,"actions",{'nValues':-1, 'collId': collId})


    #TODO When offset/limit params can be handled by TS we can move this up to actions_data
#    dt_params = parser.parse(request.GET.urlencode())
#    length = int(dt_params.get('length')) if dt_params.get('length') else 5
#    start = int(dt_params.get('start')) if dt_params.get('start') else 0
    ##############################
    action_info = {
		  1 : {'label' : 'Save' ,'colour': 'rgba(255,99,132,1)'},
		  2 : {'label' : 'Login', 'colour': 'rgba(54, 162, 235, 1)'},
		  3 : {'label' : 'Status change' , 'colour' :'rgba(255, 206, 86, 1)'},
		  4 : {'label' : 'Access document', 'colour' : 'rgba(75, 192, 192, 1)'},
		}

    days = {}
    types = {}
    sd = {}
    for action in actions:
        d = dateutil.parser.parse(action.get("time")).date()
        type_id = action.get("typeId")
        days[d] = days[d]+1 if d in days else 0
        if type_id not in types : types[type_id] = {}
        types[type_id][d] = types[type_id][d]+1 if d in types[type_id] else 0
        #zero  value for other types on that day so our datasets are of equal length...
        for x in action_info.keys() :
            if x not in types : types[x] = {}
            if x != type_id and d not in types.get(x) :
                types[x][d]=0


    datasets = []
    for x in types:
       datasets.append({
			'data': list(types.get(x).values()), 
			'label': action_info.get(x).get('label'), 
			'fill': False, 
			'borderColor': action_info.get(x).get('colour'),
			'backgroundColor': action_info.get(x).get('colour'),
			'pointRadius': 0
			})

    return JsonResponse({
	    'labels': sorted(list(days.keys())),
	    'datasets' : datasets
	},safe=False)

    '''
	    'labels': ["January", "February", "March", "April", "May", "June", "July"],
	    'datasets': [
		{
		    'label': "My First dataset",
		    'fill': 'false',
		    'lineTension': 0.1,
		    'backgroundColor': "rgba(75,192,192,0.4)",
		    'borderColor': "rgba(75,192,192,1)",
		    'borderCapStyle': 'butt',
		    'borderDash': [],
		    'borderDashOffset': 0.0,
		    'borderJoinStyle': 'miter',
		    'pointBorderColor': "rgba(75,192,192,1)",
		    'pointBackgroundColor': "#fff",
		    'pointBorderWidth': 1,
		    'pointHoverRadius': 5,
		    'pointHoverBackgroundColor': "rgba(75,192,192,1)",
		    'pointHoverBorderColor': "rgba(220,220,220,1)",
		    'pointHoverBorderWidth': 2,
		    'pointRadius': 1,
		    'pointHitRadius': 10,
		    'data': [65, 59, 80, 81, 56, 55, 40],
		    'spanGaps': 'false',
		}
	    ]
      '''



def filter_data(fields, data) :

    #data tables requires a specific set of table columns so we filter down the actions
    filtered = []
    #I suspect some combination of filter/lambda etc could do this better...
    for datum in data:
        filtered_datum = {}
        for field in fields :
            filtered_datum[field] = datum.get(field) if datum.get(field) else "n/a" #TODO this will n/a 0!!
        filtered.append(filtered_datum)

    return filtered
