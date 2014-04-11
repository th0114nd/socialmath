from django.conf.urls import url

from prooftree import views

urlpatterns = [
	url(r'^$', views.index, name='index')
]