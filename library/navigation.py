import requests
#import urllib2
from django.conf import settings
import sys
from . import settings
from read.utils import t_log

hierarchy = {'word': 'line',
             'line': 'region',
             'region': 'transcript',
             'transcript': 'page',
             'page': 'document',
             'document': 'collection',
             'collection': 'collections'}

def up_next_prev(this_level,this_id, data,parent_ids=None):

    up=prev=next=None
    up=[hierarchy.get(this_level)]
    if parent_ids:
        for id in parent_ids: #TODO work out slicker way to do this
            up.append(id)

    #assumptions are that we want to traverse by id and do that they will be presented to us in order (can sort data if not)
    next_promise=False
    last_id=None
    for x in data:
        that_id = x.get("key")
        if next_promise:
            next=that_id
            next_promise=False
        if str(that_id) == str(this_id):
            prev=last_id
            next_promise=True
        last_id = that_id

    return {'up': settings.APP_BASEURL+'/'.join(up),
                'next':next,
                'prev':prev}
