from rest_framework import viewsets


from . import services


class ApiMixin(object):

    def initial(self, request, *args, **kwargs):
        # See here: https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/views.py#L369)
        super(ApiMixin, self).initial(request, *args, **kwargs)
        self.initialize_client(request)

    def initialize_client(self, request):
        self.api = services.get_or_create_api_client(request)
