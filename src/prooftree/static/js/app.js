function Node(id, type, title, depends, body) {
  this.id = id;
  this.type = type;
  this.title = title;
  this.depends = depends;
  this.body = body;
};

Prooftree = angular.module('ProoftreeApp', [
  'ui.router',
  'ui.bootstrap'
])

Prooftree.directive('eatClick', function() {
  return function(scope, element, attrs) {
    $(element).click(function(event) {
      event.preventDefault();
    });
  }
})

Prooftree.directive('chevronIcon', function() {
  return {
    restrict: 'A',
    scope: {
      show: '=chevronIcon'
    },
    templateUrl: '/static/html/partials/chevronIcon.html'
  };
})

Prooftree.directive('draggable', DragDirective);

Prooftree.directive('draggable2', function($document) {
  return function(scope, element, attr) {
    var startX = 0, startY = 0, x = 0, y = 0;
    element.css({
     position: 'relative',
     // border: '1px solid red',
     // backgroundColor: 'lightgrey',
     cursor: 'pointer'
    });
    element.on('mousedown', function(event) {
      // Prevent default dragging of selected content
      event.preventDefault();
      startX = event.screenX - x;
      startY = event.screenY - y;
      $document.on('mousemove', mousemove);
      $document.on('mouseup', mouseup);
    });

    function mousemove(event) {
      y = event.screenY - startY;
      x = event.screenX - startX;
      element.css({
        top: y + 'px',
        left:  x + 'px'
      });
    }

    function mouseup() {
      $document.off('mousemove', mousemove);
      $document.off('mouseup', mouseup);
    }
  };
});

Prooftree.directive("mathjaxBind", function() {
  return {
    restrict: "A",
    controller: ["$scope", "$element", "$attrs",
        function($scope, $element, $attrs) {
      $scope.$watch($attrs.mathjaxBind, function(value) {
        $element.text(value == undefined ? "" : value);
        MathJax.Hub.Queue(["Typeset", MathJax.Hub, $element[0]]);
      });
    }]
  };
});

Prooftree.filter('ellipsis', function () {
  return function (input, len) {
    if (input.length < len)
      return input;
    else
      return input.slice(0, len - 3) + "...";
  }
});

Prooftree.config(function ($stateProvider, $urlRouterProvider) {
    // For any unmatched url, send to /route1
    $urlRouterProvider.otherwise("/");
    $stateProvider
        .state('index', {
            url: "/?search",
            templateUrl: "/static/html/partials/latest.html",
            controller: "LatestCtrl"
        })
        .state('brief', {
            url: "/brief",
            templateUrl: "/static/html/partials/brief.html",
            controller: "BriefCtrl"
        })
        .state('graph', {
            url: "/graph",
            templateUrl: "/static/html/partials/graph.html",
            controller: "GraphCtrl"
        })
})

Prooftree.factory('GetService', function($http) {
  return {

    'brief': function(page) {
      page = typeof page !== 'undefined' ? page : 1;
      return $http.get('/prooftree/get/brief/' + page)
        .then(function(result) {
          return result.data;
        });
    }, 

    'detail': function(node_id) {
      return $http.get('/prooftree/get/detail/' + node_id)
        .then(function(result) {
          return result;
        });
    }, 

    'search': function(searchtext) {
      return $http.get('/prooftree/searchj/',
          { params: {'searchtext': searchtext} }
        )
        .then(function(result) {
          return result;
        });
    }, 

    'latest': function() {
      return $http.get('/prooftree/get/latest/')
        .then(function(result) {
          return result.data;
        });
    }
  }
})

function Node(id, type, title, depends, body) {
  this.id = id;
  this.type = type;
  this.title = title;
  this.depends = depends;
  this.body = body;
};

Prooftree.controller('UserCtrl', ['$rootScope', '$scope', 'GetService',
function ($rootScope, $scope, GetService) {

}])

