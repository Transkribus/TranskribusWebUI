from django import template
from django.template.defaulttags import register
import datetime


#register = template.Library()
@register.filter
def print_timestamp(timestamp):
    try:
        #assume, that timestamp is given in seconds with decimal point
        ts = float(timestamp)
    except ValueError:
        return None
    return datetime.datetime.fromtimestamp(ts/1000.0)

#register.filter(print_timestamp)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def index(List, i):
    return List[int(i)]

@register.filter
def coords_for_fimagestore(crop):
    return str(crop.get('x'))+"x"+str(crop.get('y'))+"x"+str(crop.get('w'))+"x"+str(crop.get('h'))

@register.filter
def coords_for_imagemap(coords):
    return coords.replace(" ",",")


