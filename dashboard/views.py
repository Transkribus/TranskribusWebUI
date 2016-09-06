from django.shortcuts import render

#from django.contrib.auth.models import User
#from django.contrib.auth.decorators import login_required
from read.decorators import t_login_required


# Create your views here.

@t_login_required
def index(request):
    return render(request, 'dashboard/homepage.html' )
