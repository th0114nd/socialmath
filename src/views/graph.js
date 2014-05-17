
/*
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
*/

// allNodesDict = 

function Node() {

}

app = angular.module("graphForce", [])

app.controller("graphControl", function($scope, $http) {
    $scope.width = 500;
    $scope.height = 500;

    var color = d3.scale.category20()

    var force = d3.layout.force()
        .charge(-120)
        .linkDistance(30)
        .size([$scope.width, $scope.height]);

    $http.get('miserables.json').success(function(graph) {
        $scope.nodes = graph.nodes;
        $scope.links = graph.links;

        for(var i=0; i < $scope.links.length ; i++){
            $scope.links[i].strokeWidth = Math.round(Math.sqrt($scope.links[i].value))
        }

        for(var i=0; i < $scope.nodes.length ; i++){
            $scope.nodes[i].color = color($scope.nodes[i].group)
        }

        force
            .nodes($scope.nodes)
            .links($scope.links)
            .on("tick", function(){$scope.$apply()})
            .start();
    })
})