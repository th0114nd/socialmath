from django.conf.urls import url

from prooftree import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
    url(r'^get/one/(?P<node_id>\d+)/$', views.detail, name='detail'),    
    url(r'^delete/one/(?P<node_id>\d+)/$', views.delete, name='delete-one'),
    url(r'^change/(?P<node_id>\d+)/$', views.change, name='change'),
    url(r'^add/(?P<work_type>\d+)/$', views.add, name='add'),
    url(r'^submit_theorem/$', views.submit_theorem, name='submit-theorem'),
    url(r'^submit_article/$', views.submit_article, name='submit-article'),
]