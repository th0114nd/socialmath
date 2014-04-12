from django.db import models

''' Create the following tables:
CREATE TABLE "prooftree_node" (
    "node_id" integer NOT NULL PRIMARY KEY,
    "ntype" varchar(3) NOT NULL,
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

# Custom manager for Node class
class NodeManager(models.Manager):
    # Usage: DAG.objects.get_children(parent_id)
    # Return: QuerySet
    def get_children(self, parent_id):
        return self.filter(node_id=parent_id).values('child_id')

    # Usage: DAG.objects.get_parents(child_id)
    # Return: QuerySet
    def get_parents(self, child_id):
        return self.filter(node_id=child_id).values('parent_id')

# Custom manager for Keyword class
class KWManager(models.Manager):
    # Usage: Keyword.objects.get_related(keyword)
    # Return: QuerySet of node_id for theorems tagged with keyword
    def get_related(self, keyword):
        kw_id = self.get(word__exact=Keyword).values()[0]['kw_id']
        return KWMap.objects.filter(kw_id=kw_id).values('node_id')

    # Usage: Keyword.objects.get_keywords(node_id)
    # Return: QuerySet of kw_id for theorems tagged with keyword
    def get_keywords(self, node_id):
        kw = KWMap.objects.filter(node_id=node_id).values('kw_id')
        kw_list = []
        for item in kw:
            kw_list.append(item['kw_id'])
        return self.filter(kw_id_in=kw_list).values('word')

# Entity for a node in DAG. 
class Node(models.Model):
    TYPES = (
        ('thm', 'Theorem'),
        ('ax', 'Axiom'),
        ('def', 'Definition'),
        ('pf', 'Proof'),
    )
    node_id = models.AutoField(primary_key=True)
    ntype = models.CharField(max_length=3, choices=TYPES)
    title = models.CharField(max_length=100, null=True)
    statement = models.TextField()
    pub_time = models.DateTimeField()
    objects = NodeManager() 

    def __str__(self):
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

# Entity for keywords
class Keyword(models.Model):
    kw_id = models.AutoField(primary_key=True)
    word = models.CharField(max_length=100)
    objects = KWManager() 

# Many to many mapping between nodes and keywords
class KWMap(models.Model):
	node = models.ForeignKey(Node)
	kw = models.ForeignKey(Keyword)


# TODOs:
# - Node, proof + pub time
# - Proof -> theorem
# - Get all keywords mapped to a theorem
# - Search theorems by keywords
# - Get all proofs of a theorem
# - Get all children to a node
