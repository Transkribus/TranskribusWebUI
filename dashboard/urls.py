from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^([0-9]+)$', views.d_collection, name='d_collection'),
    url(r'^([0-9]+)/([0-9]+)$', views.d_document, name='d_document'),

    #TODO these three in a single call...? maybe not possible?
    url(r'^table_ajax/(?P<list_name>[a-z]+)$', views.table_ajax, name='table_ajax'),
    url(r'^table_ajax/(?P<list_name>[a-z]+)/(?P<collId>[0-9]+)$', views.table_ajax, name='table_ajax'),
    url(r'^table_ajax/(?P<list_name>[a-z]+)/(?P<collId>[0-9]+)/(?P<docId>[0-9]+)$', views.table_ajax, name='table_ajax'),

    url(r'^actions_for_chart_ajax$', views.actions_for_chart_ajax, name='actions_for_chart_ajax'),
    url(r'^actions_for_chart_ajax/(?P<collId>[0-9]+)$', views.actions_for_chart_ajax, name='actions_for_chart_ajax'),
    url(r'^actions_for_chart_ajax/(?P<collId>[0-9]+)/(?P<docId>[0-9]+)$', views.actions_for_chart_ajax, name='actions_for_chart_ajax'),


    url(r'^$', views.index, name='index'),
]
