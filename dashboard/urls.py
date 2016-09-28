from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^actions_ajax$', views.actions_ajax, name='actions_ajax'),
]
