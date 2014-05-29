from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect
from prooftree.models import *
from prooftree.serializers import *
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.core.exceptions import *
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, request, data, **kwargs):
        try:
            if 'callback' in request.REQUEST:
                callback = request.REQUEST['callback']
                content = '%s(%s);' % (callback, JSONRenderer().render(data))
            else:
                content = JSONRenderer().render(data)
        except(KeyError):
            content = JSONRenderer().render(data)

        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def index(request):
    latest_theorem_list = Node.objects.all().order_by('-pub_time')[:10]
    context = {'latest_theorem_list': latest_theorem_list}
    if request.user.is_authenticated():
        context['user'] = request.user
    else:
        context['user'] = None
    return render(request, 'prooftree/index.html', context)

def latest_json(request):
    nodes = Node.objects.all().order_by('-pub_time')[:50]

    contents = []
    for node in nodes:
        serializer = PageNodeSerializer(node, 
            fields=('node_id', 'kind', 'title'))
        contents.append(serializer.data)

    response = {'data': contents}

    return JSONResponse(request, response)

def debug(request, path='base.html'):
    return render(request, path)

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
            return HttpResponseNotFound('Page Number Out of Bound')
        # Get serialized data for each node on the page
        node_range = range((pageno - 1) * 100 + 1, pageno * 100 + 1)
        contents = []
        count = 0
        for node_id in node_range:
            try:
                node = Node.objects.get(node_id=node_id)
            except ObjectDoesNotExist:
                continue
            count += 1
            serializer = PageNodeSerializer(node, 
                fields=('node_id', 'kind', 'title', 'parent_ids', 'child_ids'))
            contents.append(serializer.data)
        # Form responses
        response = {'paging':{'current':pageno,'total':max_pageno,'count':count},
                    'data':contents}
        return JSONResponse(request, response)


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
            return HttpResponseNotFound('Page Number Out of Bound')
        # Get serialized data for each node on the page
        node_range = range((pageno - 1) * 100 + 1, pageno * 100 + 1)
        contents = []
        count = 0
        for node_id in node_range:
            try:
                node = Node.objects.get(node_id=node_id)
            except ObjectDoesNotExist:
                continue
            count += 1
            serializer = PageNodeSerializer(node)
            contents.append(serializer.data)
        # Form responses
        response = {'paging':{'current':pageno,'total':max_pageno,'count':count},
                    'data':contents}
        return JSONResponse(request, response)

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
    kwmaplist = KWMap.objects.filter(node=node)
    kwlist = [km.kw for km in kwmaplist]
    context['keywords'] = kwlist
    context['follow'] = 0
    if request.user.is_authenticated():
        if node in Event.objects.get_userfollowing(request.user):
            context['follow'] = 1
        else:
            context['follow'] = 2
    author = Event.objects.filter(node=node).filter(event_type="added")
    if len(author) == 1:
        if author[0].user.username == "socialmathghostuser":
            context['author'] = False
        else:
            context['author'] = author[0].user
    editors = Event.objects.filter(node=node).filter(Q(event_type="modified") | Q(event_type="added")).order_by("-pub_time")
    print "edited " + str(len(editors)) + "times"
    if len(editors) != 0:
        print ("hahahahahahahaha")
        if editors[0].user.username == "socialmathghostuser":
            context['last_editor'] = False
        else:
            context['last_editor'] = editors[0].user
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
        parent_ids = list(DAG.objects.get_parents(node_id))

        parents = []

        for nid in parent_ids:
            n = Node.objects.get(node_id=nid)
            serializer = PageNodeSerializer(n, 
                fields=('node_id', 'kind', 'title'))
            parents.append(serializer.data)

        child_ids = list(DAG.objects.get_children(node_id))

        children = []

        for nid in child_ids:
            n = Node.objects.get(node_id=nid)
            serializer = PageNodeSerializer(n, 
                fields=('node_id', 'kind', 'title'))
            children.append(serializer.data)

        kwmaplist = KWMap.objects.filter(node=node)
        kwlist = [{'kw_id': km.kw.kw_id, 'word': km.kw.word} for km in kwmaplist]

        # Form responses
        response = {
            'node': PageNodeSerializer(node).data, 
            'keywords': kwlist,
            'parents': parents, 
            'children': children }

        return JSONResponse(request, response)


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
    kwmaplist = KWMap.objects.filter(node=node)
    kwstring = ';'.join([km.kw.word for km in kwmaplist])
    context['keywords'] = kwstring
    if node.kind == 'thm':
        return render(request, 'prooftree/change_theorem.html', context)
    elif node.kind == 'pf':
        theorem = DAG.objects.filter(child_id=node_id).filter(dep_type='prove')
        if (theorem != []) and (len(theorem) == 1):
            context['about_theorem'] = get_object_or_404(Node, pk=theorem[0].parent_id)
            return render(request, 'prooftree/change_article.html', context)
    return HttpResponse("Error: Node type invalid", status=404)

