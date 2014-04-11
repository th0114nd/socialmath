from django.conf.urls import url

from prooftree import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
    url(r'^(?P<node_id>\d+)/$', views.detail, name='detail'),    
]