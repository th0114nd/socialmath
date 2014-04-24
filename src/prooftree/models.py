from django.db import models
from django.db.models import Avg, Max, Min
import datetime
from django.utils.timezone import utc



''' Create the following tables:
CREATE TABLE "prooftree_node" (
    "node_id" integer NOT NULL PRIMARY KEY,
    "kind" varchar(3) NOT NULL,
    "title" varchar(100),
    "statement" text NOT NULL,
    "pub_time" datetime NOT NULL
)
;
CREATE TABLE "prooftree_dag" (
    "id" integer NOT NULL PRIMARY KEY,
    "parent_id" integer NOT NULL REFERENCES "prooftree_node" ("node_id"),
    "child_id" integer NOT NULL REFERENCES "prooftree_node" ("node_id"),
    "dep_type" varchar(3) NOT NULL
)
;
CREATE TABLE "prooftree_keyword" (
    "kw_id" integer NOT NULL PRIMARY KEY,
    "word" varchar(100) NOT NULL
)
;
CREATE TABLE "prooftree_kwmap" (
    "id" integer NOT NULL PRIMARY KEY,
    "node_id" integer NOT NULL REFERENCES "prooftree_node" ("node_id"),
    "kw_id" integer NOT NULL REFERENCES "prooftree_keyword" ("kw_id")
)
;

'''

# Custom manager for DAG relations
class NodeManager(models.Manager):
    # Usage: Node.objects.max_id()
    # Return: maximum primary key
    def max_id(self):
        return self.all().aggregate(Max('node_id'))['node_id__max'] - \
               self.all().aggregate(Min('node_id'))['node_id__min'] + 1

    # Usage: Node.objects.max_pageno() 
    # Return: maximum page number, assuming we are loading 100
    #         entries per page
    def max_pageno(self):
        return (self.max_id() - 1) / 100 + 1;


# Custom manager for DAG relations
class DAGManager(models.Manager):
    # Usage: DAG.objects.get_children(node_id)
    # Return: [child_id1, child_id2, ...]
    def get_children(self, node_id):
        return self.filter(parent=node_id).values_list('child_id', flat=True)

    # Usage: DAG.objects.get_parents(node_id)
    # Return: [parent_id1, parent_id2, ...]
    def get_parents(self, node_id):
        return self.filter(child=node_id).values_list('parent_id', flat=True)


# Custom manager for Keyword class
class KWManager(models.Manager):
    # Usage: Keyword.objects.get_related(keyword)
    # Return: List of node_id for theorems tagged with keyword
    def get_related(self, keyword):
        kw = Keyword.objects.filter(word__exact=keyword)
        return KWMap.objects.filter(kw=kw).values_list('node_id', flat=True)

    # Usage: Keyword.objects.get_keywords(node_id)
    # Return: List of keywords for the theorems
    def get_keywords(self, node_id):
        kw_ids = list(KWMap.objects.filter(node_id=node_id).values_list('kw_id', flat=True))
        keywords = []
        for kw_id in kw_ids:
            keywords.append(Keyword.objects.get(kw_id=kw_id).word)
        return keywords


# Entity for a node in DAG. 
class Node(models.Model):
    TYPES = (
        ('thm', 'Theorem'),
        ('ax', 'Axiom'),
        ('def', 'Definition'),
        ('pf', 'Proof'),
    )
    node_id = models.AutoField(primary_key=True)
    kind = models.CharField(max_length=3, choices=TYPES)
    title = models.CharField(max_length=100, null=True)
    statement = models.TextField()
    pub_time = models.DateTimeField(auto_now_add=True)
    objects = NodeManager() 

    def __str__kind(self):
        return self.title        


# Adjacency list of nodes in the DAG
class DAG(models.Model):
    TYPES = (
        ('any', 'any'),
        ('all', 'all'),
    )
    parent = models.ForeignKey(Node, related_name="parent_id")
    child = models.ForeignKey(Node, related_name="child_id")
    dep_type = models.CharField(max_length=3, choices=TYPES)
    objects = DAGManager() 

# Entity for keywords
class Keyword(models.Model):
    kw_id = models.AutoField(primary_key=True)
    word = models.CharField(max_length=100)
    objects = KWManager() 

# Many to many mapping between nodes and keywords
class KWMap(models.Model):
	node = models.ForeignKey(Node)
	kw = models.ForeignKey(Keyword)


