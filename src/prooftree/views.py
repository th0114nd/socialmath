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

def detail(request, node_id):
	node = get_object_or_404(Node, pk=node_id)
	return render(request, 'prooftree/detail.html', {'node':node})

def add(request, work_type):
	theorem_list = Node.objects.all().order_by('-pub_time')
	context = {'theorem_list': theorem_list}
	context['lemma_range'] = range(9)
	print work_type
	if (int(work_type) == 1):
		return render(request, 'prooftree/add_theorem.html', context)
	elif (int(work_type) == 2):
		return render(request, 'prooftree/add_article.html', context)

def delete(request, node_id):
	return

def change(request, node_id):
	return

def submit_article(request):
	article_title = request.POST['title']
	theorem = get_object_or_404(Node, pk=int(request.POST['theorem']))
	body = request.POST['body']
	newnode = Node(kind='pf', title=article_title, statement=body)
	newnode.save()
	return index(request)

def submit_theorem(request):
	theorem_title = request.POST['title']
	body = request.POST['body']
	newnode = Node(kind='thm', title=theorem_title, statement=body)
	newnode.save()
	return index(request)