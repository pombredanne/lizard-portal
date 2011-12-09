(function() {
  Ext.define('Lizard.portlet.MultiGraph', {
    extend: 'Lizard.portlet.Portlet',
    alias: 'widget.multigraph',
    config: {
      graph_service_url: '',
      graphs: [],
      context_manager: []
    },
    setGraphFit: function(fit) {
      var item, items, _i, _j, _len, _len2;
      items = this.graphs;
      if (fit) {
        for (_i = 0, _len = items.length; _i < _len; _i++) {
          item = items[_i];
          item.flex = 1;
        }
      } else {
        for (_j = 0, _len2 = items.length; _j < _len2; _j++) {
          item = items[_j];
          delete item.flex;
        }
      }
      return this.doLayout();
    },
    updateGraphs: function(changes, new_context, context_manager, me) {
      var graph, _i, _len, _ref, _results;
      console.log('update graphs');
      _ref = me.graphs;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        graph = _ref[_i];
        console.log(arguments);
        _results.push(graph.applyParams({
          dt_start: Ext.Date.format(new_context.period_start, 'Y-m-d H:i:s'),
          dt_end: Ext.Date.format(new_context.period_end, 'Y-m-d H:i:s'),
          location: new_context.object_id
        }));
      }
      return _results;
    },
    initGraphs: function() {
      var context, getImageConfig, graph, graph_config, graph_configs, me, _i, _len, _results;
      me = this;
      getImageConfig = function(graph) {
        var output;
        output = graph;
        output.orig_src = graph.graph_service_url || me.graph_service_url;
        output.params = graph.params || {};
        return output;
      };
      graph_configs = this.getGraphs();
      context = Ext.getCmp('portalWindow').context_manager.getContext();
      this.graphs = [];
      _results = [];
      for (_i = 0, _len = graph_configs.length; _i < _len; _i++) {
        graph_config = graph_configs[_i];
        graph = Ext.create('Lizard.ux.ImageResize', Ext.merge({
          dt_start: Ext.Date.format(context.period_start, 'Y-m-d H:i:s'),
          dt_end: Ext.Date.format(context.period_end, 'Y-m-d H:i:s'),
          location: context.object_id
        }, getImageConfig(graph_config)));
        graph.applyParams();
        this.items.push(graph);
        this.graphs.push(graph);
        _results.push(this.tbar.push({
          text: graph_config.title,
          pressed: true,
          enableToggle: true,
          iconCls: 'l-icon-chartbar',
          graph: graph,
          handler: function(button) {
            if (button.pressed) {
              return button.graph.show();
            } else {
              return button.graph.hide();
            }
          }
        }));
      }
      return _results;
    },
    constructor: function(config) {
      console.log(config);
      this.initConfig(arguments);
      return this.callParent(arguments);
    },
    initComponent: function() {
      var me;
      me = this;
      Ext.apply(this, {
        layout: {
          type: 'vbox',
          align: 'stretch'
        },
        defaults: {
          flex: 1,
          height: 250
        },
        autoScroll: true,
        tbar: ['Grafieken:'],
        items: [],
        tools: [
          {
            type: 'plus',
            handler: function(e, target, panelHeader, tool) {
              var portlet;
              portlet = panelHeader.ownerCt;
              if (tool.type === 'plus') {
                tool.setType('minus');
                return me.setGraphFit(false);
              } else {
                tool.setType('plus');
                return me.setGraphFit(true);
              }
            }
          }
        ]
      });
      console.log('cm');
      console.log(this.context_manager);
      if (this.context_manager) {
        console.log('register contextchange');
        this.context_manager.on('contextchange', function(change, context, context_m) {
          return me.updateGraphs(change, context, context_m, me);
        });
      }
      this.initGraphs();
      return this.callParent(arguments);
    }
  });
}).call(this);