Prooftree.controller('GraphCtrl', ['$scope', 'GetService', 'GraphService',
function ($scope, GetService, GraphService) {
  GraphCtrl = this;
  var scope = $scope;

  scope.graph = new GraphService.Graph([]);

  scope.width = 500;
  scope.height = 500;

  GetService.brief().then(function(response) {
    scope.graph = new GraphService.Graph(response.data);
    scope.graph.bind(scope, "graph", [scope.width, scope.height]);
    scope.graph.explore();
  });

  scope.showDetail = function showDetail(node) {
    window.alert(node);
  };

}])

Prooftree.factory('GraphService', function () {
  var color = d3.scale.category10()

  var colorDict = {
    'ax':   color(0),
    'def':  color(1),
    'thm':  color(2),
    'pf':   color(3)
  };

  var Node = function Node(id, kind, title, depends, body) {
    this.id = id;
    this.kind = kind;
    this.title = title;
    this.depends = depends;
    this.body = body;
  };

  var force = function (width, height) {
    return d3.layout.force()
      .charge(-500)
      .linkDistance(120)
      .linkStrength(0.1)
      .size([width, height]);
  };

  var tick = function (graph, scope) {
    return function tick(e) {
      // Push different nodes in different directions for clustering.
      var k = 6 * e.alpha;
      var nodes = graph.vertices;
      var links = graph.arrows;

      nodes.forEach(function(o, i) {
        if (o.free)
          o.y -= k;
      });

      links.forEach(function(o, i) {
        var s = o.source;
        var t = o.target;
        var dy = 1 - (s.y - t.y) / 300;
        s.y += k * dy;
        t.y -= k * dy;
      });

      scope.$apply();
    };
  };

  var watch = function (graph) {
    return function(scope, model, dimensions) {
      scope.$watchCollection(model, function(newValue) {
      var nodes = newValue.vertices;
      var links = newValue.arrows;

      for(var i = 0; i < links.length ; i++) {
        links[i].strokeWidth = 1;
      }

      for(var i = 0; i < nodes.length ; i++) {
        nodes[i].color = colorDict[nodes[i].kind];
      }

      force(dimensions[0], dimensions[1])
        .nodes(nodes)
        .links(links)
        .on("tick", tick(graph, scope))
        .start();
      });
    };
  };

  var explore = function (graph) { 
    return function (center, depth) {
      depth = typeof depth !== 'undefined' ? depth : 1;

      if (typeof center == 'undefined') {
        graph.vertices = graph.nodes;

        for (var i = 0; i < graph.vertices.length; i++) {
          graph.vertices[i].depth = 0;
        };
      } else {
        var toVisit = [this.id2Pos[center]];
        var visited = Array.apply(null, 
          new Array(graph.nodes.length)).map(Boolean.prototype.valueOf,false);

        graph.vertices = [];
        graph.arrows = [];

        graph.nodes[toVisit[0]].depth = 0;

        while (toVisit.length) {
          var idx = toVisit.shift();
          var node = graph.nodes[idx];

          if (node.depth > depth)
            break;

          visited[idx] = true;
          node.free = true;
          graph.vertices.push(node);

          var adjs = node.parent_ids.concat(node.child_ids);

          for (var i = 0; i < adjs.length; i++) {
            var adjI = this.id2Pos[adjs[i]];
            var adjN = graph.nodes[adjI];
            if (!visited[adjI]) {
              toVisit.push(adjI);
              adjN.depth = node.depth + 1;
            }
          };
        }
      }

      for (var i = 0; i < graph.vertices.length; i++) {
        var links = graph.vertices[i].parent_ids;
        for (var j = 0; j < links.length; j++) {
          var t = graph.id2Pos[links[j]];
          if (t != undefined) {
            graph.arrows.push({
              'source': graph.vertices[i], 
              'target': graph.nodes[t]});
            graph.vertices[i].free = false;
            graph.nodes[t].free = false;
          }
        }
      }
    };
  };

  var Graph = function (nodes) {
    this.id2Pos = {};

    this.nodes = [];
    this.edges = [];
    this.vertices = [];
    this.arrows = [];
    this.opacity = function (node) {
      if (node.depth)
        return window.Math.exp(-0.5 * node.depth);
      else
        return 1;
    };

    this.bind = function (scope, model, dimensions) {
      watch(this)(scope, model, dimensions);
    };

    this.explore = explore(this);

    // var result = {'nodes': [], 'edges':[], "arrows":[]};

    for (var i = 0; i < nodes.length; i++) {
      this.id2Pos[nodes[i].node_id] = i;
      this.nodes.push(nodes[i]);
    }

    for (var i = 0; i < nodes.length; i++) {
      var links = this.nodes[i].parent_ids;
      for (var j = 0; j < links.length; j++) {
        var t = this.id2Pos[links[j]];
        if (t != undefined) {
          this.edges.push({
            'source': i, 
            'target': t});
          this.edges.push({
            'source': t, 
            'target': i});
        }
      }
    }
  };

  return {
    'Graph': Graph
  }
});

