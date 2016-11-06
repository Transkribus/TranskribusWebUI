from functools import wraps

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
#from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url
#from django.utils import six
#from django.utils.decorators import available_attrs
from django.utils.six.moves.urllib.parse import urlparse

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout

from django.http import HttpResponse, HttpResponseRedirect
#from urllib2 import HTTPError
import requests

import sys
from .services import t_refresh, t_collections, t_log

########################
# override the login_required decorator, mostly so we can call services.t_collecctions
# at login  (we can use this to check that the transkribus session is still good or not)

def t_login_required(function,redirect_field_name=REDIRECT_FIELD_NAME,login_url=None):
    @wraps(function)
    def wrapper(request, *args, **kw):
        if request.user.is_authenticated():

            #setting collections data as a session var if not already set
            if "collections" not in request.session or request.session['collections'] is None:
                resp = t_collections(request)
                if isinstance(resp,HttpResponse): return resp

            # We check here to see if we are still authenticated with transkribus
            # a quick post request to auth/refresh should do?
            # If we get 401/403 redirect to logout if not 200 raise exception
            response = None
            try:
                response = function(request, *args, **kw)
            except requests.exceptions.HTTPError as e:
                t_log(e)
#                if e.status_code not in (401, 403):
#                    raise e
                response = HttpResponseRedirect("/logout/?next={!s}".format(request.get_full_path()))

            return response
        else:
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url. #TODO fix this after port from django source....
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
    return wrapper

#What if we end up here via an ajax request?? We're going to need a special ajax decorator... right?
def t_login_required_ajax(function,redirect_field_name=REDIRECT_FIELD_NAME,login_url=None):
    @wraps(function)
    def wrapper(request, *args, **kw):
        if request.user.is_authenticated():

            #setting collections data as a session var if not already set
#            if "collections" not in request.session or request.session['collections'] is None:
#                resp = t_collections(request)
#                if isinstance(resp,HttpResponse): return resp

            # We check here to see if we are still authenticated with transkribus
            # a quick post request to auth/refresh should do?
            # If we get 401/403 redirect to logout if not 200 raise exception
            response = None
            try:
                response = function(request, *args, **kw)
            except requests.exceptions.HTTPError as e:
#               t_log(e)
#               t_log(response)
                #TODO status_code not available here so this error catching throws an error (!)
#                if e.status_code not in (401, 403):
 #                   raise e
                response =  HttpResponse('Error', status=e)
            return response
        else:
            return HttpResponse('Unauthorized', status=401)

    return wrapper