def submit_change(request, node_id):
    node = get_object_or_404(Node, pk=node_id)
    node.title = request.POST['title']
    node.statement = request.POST['body']
    node.last_modified = datetime.now()
    node.save()
    DAG.objects.filter(child_id=node_id).delete()
    KWMap.objects.filter(node=node).delete()
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
    kwstr = request.POST['keyword']
    kwlist = [i.strip() for i in kwstr.split(';')]
    for kw in kwlist:
        if kw != '':
            if len(Keyword.objects.filter(word=kw)) == 0:
                k = Keyword(word=kw)
                k.save()
            else:
                k = Keyword.objects.get(word=kw)
            kwmap = KWMap(node=node, kw=k)
            kwmap.save()
    newevent = Event(node=node, event_type='modified')
    if request.user.is_authenticated():
        newevent.user = request.user
    else:
        newevent.user = authenticate(username="socialmathghostuser", password="socialmathghostuser2014")
    newevent.save()
    return detail(request, node_id)

def submit_article(request):
    article_title = request.POST['title']
    theorem = get_object_or_404(Node, pk=int(request.POST['theorem']))
    body = request.POST['body']
    newnode = Node(kind='pf', title=article_title, statement=body, last_modified=datetime.now())
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
    kwstr = request.POST['keyword']
    kwlist = [i.strip() for i in kwstr.split(';')]
    for kw in kwlist:
        if kw != '':
            if len(Keyword.objects.filter(word=kw)) == 0:
                k = Keyword(word=kw)
                k.save()
            else:
                k = Keyword.objects.get(word=kw)
            kwmap = KWMap(node=newnode, kw=k)
            kwmap.save()
    newevent = Event(node=newnode, event_type='added')
    if request.user.is_authenticated():
        newevent.user = request.user
    else:
        newevent.user = authenticate(username="socialmathghostuser", password="socialmathghostuser2014")
    newevent.save()
    return detail(request, newnode.node_id)

def submit_theorem(request):
    theorem_title = request.POST['title']
    body = request.POST['body']
    newnode = Node(kind='thm', title=theorem_title, statement=body, last_modified=datetime.now())
    newnode.save()
    deps = []
    for i in range(9):
        dep = request.POST['lemma' + str(i)]
        if (dep != "blank") and (int(dep) not in deps):
            deps.append(int(dep))
            new_dag = DAG(parent=get_object_or_404(Node, pk=int(dep)), child=newnode, dep_type='all')
            new_dag.save()
    kwstr = request.POST['keyword']
    kwlist = [i.strip() for i in kwstr.split(';')]
    for kw in kwlist:
        if kw != '':
            if len(Keyword.objects.filter(word=kw)) == 0:
                k = Keyword(word=kw)
                k.save()
            else:
                k = Keyword.objects.get(word=kw)
            kwmap = KWMap(node=newnode, kw=k)
            kwmap.save()
    newevent = Event(node=newnode, event_type='added')
    if request.user.is_authenticated():
        newevent.user = request.user
    else:
        newevent.user = authenticate(username="socialmathghostuser", password="socialmathghostuser2014")
    newevent.save()
    return detail(request, newnode.node_id)

def lookup_keyword(request, kw_id):
    context = {}
    kw = get_object_or_404(Keyword, pk=kw_id)
    context['search'] = kw.word
    context['nodes'] = [km.node for km in KWMap.objects.filter(kw=kw)]
    context['numresults'] = len(context['nodes'])
    return {'request':request, 'context':context}

def keyword_render(request, kw_id):
    rc = lookup_keyword(request, kw_id)
    return render(rc['request'], "prooftree/search.html", rc['context'])

