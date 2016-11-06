from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^([0-9]+)$', views.d_collection, name='d_collection'),
    url(r'^([0-9]+)/([0-9]+)$', views.d_document, name='d_document'),
    url(r'^u/([a-zA-Z0-9_@\.]+)$', views.d_user, name='d_user'), #yuk TODO use userid (Whcih we have) but can't see how to get user data other than via user/findUser

    #### Data for tables (dataTable.js) ####
    url(r'^table_ajax/(?P<list_name>[a-z]+)$', views.table_ajax, name='table_ajax'),
    url(r'^table_ajax/(?P<list_name>[a-z]+)/(?P<collId>[0-9]+)$', views.table_ajax, name='table_ajax'),
    url(r'^table_ajax/(?P<list_name>[a-z]+)/(?P<collId>[0-9]+)/(?P<docId>[0-9]+)$', views.table_ajax, name='table_ajax'),
    url(r'^table_ajax/u/(?P<userId>[0-9]+)/(?P<list_name>[a-z]+)$', views.table_ajax, name='table_ajax'),

    ##### Data for charts (charts.js) ####
    # data for user (all collections)
    url(r'^chart_ajax/(?P<list_name>[a-z]+)/(?P<chart_type>[a-z_]+)$', views.chart_ajax, name='chart_ajax'),
    # data for collection (all users)
    url(r'^chart_ajax/(?P<list_name>[a-z]+)/(?P<chart_type>[a-z_]+)/(?P<collId>[0-9]+)$', views.chart_ajax, name='chart_ajax'),
    # data for document (all users)
    url(r'^chart_ajax/(?P<list_name>[a-z]+)/(?P<chart_type>[a-z_]+)/(?P<collId>[0-9]+)/(?P<docId>[0-9]+)$', views.chart_ajax, name='chart_ajax'),
    # data for user (this collection)
    url(r'^chart_ajax/u/(?P<userId>[0-9]+)/(?P<list_name>[a-z_]+)/(?P<chart_type>[a-z_]+)/(?P<collId>[0-9]+)$', views.chart_ajax, name='chart_ajax'),
    # data for user (this document)
    url(r'^chart_ajax/u/(?P<userId>[0-9]+)/(?P<list_name>[a-z_]+)/(?P<chart_type>[a-z_]+)/(?P<collId>[0-9]+)/(?P<docId>[0-9]+)$', views.chart_ajax, name='chart_ajax'),

    # pass in a subject (eg for top_bar we want the top N *actions by *subject where *subject might be userName, collId or docId etc)
    #presently returns data by subject for list filtered to those list items to which the user is associated (ie my actions)
    url(r'^chart_ajax/(?P<list_name>[a-z_]+)/(?P<chart_type>[a-z_]+)/(?P<subject>[a-zA-Z_]+)$', views.chart_ajax, name='chart_ajax'),
    url(r'^chart_ajax/(?P<list_name>[a-z_]+)/(?P<chart_type>[a-z_]+)/(?P<subject>[a-zA-Z_]+)/(?P<label>[a-zA-Z_]+)$', views.chart_ajax, name='chart_ajax'),

    #data by subject for list filtered by collId (eg actions/top_bar/docId/3 gives us the documents in collection 3 with the greatest activity)
    url(r'^chart_ajax/(?P<list_name>[a-z_]+)/(?P<chart_type>[a-z_]+)/(?P<subject>[a-zA-Z_]+)/(?P<collId>[0-9]+)$', views.chart_ajax, name='chart_ajax'),
    url(r'^chart_ajax/(?P<list_name>[a-z_]+)/(?P<chart_type>[a-z_]+)/(?P<subject>[a-zA-Z_]+)/(?P<label>[a-zA-Z_]+)/(?P<collId>[0-9]+)$', views.chart_ajax, name='chart_ajax'),

    # as above but for a given document
    url(r'^chart_ajax/(?P<list_name>[a-z_]+)/(?P<chart_type>[a-z_]+)/(?P<subject>[a-zA-Z_]+)/(?P<collId>[0-9]+)/(?P<docId>[0-9]+)$', views.chart_ajax, name='chart_ajax'),
    url(r'^chart_ajax/(?P<list_name>[a-z_]+)/(?P<chart_type>[a-z_]+)/(?P<subject>[a-zA-Z_]+)/(?P<label>[a-zA-Z_]+)/(?P<collId>[0-9]+)/(?P<docId>[0-9]+)$', views.chart_ajax, name='chart_ajax'),

]
