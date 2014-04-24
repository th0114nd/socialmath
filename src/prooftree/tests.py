from django.test import TestCase
from django.utils import unittest
from django.test.client import Client
from prooftree.models import *
import json

class NodeTestCase(unittest.TestCase):
    ''' Unit test for Node model'''
    @classmethod
    def setUpClass(cls):
        for i in range(100):
            obj = Node.objects.create(kind="thm", statement=str(i))
            if i == 99:
                cls.max_id = obj.node_id

    @classmethod
    def tearDownClass(cls):
        Node.objects.all().delete()

    def test_max_nodes(self):
        ''' Test whether Node model can get the largest primary key. '''
        self.assertEqual(Node.objects.max_nodes(), 100)
        Node.objects.get(node_id=NodeTestCase.max_id).delete()
        self.assertEqual(Node.objects.max_nodes(), 99)

    def test_max_pageno(self):
        ''' Test whether Node model can get the corret page number. '''
        self.assertEqual(Node.objects.max_pageno(), 1)
        Node.objects.create(kind="thm", statement="additional one")
        self.assertEqual(Node.objects.max_pageno(), 2)



class DAGTestCase(unittest.TestCase):
    ''' Unit test for DAG model'''
    @classmethod
    def setUpClass(cls):
        # Create nodes
        cls.thm = Node.objects.create(kind="thm", statement="Theorem 1")
        cls.pf_1 = Node.objects.create(kind="pf", statement="Proof of theorem 1")
        cls.pf_2 = Node.objects.create(kind="pf", statement="Another proof of theorem 1")
        cls.thm_2 = Node.objects.create(kind="thm", statement="Theorem 2")
        cls.ax_3 = Node.objects.create(kind="ax", statement="Axiom 3")
        cls.thm_4 = Node.objects.create(kind="thm", statement="Theorem 4")

        # Save the relations
        DAG.objects.create(parent=cls.thm, child=cls.pf_1, dep_type='any')
        DAG.objects.create(parent=cls.thm, child=cls.pf_2, dep_type='any')
        DAG.objects.create(parent=cls.thm, child=cls.thm_2, dep_type='all')
        DAG.objects.create(parent=cls.thm, child=cls.ax_3, dep_type='all')
        DAG.objects.create(parent=cls.thm_2, child=cls.thm_4, dep_type='all')

    @classmethod
    def tearDownClass(cls):
        Node.objects.all().delete()
        DAG.objects.all().delete()

    def test_get_parents(self):
        ''' Test method DAG.objects.get_parents(node_id). '''
        root_id = DAGTestCase.thm.node_id
        self.assertEqual(list(DAG.objects.get_parents(root_id)), [])
        self.assertEqual(list(DAG.objects.get_parents(DAGTestCase.pf_1.node_id)), [root_id])
        self.assertEqual(list(DAG.objects.get_parents(DAGTestCase.thm_2.node_id)), [root_id])
        self.assertEqual(list(DAG.objects.get_parents(DAGTestCase.ax_3.node_id)), [root_id])
        parent_id = list(DAG.objects.get_parents(DAGTestCase.thm_4.node_id))[0]
        self.assertEqual(list(DAG.objects.get_parents(parent_id)), [root_id])
                
    def test_get_children(self):
        ''' Test method DAG.objects.get_children(node_id). '''
        root_id = DAGTestCase.thm.node_id
        thm4_id = DAGTestCase.thm_4.node_id
        self.assertEqual(len(list(DAG.objects.get_children(root_id))), 4)
        self.assertEqual(list(DAG.objects.get_children(DAGTestCase.thm_2.node_id)), [thm4_id])


