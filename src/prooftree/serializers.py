from rest_framework import serializers
from prooftree.models import Node, DAG, Keyword, KWMap

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    '''
    #A ModelSerializer that takes an additional `fields` argument that
    #controls which fields should be displayed.
    '''

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)
                
class PageNodeSerializer(DynamicFieldsModelSerializer):
    ''' Usage: node = Node.objects.get(node_id=id)
               /get/brief
                   NodeSerializer(node, fields = ('node_id', 'kind', 'child_ids')).data
               /get/medium
                   NodeSerializer(node).data
    '''
    child_ids = serializers.SerializerMethodField('get_children')

    def get_children(self, node):
        return DAG.objects.get_children(node.node_id)

    class Meta:
        model = Node
        fields = ('node_id', 'kind', 'statement', 'child_ids')


class ProofSerializer(serializers.Serializer):
    ''' Serializer for proof nodes
        Return: {"proof_id":..., "content":..., "below_neighbors": [...]}
    '''
    proof_id = serializers.CharField(source = "node_id")
    content  = serializers.CharField(source = "statement")
    below_neighbors = serializers.SerializerMethodField('get_parents')

    def get_parents(self, node):
        return DAG.objects.get_parents(node.node_id)


class NodeSerializer(serializers.Serializer):
    ''' Return example:
        {"id":2, "kind":"theorem", "date":"4/17/14",$
                "title":"There is a unique additive inverse",
                "bodies":[{"proof_id":1,$
                           "content":"Assume there are two additive inverses...",$
                           "below_neighbors": [1]},
                          {"proof_id":2,
                           "content": "Z is a ring, therefore...",$
                           "below_neighbors": [1]}]
                "above_neighbors": []}
    '''
    id = serializers.CharField(source = "node_id")
    kind = serializers.CharField(source = "kind")
    date = serializers.CharField(source = "pub_time")
    title = serializers.CharField(source = "title")
    bodies = serializers.SerializerMethodField('get_proof')
    above_neighbors = serializers.SerializerMethodField('get_children')

    def get_children(self, node):
        return DAG.objects.get_children(node.node_id)

    def get_proof(self, node):
        ''' Return: A list of jsons for proofs of this theorem '''
        child_ids = DAG.objects.get_children(node.node_id)
        proofs = []
        for nid in child_ids:
            n = Node.objects.get(node_id=nid)
            if n.kind == 'pf':
                proofs.append(ProofSerializer(n).data)
        return proofs

    

