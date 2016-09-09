#imports of python modules
import json
import sys
import re
import random
from  xml.etree import ElementTree

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
from django.utils.html import escape

#Imports pf read modules
from read.decorators import t_login_required
from read.services import *
from read.utils import crop
#t_collection, t_register,

#Imports from app (library)
import library.settings
import library.navigation# TODO Fix this import!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from library.forms import RegisterForm, IngestMetsUrlForm, MetsFileForm
from dicttoxml import dicttoxml

#from profiler import profile #profile is a decorator, but things get circular if I include it in decorators.py so...


def index(request):
    return render(request, 'review/homepage.html' )

# TODO Crop. It's broken now and should be reused anyway.
# TODO Consider overlap with region view etc.
@t_login_required
def proofread(request, collId, docId, page, transcriptId, regionId):# TODO Decide how to select which transcript to work with unless it should always be the newest?

    current_transcript = t_current_transcript(request, collId, docId, page)

    if request.method == 'POST':# OK to assume that if we get a post request, it means that we don't need to do the sort of checking as when first showing the transcript?
        transcript_xml = t_transcript_xml(request, transcriptId, current_transcript.get("url"))
        transcript_root = ElementTree.fromstring(transcript_xml)
        for text_region in transcript_root.iter('{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}TextRegion'):# We have to have the namespace...
            if text_region.attrib['id'] == regionId:
                for line in text_region.iter('{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}TextLine'):
                    modified_text = escape(request.POST.get(line.attrib['id']))
                    line.text = modified_text
                    line.find('{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}TextEquiv').find('{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Unicode').text = modified_text
        t_save_transcript(request, ElementTree.tostring(transcript_root), collId, docId, page)
        current_transcript = t_current_transcript(request, collId, docId, page)# We want the updated transcript now.

    transcript = t_transcript(request, current_transcript.get("tsId"),current_transcript.get("url"))
    transcriptId = str(transcript.get("tsId"))
    regions=transcript.get("PcGts").get("Page").get("TextRegion");

    if isinstance(regions, dict):
        regions = [regions]

    for x in regions:
        x['key'] = x.get("@id")
        if(str(regionId) == str(x.get("@id"))):
            region = x

    if region.get("Coords"):
        region['crop_str'] = crop(region.get("Coords").get("@points"))

    nav = library.navigation.up_next_prev("region",regionId,regions,[collId,docId,page,transcriptId])
    lines = region.get("TextLine")

    if isinstance(lines, dict):
        lines = [lines]

    if lines:
        for x in lines:
            x['md'] = t_metadata(x.get("@custom"))
            x['id'] = x.get("@id")
            x['crop'] = crop(x.get("Coords").get("@points"),True)

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
        'imageUrl' : t_document(request, collId, docId, -1).get('pageList').get('pages')[int(page) - 1].get("url"),
        })
    
# Implementation of the new interface.
@t_login_required
def correct(request, collId, docId, page, transcriptId, regionId):# TODO Decide how to select which transcript to work with unless it should always be the newest?
    
    current_transcript = t_current_transcript(request, collId, docId, page)

    if request.method == 'POST':# OK to assume that if we get a post request, it means that we don't need to do the sort of checking as when first showing the transcript?
        transcript_xml = t_transcript_xml(request, transcriptId, current_transcript.get("url"))
        transcript_root = ElementTree.fromstring(transcript_xml)
        for text_region in transcript_root.iter('{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}TextRegion'):# We have to have the namespace...
            if text_region.attrib['id'] == regionId:
                for line in text_region.iter('{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}TextLine'):
                    modified_text = escape(request.POST.get(line.attrib['id']))
                    line.text = modified_text
                    line.find('{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}TextEquiv').find('{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Unicode').text = modified_text
        t_save_transcript(request, ElementTree.tostring(transcript_root), collId, docId, page)
        current_transcript = t_current_transcript(request, collId, docId, page)# We want the updated transcript now.

    transcript = t_transcript(request, current_transcript.get("tsId"),current_transcript.get("url"))
    transcriptId = str(transcript.get("tsId"))    
    regions=transcript.get("PcGts").get("Page").get("TextRegion");
    
    if isinstance(regions, dict):
        regions = [regions]
    
    lineList = []
    for x in regions:
        lines = x.get("TextLine")
        #sys.stdout.write("Processing region, x is: %s \r\n" % x)
        #sys.stdout.flush()
        if isinstance(lines, dict):
            #sys.stdout.write("### Line to line list. \r\n")
            sys.stdout.flush()
            lineList.extend([lines])
        else: # Assume that lines is a list of lines
            for line in lines:
                #sys.stdout.write("### List of lines to line list. \r\n")
                #sys.stdout.flush()
                lineList.extend([line])
        
    if lineList:
        for x in lineList:
            x['md'] = t_metadata(x.get("@custom"))
            x['crop_str'] = crop(x.get("Coords").get("@points"))
            x['id'] = x.get("@id")
    
    return render(request, 'review/correct.html', {
         'imageUrl' : t_document(request, collId, docId, -1).get('pageList').get('pages')[int(page) - 1].get("url"),
         'lines' : lineList, 
        })

@t_login_required
def correct_iframe(request):
    return render(request, 'review/correct_iframe.html')

@t_login_required
def pr_line():
    return render(request, 'review/pr_line.html')

<<<<<<< HEAD
=======
#def crop(coords):
#    sys.stdout.write("############# COORDS: %s\r\n" % coords )
#   # coords = region.get("Coords").get("@points")
#    points = coords.split()
#    xmin=ymin=99999999 #TODO durh...
#    xmax=ymax=0
#    points = [map(int, point.split(',')) for point in points]
#    #boo two loops! but I like this one above here...
    #TODO woops... I actually need this to x-off y-off widt and height...
##    for point in points:
#        if point[1] > ymax : ymax=point[1]
#        if point[1] < ymin : ymin=point[1]
#        if point[0] > xmax : xmax=point[0]
#        if point[0] < xmin : xmin=point[0]
#        crop = {'x':xmin, 'y':ymin, 'w':(xmax-xmin), 'h': (ymax-ymin)}
#        crop_str = str(crop.get('x'))+"x"+str(crop.get('y'))+"x"+str(crop.get('w'))+"x"+str(crop.get('h'))
#
#    return crop_str
#    sys.stdout.write("POINTS: %s\r\n" % (points) )
##    sys.stdout.write("CROP: %s\r\n" % (crop) )
>>>>>>> refs/remotes/origin/master
