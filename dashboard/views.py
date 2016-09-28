from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

#from django.contrib.auth.models import User

#from django.contrib.auth.decorators import login_required #for ajax reponses
from read.decorators import t_login_required, t_login_required_ajax

from read.services import *
from read.utils import t_log

from querystring_parser import parser

# Create your views here.

@t_login_required
def index(request):
    collections = t_collections(request)

    action_types = t_actions_info(request)
    if isinstance(action_types,HttpResponse): 
        return action_types

#    for collection in collections:
 #       t_log("Collection: %s " % collection)
 #       recent = t_collection_recent(request,collection.get("colId"))
 #       if isinstance(recent,HttpResponse): 
 #           return recent
#        t_log("RECENT for %s: %s" % (collection.get("colId"),recent))

#    t_log("### [VIEW] action_types: %s " % (request.session.get('action_types')) )
#We will use an ajax load into a jQuery.DataTable
    """
    #get all(?) actions for logged in user
    actions=t_list_actions(request)
    if isinstance(actions,HttpResponse): 
        return actions
    """
    return render(request, 'dashboard/homepage.html', {'collections': collections, 'action_types': action_types} )

@t_login_required_ajax #this version of the decorator will not redirect but pass the error back for the jscript to worry about
def actions_ajax(request,collId=None,docId=None):

    dt_params = parser.parse(request.GET.urlencode())
    length = int(dt_params.get('length')) if dt_params.get('length') else 5
    start = int(dt_params.get('start')) if dt_params.get('start') else 0
#    end = int(dt_params.get('end')) if dt_params.get('end') else ""

    start_date = str(dt_params.get('start_date')) if dt_params.get('start_date') else ""
    end_date = str(dt_params.get('end_date')) if dt_params.get('end_date') else ""

#    t_log("DT PARAMS: %s" % dt_params)

    #TODO use columns names rather than index
    params = {'start': start_date, 'end': end_date}
    # yuk at the moment
    if 'columns' in dt_params and dt_params.get('columns').get(5).get('search').get('value'):
        params['typeId'] = int(dt_params.get('columns').get(5).get('search').get('value')) 

    t_log("SENT PARAMS: %s" % params)

    actions=t_list_actions(request,params)
  
    #TODO pass back the error not the redirect and then process the error according to whether we have been called via ajax or not.... 
    if isinstance(actions,HttpResponse): 
        t_log("actions request has failed... %s" % actions)
        #For now this will do but there may be other reasons the transckribus request fails... (see comment above)
        return HttpResponse('Unauthorized', status=401)

    #data tables requires a specific set of table columns so we filter down the actions
    a_filter = ['time', 'colId', 'docId', 'pageId', 'userName', 'type']
    actions_filtered = []
    #I suspect some combination of filter/lambda etc could do this better...
    for action in actions:
        filtered_action = {}
        for field in a_filter : 
            filtered_action[field] = action.get(field) if action.get(field) else "n/a"
        actions_filtered.append(filtered_action)

    return JsonResponse({
            'recordsTotal': len(actions), 
            'recordsFiltered': len(actions), 
            'data': actions_filtered[start:(start+length)]
        },safe=False)
