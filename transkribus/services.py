import requests
import pickle

from django.conf import settings

from . import utils


TRANSKRIBUS_API_SESSION_KEY = KEY = '_TRANSKRIBUS_API_SESSION_KEY'


# import xmltodict
# import json
# from lxml import objectify

# def serialize(parse):
#     def wrapper(func):
#         def wrapped(*args, **kwargs):
#             response = func(*args, **kwargs)
#             # NOTE: must use stream=True keyword for this to work
#             response.raw.decode_content = True
#             return parse(response.raw)
#         return wrapped
#     return wrapper

# def to_camelcase(string):
#     return ''.join(
#         s.title() if i > 0 else s
#         for i, s in enumerate(string.split('_')))


# def postprocessor(path, key, value):
#     if type(value) is str:
#         if value.isdigit():
#             value = int(value)
#     return key, value

# NOTE: there are the serializers
# parse_xml = lambda fileobj: xmltodict.parse(
#     fileobj, postprocessor=postprocessor)
# parse_xml = lambda response: objectify.parse(response.raw).getroot()
# parse_code = lambda response: response.status_code
# parse_json = lambda fileobj: json.load(fileobj)


def raise_error(func):
    def _(*args, **kwargs):
        response = func(*args, **kwargs)
        response.raise_for_status()
        return response
    return _


class Client:

    def __init__(self, **options):
        # NOTE: options are keyword arguments set in all requests
        self.options = options

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def update_kwargs_with_options(self, kwargs):
        # NOTE: override options with specific kwargs
        for key in self.options:
            kwargs.setdefault(key, self.options[key])


class RequestsClient(Client):

    OPTIONS = {'verify': True, 'stream': True}

    def __init__(self, session=None, *args, **kwargs):

        self._client = requests

        options = self.OPTIONS.copy()
        kwargs.update(options)

        super(RequestsClient, self).__init__(*args, **kwargs)
 
    @raise_error
    def get(self, *args, **kwargs):
        self.update_kwargs_with_options(kwargs)
        return self._client.get(*args, **kwargs)

    @raise_error
    def post(self, *args, **kwargs):
        self.update_kwargs_with_options(kwargs)
        return self._client.post(*args, **kwargs)

    def head(self, *args, **kwargs):
        raise NotImplementedError

    def put(self, *args, **kwargs):
        raise NotImplementedError

    def patch(self, *args, **kwargs):
        raise NotImplementedError

    def options(self, *args, **kwargs):
        raise NotImplementedError


class API:
    client_class = None
    murl = None


class RequestsAPI(API):

    client_class = RequestsClient

    def __init__(self, client=None, **options):
        if client is None:
            self.client = self.client_class(**options)
        else:
            self.client = client


class TranskribusAPI(RequestsAPI):

    murl = utils.mURL(settings.TRANSKRIBUS_URL)

    def login(self, username, password):
        data = {'user': username, 'pw': password}

        r = self.client.post(
            self.murl('auth', 'login').url,
            data=data
        )

        self._session_cookies = r.cookies.get_dict()

        return r

    def refresh(self):
        return self.client.post(
            self.murl('auth', 'refresh').url
        )

    def list_collections(self):
        return self.client.get(
            self.murl('collections', 'list.xml').url
        )

    def list_docs_by_collection_id(self, collection_id):
        # XXX FIXTHIS cache this somehow
        return self.client.get(
            self.murl(
                'collections',
                collection_id,
                'list.xml'
            ).url
        )

    def get_doc_by_id(self, collection_id, document_id):
        return self.client.get(
            self.murl(
                'collections',
                collection_id,
                document_id,
                'fulldoc.xml'
            ).url
        )

    def get_page(self, collection_id, document_id, page_id):
        return self.client.get(
            self.murl(
                'collections',
                collection_id,
                document_id,
                page_id,
                'list'
            ).url
        )

    def create_document_from_mets(self, collection_id, mets_file):
        return self.client.post(
            self.murl(
                'collections',
                collection_id,
                'createDocFromMets'
            ),
            files={'mets': mets_file}
        )
    
    def create_document_from_mets(self, collection_id, mets_file):
        return self.client.post(
            self.murl(
                'collections',
                collection_id,
                'createDocFromMets'
            ).url,
            files={'mets': mets_file}
        )
    
    def create_document_from_mets_url(self, collection_id, mets_url):
        return self.client.post(
            self.murl(
                'collections',
                collection_id,
                'createDocFromMets'
            ).url,
            data={'fileName': mets_url}
        )

    def create_collection(self, collection_name):
        return self.client.post(
            self.murl(
                'collections',
                collection_id,
                'createDocFromMets'
            ).url,
            data={'collName': collection_name}
        )
 
    def get_jobs(self, filter_by_user=None, status=None, job_id=None,
                 job_type=None, index=None, n_values=None,
                 sort_column=None, sort_direction=None):

        params = dict(filterByUser=filter_by_user,
                      status=status, id=job_id,type=job_type,
                      index=index, nValues=n_values,
                      sortColumn=sort_column,
                      sortDirection=sort_direction)

        return self.client.get(
            self.murl('jobs', 'list.xml').url,
            params={k: v for k, v in params.items() if v is not None}
        )

    def count_jobs(self, filter_by_user=None, status=None,
                   job_type=None, job_id=None):

        params = dict(filterByUser=filter_by_user,
                      status=status, id=job_id,type=job_type)

        return self.client.get(
            self.murl('jobs', 'list.xml').url,
            params={k: v for k, v in params.items() if v is not None})

    def kill_job(self, job_id):
        return self.client.get(
            self.murl('jobs', job_id, 'kill').url)


def dump(api, request):
    request.session[KEY] = api._session_cookies

def load(request):
    maybe_cookies = request.session[KEY]
    if bool(maybe_cookies):
        kwargs = {'cookies': maybe_cookies}
    else:
        kwargs = {}
    return TranskribusAPI(**kwargs)
