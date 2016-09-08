from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from . import views
from . import viewsets


router = DefaultRouter()


collection_list = viewsets.CollectionViewSet.as_view({'get': 'list'})
router.register(
    r'collections',
    viewsets.CollectionViewSet,
    base_name='collections'
)

document_list = viewsets.DocumentViewSet.as_view({'get': 'list'})
router.register(
    r'collections/(?P<collection_id>\w+)/documents',
    viewsets.DocumentViewSet,
    base_name='documents'
)

urlpatterns = [url(r'^test/', views.test_view, name='test_view')]

urlpatterns += router.urls