Prooftree.controller('DetailCtrl', ['$scope', 'GetService', 'data',
function ($scope, GetService, data) {
  DetailCtrl = this;
  var scope = $scope;

  scope.node = data.node;
  scope.keywords = data.keywords;
  scope.parents = data.parents;
  scope.children = data.children;
}])

Prooftree.controller('LatestCtrl', 
['$scope', '$rootScope', '$modal', '$stateParams', '$location', '$anchorScroll', 
 'GetService', 'GraphService',
function ($scope, $rootScope, $modal, $stateParams, $location, $anchorScroll, 
          GetService, GraphService) {
  LatestCtrl = this;
  var scope = $scope;

  scope.latest = [];

  scope.searchResult = undefined;

  scope.graphTemplate = '/static/html/partials/graph.html';

  scope.load = function () { 
    GetService.latest().then(function(response) {
      scope.latest = response.data;
    });
  };

  scope.searchSubmit = function (searchtext) {
    GetService.search(searchtext).then(function(response) {
      scope.searchResult = response;
      scope.searchNodes = response.data.nodes;
      scope.hideLatest = true;
      $location.hash('search-area');
      $anchorScroll();
    });
  };

  if ($stateParams.search) {
    scope.searchSubmit($stateParams.search);
  }

  scope.showDetail = function (node_id) { 
    GetService.detail(node_id).then(function(response) {
      openDetail(response);
    });
  };

  var openDetail = function (context) {
    var modalInstance = $modal.open({
      templateUrl: '/static/html/partials/detail_modal.html',
      controller: 'DetailCtrl',
      size: 'lg',
      resolve: {
        data: function () {
          return context.data;
        }
      }
    });
  };

  scope.load();

  scope.graph = undefined;
  scope.hasGraph = false;
  scope.hideGraph = false;

  scope.width = 500;
  scope.height = 500;

  GetService.brief().then(function(response) {
    scope.graph = new GraphService.Graph(response.data);
    scope.graph.bind(
      scope, 
      "graph", 
      [scope.width, scope.height]);
    // scope.graph.explore();
    scope.exploreGraph = function (nid) {
      scope.graph.explore(nid);
      scope.hasGraph = true;
      scope.hideGraph = false;
      $location.hash('graph-area');
      $anchorScroll();
    };
  });
}])

Prooftree.controller('BriefCtrl', ['$scope', '$http', 'GetService', 'GraphService',
function ($scope, $http, GetService, GraphService) {
  BriefCtrl = this;
  var scope = $scope;
  scope.gs = GraphService;

  GetService.brief().then(function(response) {
    scope.pagedata = response;
    scope.graph = GraphService.Graph(scope.pagedata.data);
  });
}])

