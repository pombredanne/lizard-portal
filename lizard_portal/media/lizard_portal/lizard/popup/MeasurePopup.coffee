Ext.define('Lizard.popup.MeasurePopup', {
    extend: 'Ext.form.Panel'

    startValue: null,
    bodyStyle: 'padding:5px 5px 0',
    defaults:
        anchor: '100%'
    width: 300,
    init_background: null

    statics:
      show: (records, workspaceitem) ->
        permissions = Lizard.CM.getContext().user.permissions
        controls = {}
        if permissions.indexOf('Is beleidsmaker') >= 0
          controls['save'] = [
            'Bewerken maatregel: ' + records[0].data.title, 
            '/measure/measure_detailedit_portal/',
            { measure_id: records[0].data.id },
            null, false, 'component', true]
          controls['plus'] = [
            'Deelmaatregel toevoegen', '/measure/measure_detailedit_portal/',
            {
              parent_id: records[0].data.id,
              area_id: Lizard.CM.getContext().object.id
            }
            , null, false, 'component', true]

        controls['search'] = [
          'Geschiedenis',
          '/measure/history/' + records[0].data.id,
          {}, {}, false, 'html', false, false]

        Ext.getCmp('portalWindow').linkToPopup(
          'Maatregel: ' + records[0].data.title,
          '/measure/measure/' + records[0].data.id,
          {},
          controls,
          false,
          'html',
          false,
          true
        );
    items: [{
    }],
})