def search(request):
    searchtext = str(request.GET['searchtext'])
    searchtext = ' '.join(searchtext.split('+'))
    context = {'search':searchtext}
    kwlst = [w.strip() for w in searchtext.split(',')]
    # # kwlst = [''] when searchtext = ''
    #
    # if len(kwlst) == 0:
    #     print(request)
    #     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if len(kwlst) == 1:
        kw = Keyword.objects.filter(word__exact=kwlst[0])
        if kw:
            return lookup_keyword(request, kw[0].kw_id)
        else:
            context['numresults'] = 0
            return {'request': request, 'context': context}
    else:
        kwmaplist = KWMap.objects.all()
        for word in kwlst:
            try:
                kw = Keyword.objects.get(word__exact=word)
            except Keyword.ObjectDoesNotExist:
                context['numresults'] = 0
                return {'request': request, 'context': context}
            kwmaplist = kwmaplist.filter(kw=kw)
        context['nodes'] = [km.node for km in kwmaplist]
        context['numresults'] = len(context['nodes'])
        return {'request': request, 'context': context}

def search_render(request):
    rc = search(request)
    return render(rc['request'], 'prooftree/search.html', rc['context'])

def search_json(request):
    context = search(request)['context']
    response = {
        'keyword': context['search'], 
        'nodes': []
    }

    if context.has_key('nodes'):
        for node in context['nodes']:
            serializer = PageNodeSerializer(node, 
                fields=('node_id', 'kind', 'title', 'pub_time'))
            response['nodes'].append(serializer.data)

    return JSONResponse(request, response)

def show_signup(request, errno):
    if request.user.is_authenticated():
        return view_logout(request, 2)
    if (int(errno) != 0):
        context = {"errno": errno}
    else:
        context = {}
    return render(request, 'prooftree/register.html', context)

def signup(request):
    uname = request.POST['username']
    if (uname == ""):
        return show_signup(request, 1)
    if len(User.objects.filter(username=uname)) != 0:
        return show_signup(request, 2)
    passwd = request.POST['password']
    cpasswd = request.POST['confirm_password']
    if passwd == "" or passwd != cpasswd:
        return show_signup(request, 3)
    email = request.POST['email']
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    newuser = User.objects.create_user(uname, email, passwd)
    newuser.last_name = last_name
    newuser.first_name = first_name
    newuser.save()
    newuser = authenticate(username=uname, password=passwd)
    login(request, newuser)
    return render(request, 'prooftree/signup_success.html', {'newuser':newuser})

def show_login(request, errno):
    if int(errno) != 0:
        context = {'errno': errno}
    else:
        context = {}
    if request.user.is_authenticated():
        logout(request)
    return render(request, 'prooftree/login.html', context)

def view_login(request):
    uname = request.POST['username']
    passwd = request.POST['password']
    user = authenticate(username=uname, password=passwd)
    if user is not None:
        login(request, user)
        request.user = user
        return index(request)
    else:
        return show_login(request, 1)

def view_logout(request, mode):
    if mode == 2:
        return render(request, 'prooftree/confirm_logout.html')
    logout(request)
    return index(request)

def change_passwd(request, errno):
    if int(errno) != 0:
        context = {'errno': errno}
    else:
        context = {}
    if not request.user.is_authenticated():
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, '/prooftree/change_passwd.html', context)

def submit_passwd(request):
    if request.POST['old_password'] != request.user.password:
        return change_passwd(request, 1)
    elif request.POST['new_password'] != request.POST['confirm_password']:
        return change_passwd(request, 2)
    request.user.set_password(request.POST['new_password'])
    request.user.save()
    return render(request, '/prooftree/submit_passwd.html')

def profile_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    context = {'user': user}
    history = Event.objects.get_userhistory(user).order_by('-pub_time')
    context['history'] = history
    following = Event.objects.get_userfollowing(user)
    context['following'] = following
    return render(request, 'prooftree/profile.html', context)

def self_profile(request):
    if request.user.is_authenticated():
        return profile_detail(request, request.user.id)

def follow(request, node_id):
    node = get_object_or_404(Node, pk=node_id)
    if request.user.is_authenticated():
        new_event = Event(node=node, user=request.user, event_type='followed')
        new_event.save()
    return HttpResponseRedirect('/prooftree/get/one/' + str(node_id) + '/')

def unfollow(request, node_id):
    node = get_object_or_404(Node, pk=node_id)
    if request.user.is_authenticated():
        Event.objects.filter(node=node).filter(user=request.user).filter(event_type='followed').delete()
    return HttpResponseRedirect('/prooftree/get/one/' + str(node_id) + '/')
