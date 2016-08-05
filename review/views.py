#imports of python modules
import json
import sys
import re
import random

#Imports of django modules
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect 
from django.utils import translation
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

#Imports pf read modules
from read.decorators import t_login_required
from read.services import *
#t_collection, t_register,

#Imports from app (library)
import library.settings
import library.navigation# TODO Fix this import!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from library.forms import RegisterForm, IngestMetsUrlForm, MetsFileForm

#from profiler import profile #profile is a decorator, but things get circular if I include it in decorators.py so...

# TODO Crop. It's broken now and should be reused anyway.
# TODO Consider overlap with region view etc.
@t_login_required
def proofread(request, collId, docId, page, transcriptId, regionId):
    # We need to be able to target a transcript (as mentioned elsewhere)
    # here there is no need for anything over than the pageXML really
    # we could get one transcript from ...{page}/curr, but for completeness would 
    # rather use transciptId to target a particular transcript
    transcripts = t_page(request,collId, docId, page) 

    #To get the page image url we need the full_doc (we hope it's been cached)
    full_doc = t_document(request, collId, docId, -1)
    index = int(page)-1
    # and then extract the correct page from full_doc (may be better from a  separate page data request??)
    pagedata = full_doc.get('pageList').get('pages')[index]
    
    sys.stdout.write("############# PAGEDATA: %s\r\n" % pagedata )
    #we are only using the transcripts to get the pageXML for a particular transcript...
    pageXML_url = None;
    for x in transcripts:
        if int(x.get("tsId")) == int(transcriptId):
            pageXML_url = x.get("url")
            break
 
    if pageXML_url:
        transcript = t_transcript(request,transcriptId,pageXML_url)

    # TODO ...
    #sys.stdout.write("############# XML: %s\r\n" % transcript )
    #sys.stdout.flush()
    
    
    regions=transcript.get("PcGts").get("Page").get("TextRegion");
    if isinstance(regions, dict):
        regions = [regions]

    for x in regions:
        x['key'] = x.get("@id")
        if(unicode(regionId) == unicode(x.get("@id"))):
            region = x

    if(region.get("Coords")):
        region['crop_str'] = crop(region.get("Coords").get("@points"))

    nav = library.navigation.up_next_prev("region",regionId,regions,[collId,docId,page,transcriptId])

#    sys.stdout.write("REGION: %s\r\n" % (region) )
#    sys.stdout.flush()

    lines = region.get("TextLine")
    if isinstance(lines, dict):
        lines = [lines]
    #parse metadata
    if lines:
        for x in lines:
            x['md'] = t_metadata(x.get("@custom"))
            x['crop_str'] = crop(x.get("Coords").get("@points"))
            x['id'] = x.get("@id")

    return render(request, 'review/proofread.html', {
        'region' : region,
        'lines' : lines,
        'up': nav['up'],
        'next': nav['next'],
        'prev': nav['prev'],
        'collId': collId,
        'docId': docId,
        'pageId': page, #NB actually the number for now
        'transcriptId': transcriptId,
        'imageUrl' : pagedata.get("url"),
        })
        
# TODO Merge this as well when it's working as intended.
@t_login_required
def pr_line(request, collId, docId, page, transcriptId, regionId, lineId):
    # We need to be able to target a transcript (as mentioned elsewhere)
    # here there is no need for anything over than the pageXML really
    # we could get one transcript from ...{page}/curr, but for completeness would 
    # rather use transciptId to target a particular transcript
    transcripts = t_page(request,collId, docId, page) 
    #we are only using the transcripts to get the pageXML for a particular
    pageXML_url = None;
    for x in transcripts:
        if int(x.get("tsId")) == int(transcriptId):
            pageXML_url = x.get("url")
            break
 
    if pageXML_url:
        transcript = t_transcript(request,transcriptId,pageXML_url)

    #To get the page image url we need the full_doc (we hope it's been cached)
    full_doc = t_document(request, collId, docId, -1)
    index = int(page)-1
    # and then extract the correct page from full_doc (may be better from a  separate page data request??)
    pagedata = full_doc.get('pageList').get('pages')[index]

    #This now officially bonkers....
    regions=transcript.get("PcGts").get("Page").get("TextRegion");
    if isinstance(regions, dict):
        regions = [regions]

    for x in regions:
        if(unicode(regionId) == unicode(x.get("@id"))):
            region = x

    lines=region.get("TextLine");

    if isinstance(lines, dict):
        lines = [lines]


    for x in lines:
        x['key'] = x.get("@id")
        if(unicode(lineId) == unicode(x.get("@id"))):
            line = x

    if(line.get("Coords")):
        line['crop_str'] = crop(line.get("Coords").get("@points"))

    nav = library.navigation.up_next_prev("line",lineId,lines,[collId,docId,page,transcriptId,regionId])

