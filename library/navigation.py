import requests
#import urllib2
from django.conf import settings
import sys

hierarchy = {'page': 'document',
	     'document': 'collection',
	     'collection': 'collections'}

def up_next_prev(this_level,this_id, data,parent_ids=None):

    up=prev=next=None
    up=[hierarchy.get(this_level)]
    if parent_ids:
	for id in parent_ids: #TODO work out sslicker way to do this
            up.append(id)

#    sys.stdout.write("NAV DATA: %s   \r\n" % (data) )
#    sys.stdout.flush()

    #assumptions are that we want to traverse by id and do that they will be presented to us in order (can sort data if not)
    next_promise=False
    last_id=None
    for x in data:
        that_id = x.get("key")
 #       sys.stdout.write("NAV DATA: %s   \r\n" % (that_id) )
 #       sys.stdout.flush()

	if next_promise:
	    next=that_id
            next_promise=False
	if str(that_id) == str(this_id):
	    prev=last_id
	    next_promise=True
	last_id = that_id

#    sys.stdout.write("UP: %s \nNEXT: %s\nPREV: %s  \r\n" % (up, next, prev) )
    sys.stdout.flush()

    return {'up':"/library/"+"/".join(up),'next':next,'prev':prev}


