
$( document ).ready(function() {
    var map = new OpenLayers.Map("map");

    map.addLayer(new OpenLayers.Layer.OSM());

    var geojson_format = new OpenLayers.Format.GeoJSON();
    var epsg4326 = new OpenLayers.Projection("EPSG:4326");
    var projectTo = map.getProjectionObject();

    var sjc_lonlat = new OpenLayers.LonLat(-45.88555, -23.17960).transform(epsg4326, projectTo);
    var zoom = 15;
    map.setCenter(sjc_lonlat, zoom);

    function toPosition(position){
        var current_lonlat = new OpenLayers.LonLat(
            position.coords.longitude,
            position.coords.latitude
        ).transform(epsg4326, projectTo);

        var current_point = new OpenLayers.Geometry.Point(
            current_lonlat.lon,
            current_lonlat.lat
        );

        $.getJSON( "/get_current_geom/", function(data) {

            var features = geojson_format.read(data);

            if(features.length >= 1){
                var feature = features[0];

                if(feature.geometry.intersects(current_point))
                    map.setCenter(current_point, zoom);
            }

        });
    }

    if (navigator.geolocation)
        navigator.geolocation.getCurrentPosition(toPosition);

});
