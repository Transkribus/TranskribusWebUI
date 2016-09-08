from rest_framework import viewsets
from rest_framework.response import Response

from . import serializers
from . import mixins


class CollectionViewSet(mixins.ApiMixin, viewsets.ViewSet):
    serializer_class = serializers.CollectionSerializer

    def list(self, request):

        collections = self.api.get_collections_for_user()

        serializer = serializers.CollectionSerializer(collections,
                                                      many=True)

        return Response(serializer.data)


class DocumentViewSet(mixins.ApiMixin, viewsets.ViewSet):
    serializer_class = serializers.DocumentSerializer

    def list(self, request, collection_id):

        documents = self.api.get_documents_for_collection(collection_id)
        serializer = serializers.DocumentSerializer(documents, many=True)

        return Response(serializer.data)

        # documents = self.api.get_collections_for_document(collection_id)
        # document_list = self.api.collections(collection_id).documents.get()
        # serializer_list = serializers.DocumentSerializer(
        #     documents,
        #     many=True
        # )

        # return Response(serializer.data)
