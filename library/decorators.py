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

from django.http import HttpResponseRedirect

import sys
from services import t_refresh, t_collections

#override the login_required decorator, mostly so we can call services.t_collecctions at login
def t_login_required(function,redirect_field_name=REDIRECT_FIELD_NAME,login_url=None):
    @wraps(function)
    def wrapper(request, *args, **kw):	
        if request.user.is_authenticated():
	    # We check here to see if we are still authenticated with transkribus
	    # a quick post request ti auth/refresh should do?
	    # If we don't get a 200 we logout
	    if not t_refresh():
	        return HttpResponseRedirect('/library/logout?next='+request.get_full_path())
            #setting collections data as a session var if no already set
	    if "collections" not in request.session or request.session['collections'] is None:
	        request.session['collections'] = t_collections()
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

#import hotshot
#import os
#import time
#import tempfile
#
#try:
#    PROFILE_LOG_BASE = settings.PROFILE_LOG_BASE
#except:
#    PROFILE_LOG_BASE = tempfile.gettempdir()
#
#
#def profile(log_file):
#    """Profile some callable.
#
#    This decorator uses the hotshot profiler to profile some callable (like
#    a view function or method) and dumps the profile data somewhere sensible
#    for later processing and examination.
#
#    It takes one argument, the profile log name. If it's a relative path, it
#    places it under the PROFILE_LOG_BASE. It also inserts a time stamp into the 
#    file name, such that 'my_view.prof' become 'my_view-20100211T170321.prof', 
#    where the time stamp is in UTC. This makes it easy to run and compare 
#    multiple trials.     
#    """
#    if not os.path.isabs(log_file):
#        log_file = os.path.join(PROFILE_LOG_BASE, log_file)
#
#    def _outer(f):
#        def _inner(*args, **kwargs):
#            # Add a timestamp to the profile output when the callable
#            # is actually called.
#	    sys.stdout.write("############# PROFILING2: %s\r\n" % log_file )
#            (base, ext) = os.path.splitext(log_file)
#            base = base + "-" + time.strftime("%Y%m%dT%H%M%S", time.gmtime())
#            final_log_file = base + ext
#
#            prof = hotshot.Profile(final_log_file)
#            try:
#                ret = prof.runcall(f, *args, **kwargs)
#            finally:
#                prof.close()
#            return ret
#
#        return _inner
#    return _outer