#    sys.stdout.write("REGION: %s\r\n" % (region) )
#    sys.stdout.flush()

    words = line.get("Word")
    if isinstance(words, dict):
        words = [words]
    #parse metadata
    if words:
        for x in words:
            x['md'] = t_metadata(x.get("@custom"))

    return render(request, 'review/pr_line.html', {
        'line' : line,
        'words' : words,
        'up': nav['up'],
        'next': nav['next'],
        'prev': nav['prev'],
        'collId': collId,
        'docId': docId,
        'pageId': page, #NB actually the number for now
        'transcriptId': transcriptId,
        'regionId': regionId,
        'lineId': lineId,
        'imageUrl' : pagedata.get("url"),
        })
    
def crop(coords):
    sys.stdout.write("############# COORDS: %s\r\n" % coords )
   # coords = region.get("Coords").get("@points")
    points = coords.split()    
    xmin=ymin=99999999 #TODO durh...
    xmax=ymax=0
    points = [map(int, point.split(',')) for point in points]
    #boo two loops! but I like this one above here...
    #TODO woops... I actually need this to x-off y-off widt and height...
    for point in points:
        if point[1] > ymax : ymax=point[1]
        if point[1] < ymin : ymin=point[1]
        if point[0] > xmax : xmax=point[0]
        if point[0] < xmin : xmin=point[0]
        crop = {'x':xmin, 'y':ymin, 'w':(xmax-xmin), 'h': (ymax-ymin)}
        crop_str = str(crop.get('x'))+"x"+str(crop.get('y'))+"x"+str(crop.get('w'))+"x"+str(crop.get('h'))

    return crop_str
#    sys.stdout.write("POINTS: %s\r\n" % (points) )
#    sys.stdout.write("CROP: %s\r\n" % (crop) )

# TODO Merge this as well when it's working as intended.
@t_login_required
def pr_line(request, collId, docId, page, transcriptId, regionId, lineId):
    # We need to be able to target a transcript (as mentioned elsewhere)
    # here there is no need for anything over than the pageXML really
    # we could get one transcript from ...{page}/curr, but for completeness would 
    # rather use transciptId to target a particular transcript
    transcripts = services.t_page(request,collId, docId, page) 
    #we are only using the transcripts to get the pageXML for a particular
    pageXML_url = None;
    for x in transcripts:
        if int(x.get("tsId")) == int(transcriptId):
            pageXML_url = x.get("url")
            break
 
    if pageXML_url:
        transcript = services.t_transcript(request,transcriptId,pageXML_url)

    #To get the page image url we need the full_doc (we hope it's been cached)
    full_doc = services.t_document(request, collId, docId, -1)
    index = int(page)-1
    # and then extract the correct page from full_doc (may be better from a  separate page data request??)
    pagedata = full_doc.get('pageList').get('pages')[index]

    #This now officially bonkers....
    regions=transcript.get("PcGts").get("Page").get("TextRegion");
    if isinstance(regions, dict):
        regions = [regions]

    for x in regions:
        if(unicode(regionId) == unicode(x.get("@id"))):
            region = x

    lines=region.get("TextLine");

    if isinstance(lines, dict):
        lines = [lines]


    for x in lines:
        x['key'] = x.get("@id")
        if(unicode(lineId) == unicode(x.get("@id"))):
            line = x

    if(line.get("Coords")):
        line['crop_str'] = crop(line.get("Coords").get("@points"))

    nav = library.navigation.up_next_prev("line",lineId,lines,[collId,docId,page,transcriptId,regionId])

#    sys.stdout.write("REGION: %s\r\n" % (region) )
#    sys.stdout.flush()

    words = line.get("Word")
    if isinstance(words, dict):
        words = [words]
    #parse metadata
    if words:
        for x in words:
            x['md'] = services.t_metadata(x.get("@custom"))

    return render(request, 'review/pr_line.html', {
        'line' : line,
        'words' : words,
        'up': nav['up'],
        'next': nav['next'],
        'prev': nav['prev'],
        'collId': collId,
        'docId': docId,
        'pageId': page, #NB actually the number for now
        'transcriptId': transcriptId,
        'regionId': regionId,
        'lineId': lineId,
        'imageUrl' : pagedata.get("url"),
        })
    return None # TODO Something

@t_login_required    
def save_line(request):
    # TODO Get some magic parameters from the modal.
    return None # TODO Something