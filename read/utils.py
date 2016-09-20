import re
import sys
import datetime
import json

# log message 
def t_log(text):
    sys.stdout.write("["+str(datetime.datetime.now())+"] "+text+"\n")
    sys.stdout.flush()


###########################################################
# crop(list coords, boolean offset=None)
# turn polygon coords into rectangle coords or xywh if offset flag set
def crop(coords, offset=None):
   # coords = region.get("Coords").get("@points")
    points = coords.split()
    xmin=ymin=99999999 #TODO durh...
    xmax=ymax=0
    points = [list(map(int, point.split(','))) for point in points]
    #boo two loops! but I like this one above here...
    #TODO woops... I actually need this to give the x-off y-off width and height...
    for point in points:
        if point[1] > ymax : ymax=point[1]
        if point[1] < ymin : ymin=point[1]
        if point[0] > xmax : xmax=point[0]
        if point[0] < xmin : xmin=point[0]
    if offset:
        crop = {'x':xmin, 'y':ymin, 'w':(xmax-xmin), 'h': (ymax-ymin)}
    else:
        crop = {'tl':[xmin,ymin], 'tr': [xmax,ymin], 'br': [xmax,ymax], 'bl': [xmin,ymax]}

    return crop
##################################
# t_metadata(str custom_attr)

def quote_value(m):
    return ':"'+m.group(1)+'",'

def quote_property(m):
    return '"'+m.group(1)+'":'

def t_metadata(custom_attr):

    #transcript metadata for this page ie the pageXML
    if not custom_attr:
        return None
    #CSS parsing (tinycss or cssutils) wasn't much cop so css => json by homemade regex (gulp!)

    #TODO rationalise steps
    #t_log("### CSS: %s   \r\n" % (custom_attr) )
    custom_json = re.sub(r' {', ': {', custom_attr)
    #t_log("### JSON 0: %s   \r\n" % (custom_json) )
    custom_json = re.sub(r'}', '},', custom_json)
    #t_log("### JSON 1: %s   \r\n" % (custom_json) )
    custom_json = re.sub(r':([^,{:]+);', quote_value, custom_json)
    #t_log("### JSON 2: %s   \r\n" % (custom_json) )
    custom_json = re.sub(r'([^,:{}\s]+):', quote_property, custom_json)
    custom_json = "{"+custom_json+"}"
    #t_log("### JSON 3: %s   \r\n" % (custom_json) )
    custom_json = re.sub(r',}', '}', custom_json)
    #t_log("### JSON FINAL: %s   \r\n" % (custom_json) )

    t_metadata = json.loads(custom_json)

    t_log("### METADATA from CSS: %s   \r\n" % (t_metadata) )

    return t_metadata

