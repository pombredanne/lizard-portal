# Collection of apps selected by User

Ext.define('Lizard.store.AppScreen', {
    extend: 'Ext.data.Store',
    model: 'Lizard.model.App',
    # data must be provided from outside
    # data: apps,

    # Apparently required
    proxy: {
        type: 'memory',
        reader: {
            type: 'json'
        }
    },
});
