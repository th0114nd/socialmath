from django.http import HttpResponse
from prooftree.models import *
from prooftree.serializers import *
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.core.exceptions import *

class JSONResponse(HttpResponse):
	"""
	An HttpResponse that renders its content into JSON.
	"""
	def __init__(self, data, **kwargs):
		content = JSONRenderer().render(data)
		kwargs['content_type'] = 'application/json'
		super(JSONResponse, self).__init__(content, **kwargs)

def index(request):
	latest_theorem_list = Node.objects.all().order_by('-pub_time')[:10]
	context = {'latest_theorem_list': latest_theorem_list}
	return render(request, 'prooftree/index.html', context)

def pagebrief(request, pageno='1'):
	''' **HTTP GET**
		/get/brief
		/get/brief?page=n
	'''
	if request.method == 'GET':
		# Check whether page number is valid
		max_pageno = Node.objects.max_pageno()
		pageno = int(pageno)
		if pageno > max_pageno:
			return HttpResponse(status=404)
		# Get serialized data for each node on the page
		node_range = range((pageno - 1) * 100 + 1, pageno * 100 + 1)
		contents = []
		count = 0
		for node_id in node_range:
			try:
				node = Node.objects.get(node_id=node_id)
			except Node.ObjectDoesNotExist:
				continue
			count += 1
			serializer = PageNodeSerializer(node, fields=('node_id', 'kind', 'child_ids'))
			contents.append(PageNodeSerializer(serializer.data))
		# Form responses
		response = {'paging':{'current':pageno,'total':max_pageno,'count':count},
					'data':contents}
		return JSONResponse(response)


def pagemedium(request, pageno='1'):
	''' **HTTP GET**
		/get/medium
		/get/medium?page=n
	'''
	if request.method == 'GET':
		# Check whether page number is valid
		max_pageno = Node.objects.max_pageno()
		pageno = int(pageno)
		if pageno > max_pageno:
			return HttpResponse(status=404)
		# Get serialized data for each node on the page
		node_range = range((pageno - 1) * 100 + 1, pageno * 100 + 1)
		contents = []
		count = 0
		for node_id in node_range:
			try:
				node = Node.objects.get(node_id=node_id)
			except Node.ObjectDoesNotExist:
				continue
			count += 1
			serializer = PageNodeSerializer(node)
			contents.append(PageNodeSerializer(serializer.data))
		# Form responses
		response = {'paging':{'current':pageno,'total':max_pageno,'count':count},
					'data':contents}
		return JSONResponse(response)

def detail(request, node_id):
	''' **HTTP GET**
		/get/one/<id>
	'''
	# Error handling
	maxid = int(Node.objects.max_id())
	node_id = int(node_id)
	if node_id is None:
		return HttpResponse("Bad Request. An id is required.", status=400)
	if node_id > maxid:
		return HttpResponse("Bad Request. Id not found.", status=404)
	try:
		node = Node.objects.get(node_id=node_id)
	except ObjectDoesNotExist:
		return HttpResponse("Bad Request. Id has been deleted.", status=410)

	deps = DAG.objects.filter(child_id=node_id).filter(dep_type='all')
	dependencies = []
	for dep in deps:
		neighbor = Node.objects.get(node_id=dep.parent_id)
		dependencies.append(neighbor)
	context = {'node':node, 'dependencies':dependencies}

	if node.kind == 'thm':
		proofs = []
		proofdags = DAG.objects.filter(parent_id=node_id).filter(dep_type='prove')
		for pf in proofdags:
			proofs.append(Node.objects.get(node_id=pf.child_id))
		context['proofs'] = proofs
	elif node.kind == 'pf':
		theoremdag = DAG.objects.filter(child_id=node_id).filter(dep_type='prove')
		if (len(theoremdag) == 1):
			theorem = Node.objects.get(node_id=theoremdag[0].parent_id)
			context['theorem'] = theorem
	# Form responses
	return render(request, 'prooftree/detail.html', context)

def detail_json(request, node_id):
	''' **HTTP GET**
		/get/one/<id>
	'''
	# Error handling
	maxid = int(Node.objects.max_id())
	node_id = int(node_id)
	if node_id is None:
		return HttpResponse("Bad Request. An id is required.", status=400)
	if node_id > maxid:
		return HttpResponse("Bad Request. Id not found.", status=404)
	try:
		node = Node.objects.get(node_id=node_id)
	except ObjectDoesNotExist:
		return HttpResponse("Bad Request. Id has been deleted.", status=410)

	if request.method == 'GET':
		neighbor_ids = list(DAG.objects.get_children(node_id)) + \
					   list(DAG.objects.get_parents(node_id))
		neighbors = []
		for neighbor_id in neighbor_ids:
			neighbor = Node.objects.get(node_id=neighbor_id)
			serializer = NodeSerializer(neighbor)
			neighbors.append(serializer.data)

		# Form responses
		response = {'wanted': NodeSerializer(node).data, 'neighbors':neighbors}
		return JSONResponse(response)


def add(request, work_type):
    theorem_list = Node.objects.filter(kind='thm').order_by('-pub_time')
    context = {'theorem_list': theorem_list}
    context['lemma_range'] = range(9)
    if (int(work_type) == 1):
        return render(request, 'prooftree/add_theorem.html', context)
    elif (int(work_type) == 2):
        return render(request, 'prooftree/add_article.html', context)

