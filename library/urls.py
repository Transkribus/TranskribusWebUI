from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^kill_job$', views.kill_job, name='kill_job'),
    url(r'^job_count$', views.job_count, name='job_count'),
    url(r'^changed_jobs_modal$', views.changed_jobs_modal, name='changed_jobs_modal'),
    
    url(r'^message_modal$', views.message_modal, name='message_modal'),
    
    url(r'^jobs$', views.jobs, name='jobs'),
    url(r'^jobs_list$', views.jobs_list, name='jobs_list'),
    url(r'^jobs_list_compact$', views.jobs_list_compact, name='jobs_list_compact'),
    url(r'^create_collection_modal$', views.create_collection_modal, name='create_collection_modal'),
    url(r'^collections_dropdown$', views.collections_dropdown, name='collections_dropdown'),
    url(r'^ingest_mets_xml$', views.ingest_mets_xml, name='ingest_mets_xml'),    
    url(r'^ingest_mets_url$', views.ingest_mets_url, name='ingest_mets_url'),
    

    url(r'^collections$', views.collections, name='collections'),
    url(r'^collection/([0-9]+)$', views.collection, name='collection'),
    url(r'^collection_noaccess/([0-9]+)$', views.collection_noaccess, name='collection_noaccess'),
    url(r'^document/([0-9]+)/([0-9]+)$', views.document, name='document'),
    url(r'^page/([0-9]+)/([0-9]+)/([0-9]+)$', views.page, name='page'),
    url(r'^transcript/([0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)$', views.transcript, name='transcript'),
    url(r'^region/([0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)/(\w+)$', views.region, name='region'), #TODO improve regionId regex?
    url(r'^line/([0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)/(\w+)/(\w+)$', views.line, name='line'), #TODO as above...
    #oh no he di'nt
    url(r'^word/([0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)/(\w+)/(\w+)/(\w+)$', views.word, name='word'), #TODO as above...
    #oh yes he di' 
    url(r'^rand/([0-9]+)/(word|line|region|transcript|document)$', views.rand, name='rand'),

    url(r'^search$', views.search, name='search'),
    url(r'^about$', views.about, name='about'),
    url(r'^user_guide$', views.user_guide, name='user_guide'),
    url(r'^users/([0-9]+)/([0-9]+)$', views.users, name='users'),
    url(r'^register$', views.register, name='register'),
    url(r'^$', views.index, name='index'),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url('^', include('django.contrib.auth.urls')),
]
