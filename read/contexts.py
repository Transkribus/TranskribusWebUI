def appname(request):
    return {'appname': request.resolver_match.app_name }
