from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm
from prooftree.models import *
from django.http import HttpResponse

# Create your views here.
class NodeForm(ModelForm):
	class Meta:
		model = Node

def node_list(request, template_name='prooftree/node_list.html'):
	nodes = Node.objects.all()
	data = {}
	data['object_list'] = nodes
	return render(request, template_name, data)

def node_create(request, template_name='prooftree/node_form.hml'):
	form = NodeForm(request.POST or None)
	if form.is_valid():
		form.save()
		return redirect('node_list')
	return render(request, template_name, {'form':form})

def node_update(request, id, template_name='prooftree/node_form.html'):
	node = get_object_or_404(Node, pk=id)
	form = NodeForm(request.POST or None, instance=node)
	if form.is_valid():
		form.save()
		return redirect('node_list')
	return render(request, 'template_name', {'form':form})

def node_delete(request, id, template_name='prooftree/node_delete.html'):
	node = get_object_or_404(Node, pk=id)
	if request.method == 'POST':
		node.delete()
		return redirect('node_list')
	return render(request, template_name, {'object':node})

def index(request):
    latest_theorem_list = Node.objects.all().order_by('-pub_time')[:10]
    context = {'latest_theorem_list': latest_theorem_list}
    return render(request, 'prooftree/index.html', context)