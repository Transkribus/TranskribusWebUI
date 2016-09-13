from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'correct/([0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)/(\w+)$', views.correct, name='correct'),
    url(r'^correct_modal$', views.correct_modal, name='correct_modal'),
    url(r'^correct_js$', views.correct_js, name='correct_js'),
]
