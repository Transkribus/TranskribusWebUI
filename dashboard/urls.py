from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^([0-9]+)$', views.d_collection, name='d_collection'),
    url(r'^([0-9]+)/([0-9]+)$', views.d_document, name='d_document'),
    url(r'^actions_for_table_ajax$', views.actions_for_table_ajax, name='actions_for_table_ajax'),
    url(r'^actions_for_table_ajax/([0-9]+)$', views.actions_for_table_ajax, name='actions_for_table_ajax'),
    url(r'^collections_for_table_ajax$', views.collections_for_table_ajax, name='collections_for_table_ajax'),
    url(r'^documents_for_table_ajax/([0-9]+)$', views.documents_for_table_ajax, name='documents_for_table_ajax'),
    url(r'^actions_for_chart_ajax$', views.actions_for_chart_ajax, name='actions_for_chart_ajax'),
    url(r'^$', views.index, name='index'),
]
