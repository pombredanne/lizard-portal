{% load get_portal_template %}
{
    itemId: 'toestand-aan-afvoergebied',
    title: 'Toestand',
    breadcrumbs: [
        {
            name: 'watersysteemkaart',
            link: 'homepage'
        },
        {
            name: 'Toestand'
        }
    ],
	xtype: 'portalpanel',
	items: [{
    	width: 200,
		items: [
            {% get_portal_template gebiedseigenschappen %},
            {% get_portal_template communique %},
            {% get_portal_template esf-overzicht %}
        ]
    },{
		flex: 1,
		items: [{
            title: 'Grafieken',
            flex: 1,
            xtype: 'multigraphstore',
            store: Ext.create('Lizard.store.Graph', {data: {% get_portal_template graphs-aanafvoer_toestand %} })
		}],
        tools: [{
            type: 'save',
            handler: function (e, target, panelHeader, tool) {
                var cm = Lizard.CM;

                Ext.create('Ext.window.Window', {
                    title: 'Stuurparameters instellen',
                    width: 800,
                    height: 600,
                    modal: true,
                    finish_edit_function: function (updated_record) {
                        //todo
                    },
                    editpopup: true,

                    loader:{
                        loadMask: true,
                        autoLoad: true,
                        url: '/measure/steering_parameter_form/',
                        params: {
                            object_id: cm.object.id
                        },
                        ajaxOptions: {
                            method: 'GET'
                        },
                        renderer: 'component'
                    }
                }).show();
            }
        }]
    },
    {
		width: 200,
		items: [{
            title: 'Links van dit gebied',
            layout: {
                type: 'table',
                columns:1
            },
            height: 250,
            defaults:{
                width:150,
                xtype:'button',
                margin: 2
            },
            items:[{
                    text: 'Ecologische sleutelfactoren',
                    icon: '/static_media/vss/icons/esf.png',
                    handler: function() { Lizard.CM.setContext({portal_template:'esf-1'}); }
                }, {
                   text: 'Waterbalansen',
                   icon: '/static_media/vss/icons/waterbalansen.png',
                   handler: function() { Lizard.CM.setContext({portal_template:'waterbalans'}); }
                }, {
                   text: 'Analyse interpretaties',
                   icon: '/static_media/vss/icons/advies.png',
                   handler: function() { Lizard.CM.setContext({portal_template:'analyse-interpretatie'}); }
                }, {
                   text: 'Geschikte maatregelen',
                   icon: '/static_media/vss/icons/gebiedsinformatie.png',
                   handler: function() { Lizard.CM.setContext({portal_template:'advies'}); }
                }, {
                   text: 'Maatregelen',
                   icon: '/static_media/vss/icons/maatregelen.png',
                   handler: function() { Lizard.CM.setContext({portal_template:'maatregelen'}); }
                }, {
                   text: 'Watersysteemkaart',
                   //icon: '/static_media/vss/icons/toestand.png',
                   handler: function() { Lizard.CM.setContext({portal_template:'homepage'}); }
                }
            ]
 		},
        {% get_portal_template gebieden_links %}
        ]
    }]
}

