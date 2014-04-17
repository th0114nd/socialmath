from django.http import HttpResponse
from prooftree.models import *
from prooftree.serializers import *
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

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
    maxid = Node.objects.max_id()
    node_id = int(node_id)
    if node_id is None:
        return HttpResponse("Bad Request. An id is required.", status=400)
    if int(node_id) > int(maxid):
        return HttpResponse("Bad Request. Id not found.", status=404)
    try:
        node = Node.objects.get(node_id=node_id)
    except Node.ObjectDoesNotExist:
        return HttpResponse("Bad Request. Id has been delete.", status=410)

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
    theorem_list = Node.objects.all().order_by('-pub_time')
    context = {'theorem_list': theorem_list}
    context['lemma_range'] = range(9)
    return render(request, 'prooftree/add_article.html', context)

def delete(request, node_id):
    return

def change(request, node_id):
    return