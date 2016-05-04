from functools import wraps

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
#from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url
#from django.utils import six
#from django.utils.decorators import available_attrs
from django.utils.six.moves.urllib.parse import urlparse

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect

import sys
import services

#override the login_required decorator, mostly so we can call services.t_collecctions at login
def t_login_required(function,redirect_field_name=REDIRECT_FIELD_NAME,login_url=None):
    @wraps(function)
    def wrapper(request, *args, **kw):	
        if request.user.is_authenticated():
	    #setting collections data as a session var if no already set
	    if "collections" not in request.session:
	         request.session['collections'] = services.t_collections()
            return function(request, *args, **kw)
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
