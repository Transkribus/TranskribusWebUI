from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'correct/([0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)$', views.correct, name='correct'),
    #allow edit of current transcript with no transcriptId
    url(r'correct/([0-9]+)/([0-9]+)/([0-9]+)$', views.correct, name='correct'),
]
