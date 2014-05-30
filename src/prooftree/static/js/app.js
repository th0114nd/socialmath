Prooftree = angular.module('ProoftreeApp', [
  'ui.router',
  'ui.bootstrap',
  'ngCookies'
])

Prooftree.directive('eatClick', function() {
  return function(scope, element, attrs) {
    $(element).click(function(event) {
      event.preventDefault();
    });
  }
})

Prooftree.directive('stopEvent', function () {
  return {
    restrict: 'A',
    link: function (scope, element, attr) {
      element.bind(attr.stopEvent, function (e) {
          e.stopPropagation();
      });
    }
  };
});

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

Prooftree.filter('markdown', function ($sce) {
  var converter = new Showdown.converter();
  return function (value) {
    var html = converter.makeHtml(value || '');
    return $sce.trustAsHtml(html);
  };
});

Prooftree.directive("mathjaxBind", function($sce) {
  return {
    restrict: "A",
    controller: ["$scope", "$element", "$attrs", "$filter",
        function($scope, $element, $attrs, $filter) {
      $scope.$watch($attrs.mathjaxBind, function(value) {
        $element.text(value == undefined ? "" : value);
        // if ($attrs.mathjaxMarkdown == undefined)
        //   $element[0].innerHTML = $sce.trustAsHtml(value == undefined ? "" : value);
        // else
        //   $element[0].innerHTML = $sce.trustAsHtml(value == undefined ? "" : $filter('markdown')(value));

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

Prooftree.provider('greeter2', function($httpProvider) {
  var salutation = 'Hello';
  this.setSalutation = function(s) {
    salutation = s;
  }

  function Greeter(a) {
    this.greet = function() {
      return salutation + ' ' + a;
    }
  }

  this.$get = function(a) {
    return new Greeter(a);
  };
});

Prooftree.config(['$stateProvider', '$urlRouterProvider',
function ($stateProvider, $urlRouterProvider) {
  // For any unmatched url, send to /route1
  // $httpProvider.defaults.xsrfCookieName = 'csrftoken';
  // $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
  // $locationProvider.html5Mode(true);
  $urlRouterProvider.otherwise("/");
  $stateProvider
    .state('index', {
      url: "/?search&center",
      templateUrl: "/static/html/partials/latest.html",
      controller: "LatestCtrl"
    })
    .state('newthm', {
      url: "/newthm?lemma",
      templateUrl: "/static/html/partials/newthm.html",
      controller: "NewThmCtrl"
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
}])

Prooftree.run(function run($http, $cookies) {
  // For CSRF token compatibility with Django
  $http.defaults.headers.post['X-CSRFToken'] = $cookies['csrftoken'];
  // console.log($cookies['csrftoken']);
});

Prooftree.factory('TokenService', function($cookies) {
  return function (param) {
    param['csrfmiddlewaretoken'] = $cookies['csrftoken'];
    return param;
  };
});

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

JSON_CALLBACK = function (data) { return data; };

Prooftree.factory('GetServiceRemote', function($http) {
  var domain = 'http://socialmath-env-6bvqmbhmpe.elasticbeanstalk.com/';
  // var domain = '/';
  var callback = '?callback=JSON_CALLBACK';

  return {

    'brief': function(page) {
      page = typeof page !== 'undefined' ? page : 1;
      return $http.jsonp(domain + 'prooftree/get/brief/' + page + callback)
        .then(function(result) {
          return result.data;
        });
    }, 

    'detail': function(node_id) {
      return $http.jsonp(domain + 'prooftree/get/detail/' + node_id + callback)
        .then(function(result) {
          return result;
        });
    }, 

    'search': function(searchtext) {
      return $http.jsonp(domain + 'prooftree/searchj/' + callback,
          { params: {'searchtext': searchtext} }
        )
        .then(function(result) {
          return result;
        });
    }, 

    'latest': function() {
      return $http.jsonp(domain + 'prooftree/get/latest/' + callback)
        .then(function(result) {
          return result.data;
        });
    }
  }
})

Prooftree.controller('NewThmCtrl', [
'$http', '$scope', '$window', '$state', '$stateParams', 'GetService', 'TokenService', 
function ($http, $scope, $window, $state, $stateParams, GetService, TokenService) {
  NewThmCtrl = this;
  var scope = $scope;

  scope.lemmas = [];

  scope.briefs = [];

  scope.load = function () { 
    GetService.brief().then(function(response) {
      scope.briefs = response.data;
      // console.log(scope.briefs);
      if ($stateParams.lemma) {
        var lemmas = $stateParams.lemma.split(",");
        angular.forEach(scope.briefs, function (item) {
          if (lemmas.indexOf(String(item.node_id)) != -1)
            scope.lemmas.push(item);
        });
      }
    });
  };

  scope.load();

  scope.notAdded = function (lemma) {
    return scope.lemmas.indexOf(lemma) == -1;
  };

  scope.searchMatch = function (lemma) {
    scope.lemmas.push(lemma);
    scope.searchLemma = undefined;
  };

  scope.back = function () {
    $window.history.back();
  };

  // console.log(TokenService({}));

  // csrfmiddlewaretoken: Waeyu1yRFCUM13rUYUDIk1ZFa6Wo3Gcz
  scope.submit = function () {
    var params = {
      title: scope.title,
      body: scope.body,
      keyword: scope.keyword
    };

    for (var i = 0; i < scope.lemmas.length; i++) {
      params['lemma' + i] = scope.lemmas[i].node_id;
    };

    // console.log(params);

    $http.post('/prooftree/submit_theoremj/', TokenService(params))
      .then(function (response) {
        // console.log(response.data.node_id);
        $state.go('index', {center: response.data.node_id});
      }, function(reason) {
        console.log('Failed: ');
        console.log(reason.data);
      }
    );
  };

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
      .charge(-700)
      .linkDistance(120)
      .linkStrength(0.2)
      .size([width, height]);
  };

  var tick = function (graph, scope) {
    return function tick(e) {
      // Push different nodes in different directions for clustering.
      var k = 20 * e.alpha;
      var nodes = graph.vertices;
      var links = graph.arrows;

      // nodes.forEach(function(o, i) {
      //   if (o.free)
      //     o.y -= k;
      // });

      links.forEach(function(o, i) {
        var s = o.source;
        var t = o.target;
        var dy = 1 - (s.y - t.y) / 200;
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

      var visited;

      if (typeof center == 'undefined') {
        visited = Array.apply(null, 
          new Array(graph.nodes.length)).map(Boolean.prototype.valueOf,true);

        graph.vertices = graph.nodes;

        for (var i = 0; i < graph.vertices.length; i++) {
          graph.vertices[i].depth = 0;
        };
      } else {
        var toVisit = [this.id2Pos[center]];

        visited = Array.apply(null, 
          new Array(graph.nodes.length)).map(Boolean.prototype.valueOf,false);

        graph.vertices = [];

        graph.nodes[toVisit[0]].depth = 0;
        visited[toVisit[0]] = true;

        while (toVisit.length) {
          var idx = toVisit.shift();
          var node = graph.nodes[idx];
          
          node.free = true;
          graph.vertices.push(node);

          var adjs = node.parent_ids.concat(node.child_ids);

          for (var i = 0; i < adjs.length; i++) {
            var adjI = this.id2Pos[adjs[i]];
            var adjN = graph.nodes[adjI];

            if (!visited[adjI] && node.depth < depth) {
              visited[adjI] = true;
              toVisit.push(adjI);
              adjN.depth = node.depth + 1;
            }
          };
        }
      }

      graph.arrows = [];

      for (var i = 0; i < graph.vertices.length; i++) {
        var links = graph.vertices[i].parent_ids;
        for (var j = 0; j < links.length; j++) {
          var t = graph.id2Pos[links[j]];
          if (t != undefined && visited[t]) {
            graph.arrows.push({
              'source': graph.vertices[i], 
              'target': graph.nodes[t]});
            graph.vertices[i].free = false;
            graph.nodes[t].free = false;
          }
        }
      }
      // console.log('Graph:\n')
      // console.log(graph);
    };
  };

  var Graph = function (nodes) {
    this.id2Pos = {};

    this.nodes = [];
    // this.edges = [];
    this.vertices = [];
    this.arrows = [];
    this.opacity = function (node) {
      if (node.depth)
        return window.Math.exp(-0.2 * node.depth);
      else
        return 1;
    };

    this.bind = function (scope, model, dimensions) {
      watch(this)(scope, model, dimensions);
    };

    this.explore = explore(this);

    for (var i = 0; i < nodes.length; i++) {
      this.id2Pos[nodes[i].node_id] = i;
      this.nodes.push(nodes[i]);
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
 '$window', '$interval', '$state', 'GetService', 'GraphService',
function ($scope, $rootScope, $modal, $stateParams, $location, $anchorScroll, 
          $window, $interval, $state, GetService, GraphService) {
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
      scope.hideGraph = true;
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

  scope.nodeAction = 0;

  scope.nodeActions = [
    {
      name: 'Preview', 
      action: scope.showDetail
    },
    {
      name: 'Detail', 
      action: function (node_id) {
        $window.location.href = '/prooftree/get/one/' + node_id;
      }
    },
    {
      name: 'Recenter', 
      action: function (node_id) {
        scope.graphCenter = node_id;
        scope.graphShowAll = false;
        scope.exploreGraph(scope.graphCenter, scope.graphDepth);
      }
    },
    {
      name: 'Add child',
      action: function (node_id) {
        $state.go('newthm', {lemma: node_id});
      }
    },
    {
      name: 'Console log', 
      action: function (node_id) {
        GetService.detail(node_id).then(function(response) {
          console.log(response);
        });
      }
    }
  ];

  scope.nodeClick = function (nid) {
    scope.nodeActions[scope.nodeAction].action(nid);
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
  scope.graphCenter = undefined;
  scope.graphDepth = 1;
  scope.graphShowAll = false;
  scope.hasGraph = false;
  scope.hideGraph = false;

  scope.graphOffset = [0, 0];
  scope.graphMomentum = [0, 0];

  scope.graphZoom = 1;
  scope.graphDilation = 0;

  scope.scrollArrows = [
    {rot:   0, offset: [-1,  0]},
    {rot:  90, offset: [ 0, -1]},
    {rot: 180, offset: [ 1,  0]},
    {rot: 270, offset: [ 0,  1]}
  ];

  scope.resetZoom = function () {
    scope.graphOffset[0] /= scope.graphZoom;
    scope.graphOffset[1] /= scope.graphZoom;
    scope.graphZoom = 1;
  }

  scope.setMomentum = function (p) {
    scope.graphMomentum = p;
    console.log(p);
  };

  scope.scrollGraph = function (speedT, speedS) {
    return function () {
      if (scope.graphMomentum[0] || scope.graphMomentum[1]) {
        scope.graphOffset[0] += scope.graphMomentum[0] * speedT;
        scope.graphOffset[1] += scope.graphMomentum[1] * speedT;
      }

      if (scope.graphDilation) {
        var z = Math.exp(speedS * scope.graphDilation);
        scope.graphOffset[0] *= z;
        scope.graphOffset[1] *= z;
        scope.graphZoom *= z;
      }
      // console.log(scope.graphOffset);
    };
  };

  $interval(scope.scrollGraph(5, 0.02), 40, 0, true);

  scope.width = 800;
  scope.height = 800;

  GetService.brief().then(function(response) {
    scope.graph = new GraphService.Graph(response.data);
    scope.graph.bind(
      scope, 
      "graph", 
      [scope.width, scope.height]);
    
    scope.exploreGraph = function (nid, depth, jump) {
      depth = typeof depth !== 'undefined' ? depth : 1;

      scope.graphCenter = nid;
      scope.graph.explore(nid, depth);
      scope.hasGraph = true;
      scope.hideGraph = false;
      scope.graphOffset = [0, 0];

      if (jump) {
        $location.hash('graph-area');
        $anchorScroll();
      }
    };

    scope.graph.explore();

    scope.globalGraph = function () {
      scope.graph.explore();
    };

    scope.toggleShowAll = function (showAll) {
      if (showAll)
        scope.globalGraph();
      else
        scope.exploreGraph(scope.graphCenter, scope.graphDepth);
    };

    scope.setDepth = function (depth) {
      if (depth < 0)
        depth = 0;
      scope.graphDepth = depth;

      if (!scope.graphShowAll)
        scope.exploreGraph(scope.graphCenter, scope.graphDepth);
    };

    if ($stateParams.center) {
      scope.exploreGraph($stateParams.center, 1, true);
    }
  
    scope.latestNum = 5;
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

