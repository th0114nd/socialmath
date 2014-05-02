function Node(id, type, title, depends) {
  this.id = id;
  this.type = type;
  this.title = title;
  this.depends = depends;
};

angular.module('prooftree', [])
  .factory('graphConverter', function () {
    var conv = function (nodes) {
      var id2Pos = new Object();
      var result = {'nodes': [], "links":[]};

      for (var i = 0; i < nodes.length; i++) {
        id2Pos[nodes[i].id] = i;
        result.nodes.push(nodes[i]);

        nodes[i].free = (nodes[i].depends.length == 0);
      }

      for (var i = 0; i < nodes.length; i++) {
        var links = result.nodes[i].depends;
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

    return conv;
  });

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

    scope.$watch("$parent.lastUpdate", function(newValue) {
      scope.graph = scope.conv(scope.data);
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
          this.newDeps.sort(function (a,b) {return a-b;}));
        scope.dictOutput[this.nextID] = newNode;
        scope.arrayOutput.push(newNode);
        scope.lastUpdate = new Date().getTime();
      }

      this.nextID++;
      this.newTitle = '';
      this.newDeps = [];
    };

    ctrl = this;
  });