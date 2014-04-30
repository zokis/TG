
$( document ).ready(function() {
    var map = new OpenLayers.Map("map");

    console.log(map);

    map.addLayer(new OpenLayers.Layer.OSM());

    var epsg4326 = new OpenLayers.Projection("EPSG:4326");
    var projectTo = map.getProjectionObject();

    var sjc_lonlat = new OpenLayers.LonLat(-45.88821, -23.23960).transform(epsg4326, projectTo);

    var zoom = 15;
    map.setCenter(sjc_lonlat, zoom);
});
