from django.shortcuts import render

#from django.contrib.auth.models import User
#from django.contrib.auth.decorators import login_required
from read.decorators import t_login_required

from read.services import *

# Create your views here.

@t_login_required
def index(request):
    collections = request.session.get("collections");

    t_actions_info(request)
    sys.stdout.write("### [VIEW] action_types: %s   \r\n" % (request.session.get('action_types')) )

    #get all(?) actions for logged in user
    actions=t_list_actions(request)
    sys.stdout.write("### [VIEW] actions: %s   \r\n" % (request.session.get('actions')) )

    return render(request, 'dashboard/homepage.html', {'collections': collections} )