def delete_one(request, node_id):
    ''' **HTTP PUT**
       /delete/one/<id>'''
    # Error handling
    maxid = int(Node.objects.max_id())
    node_id = int(node_id)
    if node_id > maxid:
        return HttpResponse("Bad Request. Id not found.", status=404)
    try:
        node = Node.objects.get(node_id=node_id)
    except ObjectDoesNotExist:
        return HttpResponse("Bad Request. Id has been delete.", status=410)
    # TODO: 403 do not have authorization

    # Delete dependencies from DAG
    DAG.objects.filter(child_id=node_id).delete()
    DAG.objects.filter(parent_id=node_id).delete()
    # Delete keyword mapping
    KWMap.objects.filter(node_id=node_id).delete()
    # Delete node
    node.delete()
    return index(request)

def delete_pf(request, node_id, pf_id):
    ''' **HTTP PUT**
       /delete/proof/<id>/<proofid>'''
    # Error handling
    maxid = int(Node.objects.max_id())
    node_id = int(node_id)
    pf_id = int(pf_id)
    if node_id > maxid or pf_id > max_id:
        return HttpResponse("Bad Request. Id not found.", status=404)
    try:
        parent = Node.objects.get(node_id=node_id)
        proof = Node.objects.get(node_id=pf_id)
    except ObjectDoesNotExist:
        return HttpResponse("Bad Request. Id has been delete.", status=410)
    # TODO: 403 do not have authorization

    if request.method == 'PUT':
        # Delete dependencies from DAG
        DAG.objects.filter(parent_id=node_id).filter(child_id=pf_id).delete()
        # Delete keyword mapping
        KWMap.objects.filter(node_id=pf_id).delete()
        # Delete node
        proof.delete()

def delete_all(request):
    ''' **HTTP PUT**
       /delete/all/'''

    if request.method == 'PUT':
        Node.objects.all().delete()
        keyword.objects.all().delete()
        DAG.objects.all().delete()
        KWMap.objects.all().delete()

def change(request, node_id):
    node = get_object_or_404(Node, pk=node_id)
    theorem_list = list(Node.objects.filter(kind='thm').order_by('pub_time'))
    context = {'theorem_list': theorem_list}
    context['node'] = node
    dependencies = DAG.objects.filter(child_id=node_id).filter(dep_type='all')
    lemmas = []
    for dependency in dependencies:
        if (dependency.parent_id not in lemmas):
            i = 0
            lemma = get_object_or_404(Node, pk=dependency.parent_id)
            lemmas.append(lemma)
            i += 1
    context['lemmas'] = lemmas
    for lemma in lemmas:
        theorem_list.remove(lemma)
    context['theorem_list'] = theorem_list
    if len(dependencies) < 9:
        context['lemma_range'] = range(len(dependencies), 9)
    else:
        context['lemma_range'] = []
    if node.kind == 'thm':
        return render(request, 'prooftree/change_theorem.html', context)
    elif node.kind == 'pf':
        theorem = DAG.objects.filter(child_id=node_id).filter(dep_type='prove')
        if (theorem != []) and (len(theorem) == 1):
            context['about_theorem'] = get_object_or_404(Node, pk=theorem[0].parent_id)
            return render(request, 'prooftree/change_article.html', context)
    print node.kind
    print theorem
    return HttpResponse("Error: Node type invalid", status=404)

def submit_change(request, node_id):
    node = get_object_or_404(Node, pk=node_id)
    node.title = request.POST['title']
    node.statement = request.POST['body']
    node.save()
    DAG.objects.filter(child_id=node_id).delete()
    deps = []
    for i in range(9):
        dep = request.POST['lemma' + str(i)]
        if (dep != "blank") and (int(dep) not in deps):
            deps.append(int(dep))
            new_dag = DAG(parent=get_object_or_404(Node, pk=int(dep)), child=node, dep_type='all')
            new_dag.save()
    if (node.kind == 'pf'):
        theorem = request.POST['theorem']
        if (theorem != "blank") and (int(theorem) not in deps):
            new_dag = DAG(parent=get_object_or_404(Node, pk=int(theorem)), child=node, dep_type='prove')
            new_dag.save()
    return detail(request, node_id)

def submit_article(request):
    article_title = request.POST['title']
    theorem = get_object_or_404(Node, pk=int(request.POST['theorem']))
    body = request.POST['body']
    newnode = Node(kind='pf', title=article_title, statement=body)
    newnode.save()
    deps = []
    for i in range(9):
        dep = request.POST['lemma' + str(i)]
        if (dep != "blank") and (int(dep) not in deps):
            deps.append(int(dep))
            new_dag = DAG(parent=get_object_or_404(Node, pk=int(dep)), child=newnode, dep_type='all')
            new_dag.save()
    theorem = request.POST['theorem']
    if (theorem != "blank") and (int(theorem) not in deps):
        new_dag = DAG(parent=get_object_or_404(Node, pk=int(theorem)), child=newnode, dep_type='prove')
        new_dag.save()
    return detail(request, newnode.node_id)

def submit_theorem(request):
    theorem_title = request.POST['title']
    body = request.POST['body']
    newnode = Node(kind='thm', title=theorem_title, statement=body)
    newnode.save()
    deps = []
    for i in range(9):
        dep = request.POST['lemma' + str(i)]
        if (dep != "blank") and (int(dep) not in deps):
            deps.append(int(dep))
            new_dag = DAG(parent=get_object_or_404(Node, pk=int(dep)), child=newnode, dep_type='all')
            new_dag.save()
    return detail(request, newnode.node_id)