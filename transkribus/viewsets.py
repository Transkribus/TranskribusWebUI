from rest_framework import viewsets
from rest_framework.response import Response

from rest_framework import serializers

from . import mixins


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
