from django.db import models

''' Create the following tables:
CREATE TABLE "prooftree_node" (
    "node_id" integer NOT NULL PRIMARY KEY,
    "type" integer NOT NULL,
    "title" varchar(100) NOT NULL,
    "statement" text NOT NULL
)
;
CREATE TABLE "prooftree_proof" (
    "pf_id" integer NOT NULL PRIMARY KEY,
    "content" text NOT NULL
)
;
CREATE TABLE "prooftree_prove" (
    "id" integer NOT NULL PRIMARY KEY,
    "node_id" integer NOT NULL REFERENCES "prooftree_node" ("node_id"),
    "pf_id" integer NOT NULL REFERENCES "prooftree_proof" ("pf_id")
)
;
CREATE TABLE "prooftree_dag" (
    "id" integer NOT NULL PRIMARY KEY,
    "parent_id" integer NOT NULL REFERENCES "prooftree_node" ("node_id"),
    "child_id" integer NOT NULL REFERENCES "prooftree_node" ("node_id")
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
# Entity for a node in DAG. A node can be a theorem (type = 0).
# a definition (type = 1).
class Node(models.Model):
	node_id = models.AutoField(primary_key=True)
	type = models.IntegerField()
	title = models.CharField(max_length=100)
	statement = models.TextField()
	def __str__(self):
		return self.title

# Entity for proofs.
class Proof(models.Model):
	pf_id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=100)
	content = models.TextField()
	def __str__(self):
		return self.title

# Mapping between theorem and proofs
class Prove(models.Model):
	node = models.ForeignKey(Node)
	pf = models.ForeignKey(Proof)

# Adjacency list of nodes in the DAG
class DAG(models.Model):
	parent = models.ForeignKey(Node, related_name="parent_id")
	child = models.ForeignKey(Node, related_name="child_id")

# Entity for keywords
class Keyword(models.Model):
	kw_id = models.AutoField(primary_key=True)
	word = models.CharField(max_length=100)

# Mapping between nodes and keywords
class KWMap(models.Model):
	node = models.ForeignKey(Node)
	kw = models.ForeignKey(Keyword)

