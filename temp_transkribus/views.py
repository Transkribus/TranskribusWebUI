from django.http import HttpResponse
from django.shortcuts import render

from .decorators import login_required

@login_required
def test(request):
    return HttpResponse("OK")
