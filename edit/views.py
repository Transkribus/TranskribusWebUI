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

#from profiler import profile #profile is a decorator, but things get circular if I include it in decorators.py so...

# TODO Consider overlap with region view etc.


    
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
            #sys.stdout.flush()
            lineList.extend([lines])
        else: # Assume that lines is a list of lines
            for line in lines:
                #sys.stdout.write("### List of lines to line list. \r\n")
                #sys.stdout.flush()
                lineList.extend([line])
    
    content_dict = {}
    # TODO Use "readingorder"?
    if lineList:
        for line in lineList:
            line_crop = crop(line.get("Coords").get("@points"))#,True)
            line['crop'] = line_crop
            line_id = line.get("@id")
            line['id'] = line_id
            content_dict[line_id] = line.get('TextEquiv').get('Unicode')
    
    return render(request, 'edit/correct.html', {
         'imageUrl': t_document(request, collId, docId, -1).get('pageList').get('pages')[int(page) - 1].get("url"),
         'lines': lineList,  
         'content': json.dumps(content_dict) 
        })
    

def correct_modal(request):
    return render(request, 'edit/correct_modal.html')
