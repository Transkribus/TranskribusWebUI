from django.shortcuts import render

from read.decorators import t_login_required


# Create your views here.

#@t_login_required
def index(request):
    return render(request, 'search/homepage.html' )
