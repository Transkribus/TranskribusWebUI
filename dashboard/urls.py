from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^([0-9]+)$', views.collection, name='collection'),
    url(r'^([0-9]+)/([0-9]+)$', views.document, name='document'),
    url(r'^actions_for_table_ajax$', views.actions_for_table_ajax, name='actions_for_table_ajax'),
    url(r'^actions_for_table_ajax/([0-9]+)$', views.actions_for_table_ajax, name='actions_for_table_ajax'),
    url(r'^actions_for_chart_ajax$', views.actions_for_chart_ajax, name='actions_for_chart_ajax'),
    url(r'^$', views.index, name='index'),
]
