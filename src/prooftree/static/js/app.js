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

Prooftree.config(function ($stateProvider, $urlRouterProvider) {
    // For any unmatched url, send to /route1
    $urlRouterProvider.otherwise("/");
    $stateProvider
        .state('index', {
            url: "/",
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

Prooftree.factory('GraphService', function () {
  var Node = function Node(id, kind, title, depends, body) {
    this.id = id;
    this.kind = kind;
    this.title = title;
    this.depends = depends;
    this.body = body;
  };

  var conv = function (nodes) {
    var id2Pos = new Object();
    var result = {'nodes': [], "links":[]};

    for (var i = 0; i < nodes.length; i++) {
      id2Pos[nodes[i].node_id] = i;
      result.nodes.push(nodes[i]);

      nodes[i].free = (nodes[i].parent_ids.length == 0);
    }

    for (var i = 0; i < nodes.length; i++) {
      var links = result.nodes[i].parent_ids;
      for (var j = 0; j < links.length; j++) {
        var t = id2Pos[links[j]];
        result.links.push({
          'source': i, 
          'target': t});
        nodes[t].free = false;
      }
    }

    return result;
  };

  return {
    'conv': conv
  }
});

Prooftree.controller('LatestCtrl', ['$scope', 'GetService', 
function ($scope, GetService) {
  LatestCtrl = this;
  var scope = $scope;

  scope.latest = [];

  scope.load = function () { 
    GetService.latest().then(function(response) {
      scope.latest = response.data;
    });
  };

  scope.load();
}])

Prooftree.controller('BriefCtrl', ['$scope', '$http', 'GetService', 'GraphService',
function ($scope, $http, GetService, GraphService) {
  BriefCtrl = this;
  var scope = $scope;
  scope.gs = GraphService;

  GetService.brief().then(function(response) {
    scope.pagedata = response;
    scope.graph = GraphService.conv(scope.pagedata.data);
  });
}])

Prooftree.controller('GraphCtrl', ['$scope', 'GetService', 'GraphService',
function ($scope, GetService, GraphService) {
  GraphCtrl = this;
  var scope = $scope;

  scope.graph = GraphService.conv([]);

  GetService.brief().then(function(response) {
    scope.graph = GraphService.conv(response.data);
  });
  
  scope.width = 500;
  scope.height = 500;

  var color = d3.scale.category10()

  var colorDict = {
    'ax':   color(0),
    'def':  color(1),
    'thm':  color(2),
    'pf':   color(3)
  };

  var force = d3.layout.force()
    .charge(-250)
    .linkDistance(200)
    .linkStrength(0.1)
    .size([scope.width, scope.height]);

  scope.showDetail = function showDetail(node) {
    window.alert(node);
  };

  scope.tick = function tick(e) {
    // Push different nodes in different directions for clustering.
    var k = 6 * e.alpha;
    var nodes = scope.graph.nodes;
    var links = scope.graph.links;

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

  scope.$watchCollection("graph", function(newValue) {
    var nodes = scope.graph.nodes;
    var links = scope.graph.links;

    for(var i = 0; i < links.length ; i++) {
      links[i].strokeWidth = 1;
    }

    for(var i = 0; i < nodes.length ; i++) {
      nodes[i].color = colorDict[nodes[i].kind];
    }

    force
      .nodes(nodes)
      .links(links)
      .on("tick", scope.tick)
      .start();
  });
}])

angular.module('datamaker', ['ui.bootstrap', 'prooftree'])
  .controller('DataMakerController', function($filter, $scope) {
    $scope.dictOutput = new Object();
    $scope.arrayOutput = [];

    $scope.isopen = true;
    $scope.hidejson = true;
    $scope.hidegraph = false;

    $scope.lastUpdate = new Date().getTime();

    $scope.promptCopy = function promptCopy(data) {
      window.prompt(
        'Press Ctrl+C or Cmd+C.', 
        $filter('json')(data));
    };
  })
  .controller('GraphController', 
  ['$scope', '$filter', 'graphConverter',
  function($scope, $filter, graphConverter) {
    var scope = $scope;
    gctrl = this;
    scope.conv = graphConverter;
    this.scope = scope;
    scope.data = scope.$parent.arrayOutput;
    scope.graph = {};
    
    scope.width = 500;
    scope.height = 500;

    var color = d3.scale.category10()

    var colorDict = {
      'ax':   color(0),
      'def':  color(1),
      'thm':  color(2),
      'pf':   color(3)
    };

    var force = d3.layout.force()
      .charge(-250)
      .linkDistance(200)
      .linkStrength(0.1)
      .size([this.scope.width, this.scope.height]);

    scope.showDetail = function showDetail(node) {
      window.alert(node.body);
    };

    scope.tick = function tick(e) {
      // Push different nodes in different directions for clustering.
      var k = 6 * e.alpha;
      var nodes = scope.graph.nodes;
      var links = scope.graph.links;

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

    scope.$watchCollection("data", function(newValue) {
      scope.graph = scope.conv(newValue);
      var nodes = scope.graph.nodes;
      var links = scope.graph.links;

      for(var i = 0; i < links.length ; i++) {
        links[i].strokeWidth = 1;
      }

      for(var i = 0; i < nodes.length ; i++) {
        nodes[i].color = colorDict[nodes[i].type];
      }

      force
        .nodes(nodes)
        .links(links)
        .on("tick", scope.tick)
        .start();
    });


  }])
  .controller('NewEntryController', function($scope) {
    var scope = $scope.$parent;

    this.entryTypes = {
      'ax':   'Axiom',
      'def':  'Definition',
      'thm':  'Theorem',
      'pf':   'Proof'
    };

    this.newType = 'ax';
    this.newTitle = '';
    this.newBody = '';
    this.newDeps = [];
    this.nextID = 1;

    this.searchDep = null;

    this.searchMatch = function searchMatch() {
      id = this.searchDep.id;
      if (this.newDeps.indexOf(id) == -1)
        this.newDeps.push(id);
      this.searchDep = null;
    };

    this.removeDep = function removeDep(index) {
      // var index = this.newDeps.indexOf(d);
      this.newDeps.splice(index, 1);
    };

    this.formatNode = function formatNode (node) {
      if (node)
        return this.entryTypes[node.type] + ' - ' + node.title;
      else
        return '';
    };

    // this.output = function output() {
    //   // return JSON.stringify(this.entries, null, 2);
    //   return this.entries;
    // };

    this.add = function add() {
      if (this.newtitle == '')
        return;

      if (scope.dictOutput[this.nextID] == undefined) {
        var newNode = new Node(
          this.nextID,
          this.newType,
          this.newTitle,
          this.newDeps.sort(function (a,b) {return a-b;}),
          this.newBody);
        scope.dictOutput[this.nextID] = newNode;
        scope.arrayOutput.push(newNode);
        scope.lastUpdate = new Date().getTime();
      }

      this.nextID++;
      this.newTitle = '';
      this.newBody = '';
      this.newDeps = [];
    };

    ctrl = this;
  });