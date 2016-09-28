"""read URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^library/', include('library.urls')),
#    url(r'^crowd/', include('crowd.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^review/', include('review.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^edit/', include('edit.urls')),
    url(r'^search/', include('search.urls')),
    url('', include('django.contrib.auth.urls')),


    url(r'^e-learning/', include('read_e_learning.urls', namespace='e-learning')),

]
