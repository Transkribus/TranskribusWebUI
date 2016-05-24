from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^collections$', views.collections, name='collections'),
    url(r'^collection/([0-9]+)$', views.collection, name='collection'),
    url(r'^collection_noaccess/([0-9]+)$', views.collection_noaccess, name='collection_noaccess'),
    url(r'^document/([0-9]+)/([0-9]+)$', views.document, name='document'),
    url(r'^page/([0-9]+)/([0-9]+)/([0-9]+)$', views.page, name='page'),
    url(r'^transcript/([0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)$', views.transcript, name='transcript'),
    url(r'^search$', views.search, name='search'),
    url(r'^about$', views.about, name='about'),
    url(r'^user_guide$', views.user_guide, name='user_guide'),
    url(r'^users/([0-9]+)/([0-9]+)$', views.users, name='users'),
    url(r'^register$', views.register, name='register'),
    url(r'^$', views.index, name='index'),
    url(r'^profile$', views.profile, name='profile'),
    url('^', include('django.contrib.auth.urls')),
]
