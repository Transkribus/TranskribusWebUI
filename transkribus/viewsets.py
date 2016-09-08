from rest_framework import viewsets
from rest_framework.response import Response

from . import mixins


# XXX use model serializer as base
# define model equivalence relations, etc.
# https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/serializers.py#L776

# like so:

# class MySerializer(SpecialSerializerWhatever):
#    class Meta:
#        model = TheXmlSerializerThing

   
# XXX FIXTHIS should not be here, but serializers.py already contains
#     XML serializers with same name ...

from rest_framework import serializers

class CollectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    role = serializers.CharField()
    description = serializers.CharField()        


class DocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    num_pages = serializers.IntegerField()
    uploader = serializers.CharField()
    # uploaded_at = serializers.IntegerField()


class CollectionViewSet(mixins.ApiMixin, viewsets.ViewSet):
    serializer_class = CollectionSerializer

    def list(self, request):

        collections = self.api.list_collections()

        serializer = CollectionSerializer(collections, many=True)

        return Response(serializer.data)


class DocumentViewSet(mixins.ApiMixin, viewsets.ViewSet):
    serializer_class = DocumentSerializer

    def list(self, request, collection_id):

        documents = self.api.list_docs_by_collection_id(collection_id)
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
