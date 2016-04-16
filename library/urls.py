from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^collections$', views.collections, name='collections'),
    url(r'^documents$', views.documents, name='documents'),
    url(r'^document$', views.document, name='document'),
    url(r'^page$', views.page, name='page'),
    url(r'^search$', views.search, name='search'),
    url(r'^about$', views.about, name='about'),
    url(r'^user_guide$', views.user_guide, name='user_guide'),
    url(r'^register$', views.register, name='register'),
    url(r'^$', views.index, name='index'),
    url(r'^profile$', views.profile, name='profile'),
    url('^', include('django.contrib.auth.urls')),
]
