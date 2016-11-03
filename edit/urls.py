from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'correct/([0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)$', views.correct, name='correct'),
    url(r'proofread/([0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)$', views.proofread, name='proofread'),
]