class KeywordTestCase(unittest.TestCase):
    ''' Unit test for Keyword model'''
    @classmethod
    def setUpClass(cls):
        # Create nodes
        cls.thm = Node.objects.create(kind="thm", statement="Theorem 1")
        cls.thm_2 = Node.objects.create(kind="thm", statement="Theorem 2")
        cls.ax_3 = Node.objects.create(kind="ax", statement="Axiom 3")
        # Create keywords
        cls.kw_1 = Keyword.objects.create(word="kw_1")
        cls.kw_2 = Keyword.objects.create(word="kw_2")
        cls.kw_3 = Keyword.objects.create(word="kw_3")

        # Save the relations
        KWMap.objects.create(node=cls.thm, kw=cls.kw_1)
        KWMap.objects.create(node=cls.thm, kw=cls.kw_2)
        KWMap.objects.create(node=cls.thm_2, kw=cls.kw_1)
        KWMap.objects.create(node=cls.thm_2, kw=cls.kw_3)
        KWMap.objects.create(node=cls.ax_3, kw=cls.kw_3)

    @classmethod
    def tearDownClass(cls):
        Node.objects.all().delete()
        Keyword.objects.all().delete()
        KWMap.objects.all().delete()

    def test_get_keywords(self):
        ''' Test method Keyword.objects.get_keywords(node_id) '''
        self.assertEqual(list(Keyword.objects.get_keywords(KeywordTestCase.thm.node_id)), \
            ['kw_1', 'kw_2'])
        self.assertEqual(list(Keyword.objects.get_keywords(KeywordTestCase.thm_2.node_id)), \
            ['kw_1', 'kw_3'])
        self.assertEqual(list(Keyword.objects.get_keywords(KeywordTestCase.ax_3.node_id)), \
            ['kw_3'])
                
    def test_get_related(self):
        ''' Test method Keyword.objects.get_related(keyword) '''
        self.assertEqual(len(list(Keyword.objects.get_related('kw_1'))), 2)
        self.assertEqual(len(list(Keyword.objects.get_related('kw_2'))), 1)
        self.assertEqual(len(list(Keyword.objects.get_related('kw_3'))), 2)


class ProoftreeViewsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        # Create nodes
        cls.thm = Node.objects.create(kind="thm", statement="Theorem 1")
        cls.pf_1 = Node.objects.create(kind="pf", statement="Proof of theorem 1")
        cls.pf_2 = Node.objects.create(kind="pf", statement="Another proof of theorem 1")
        cls.thm_2 = Node.objects.create(kind="thm", statement="Theorem 2")
        cls.ax_3 = Node.objects.create(kind="ax", statement="Axiom 3")

        # Save the relations
        DAG.objects.create(parent=cls.thm, child=cls.pf_1, dep_type='any')
        DAG.objects.create(parent=cls.thm, child=cls.pf_2, dep_type='any')
        DAG.objects.create(parent=cls.thm, child=cls.thm_2, dep_type='all')
        DAG.objects.create(parent=cls.thm, child=cls.ax_3, dep_type='all')

    @classmethod
    def tearDownClass(cls):
        Node.objects.all().delete()
        DAG.objects.all().delete()

    def test_detail(self):
        max_id = Node.objects.max_id()
        # Test for response code 404: invalid id
        response = GetTestCase.client.get('/prooftree/get/one/' \
            + str(max_id + 1) + '/')
        self.assertEqual(response.status_code, 404)

        # Test for response code 410: deleted id
        delete_id = GetTestCase.thm_2.node_id
        Node.objects.get(node_id=delete_id).delete()
        DAG.objects.filter(child_id=delete_id).delete()
        DAG.objects.filter(parent_id=delete_id).delete()
        response = GetTestCase.client.get('/prooftree/get/one/' \
            + str(delete_id) + '/')
        self.assertEqual(response.status_code, 410)

        # Test for response code 200: id found
        root_id = GetTestCase.thm.node_id
        response = GetTestCase.client.get('/prooftree/get/one/' \
            + str(root_id) + '/')
        self.assertEqual(response.status_code, 200)
        # Check for response
        json_resp = json.loads(response.content)
        self.assertEqual(len(json_resp["neighbors"]), 3)
        self.assertEqual(json_resp["neighbors"][0]["id"], \
            GetTestCase.pf_1.node_id)
        self.assertEqual(json_resp["neighbors"][0]["above_neighbors"], [])
        self.assertEqual(json_resp["neighbors"][1]["above_neighbors"], [])
        self.assertEqual(json_resp["neighbors"][2]["above_neighbors"], [])

        self.assertEqual(len(json_resp["wanted"]["bodies"]), 2)
        self.assertEqual(json_resp["wanted"]["bodies"][0]["proof_id"], \
            GetTestCase.pf_1.node_id)
        self.assertEqual(json_resp["wanted"]["bodies"][0]["below_neighbors"], \
            [root_id])
        self.assertEqual(json_resp["wanted"]["bodies"][1]["proof_id"], \
            GetTestCase.pf_2.node_id)
        self.assertEqual(json_resp["wanted"]["bodies"][1]["below_neighbors"], \
            [root_id])
