from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^proofread/([0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)/(\w+)$', views.proofread, name='proofread'),
    url(r'^pr_line/([0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)/(\w+)$', views.pr_line, name='pr_line'),
    url(r'^correct/([0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)/(\w+)$', views.correct, name='correct'),
    url(r'^correct/([0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)/(\w+)$', views.correct, name='correct'),
]
