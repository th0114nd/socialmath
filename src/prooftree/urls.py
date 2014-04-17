from django.conf.urls import url

from prooftree import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
    url(r'^get/one/(?P<node_id>\d+)/$', views.detail, name='detail'),    
    url(r'^delete/one/(?P<node_id>\d+)/$', views.delete, name='delete-one'),
    url(r'^change/(?P<node_id>\d+)/$', views.change, name='change'),
    url(r'^add/(?P<work_type>\w+/$)', views.add, name='add'),
]