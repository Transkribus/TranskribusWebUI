from functools import wraps

from django.contrib.auth import decorators
from django.contrib.auth import logout
from django.shortcuts import redirect

from requests.exceptions import HTTPError as MaybeLoginExpired


def login_required(view_func, *args, **kwargs):

    decorated_view_func = decorators.login_required(view_func, *args, **kwargs)

    def wrapper(request, *args, **kwargs):
        try:
            # Use default login_required decorator ...
            if not request.user.is_authenticated():
                return decorated_view_func(request, *args, **kwargs)
            else:
                return view_func(request, *args, **kwargs)
        except MaybeLoginExpired as error: # XXX FIXTHIS raise special exception?
            if error.status_code in (401, 403):
                logout(request, next_page=request.get_full_path())
                return redirect('logout')
            else:
                raise error

    return wrapper
