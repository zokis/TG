var map;
var epsg4326 = new OpenLayers.Projection("EPSG:4326");
var epsg900913 = new OpenLayers.Projection("EPSG:900913");
var wkt = new OpenLayers.Format.WKT();

function init() {
    map = new OpenLayers.Map({
        div: "map",
        projection: "EPSG:900913",
        fractionalZoom: true,
        layers: [new OpenLayers.Layer.OSM()],
        controls: [
        new OpenLayers.Control.Navigation({
            dragPanOptions: {
                enableKinetic: true
            }
        }),
        // new OpenLayers.Control.Zoom(),
        new OpenLayers.Control.ScaleLine(),
        new OpenLayers.Control.MousePosition(),
        new OpenLayers.Control.Permalink(), ]
    });
}

function popup_clear() {
    while (map.popups.length) {
        map.removePopup(map.popups[0]);
    }
}

function feature_click(event) {
    popup_clear();
    var feature = event.feature;
    var content = "<h2>" + feature.attributes.name + "</h2>" + feature.attributes.description;
    popup = new OpenLayers.Popup.FramedCloud(
        "chicken",
    feature.geometry.getBounds().getCenterLonLat(),
    new OpenLayers.Size(100, 100),
    content,
    null,
    true,
    popup_clear);
    feature.popup = popup;
    map.addPopup(popup);
}

function load_cidade_geom() {
    var geojson_format = new OpenLayers.Format.GeoJSON();
    var sjc_lonlat = new OpenLayers.LonLat(-45.88555, -23.17960).transform(epsg4326, epsg900913);
    var zoom = 15;
    map.setCenter(sjc_lonlat, zoom);
    var cidade_layer = new OpenLayers.Layer.Vector("Limites de São José dos Campos");
    map.addLayer(cidade_layer);
    $.ajax({
        dataType: "json",
        url: "/get_current_geom/",
        success: function (data) {
            var features = geojson_format.read(data);
            if (features.length >= 1) {
                var feature = features[0];
                feature.style = {
                    fillColor: '#FFF',
                    fillOpacity: 0
                };
                map.setOptions({
                    restrictedExtent: feature.geometry.getBounds(),
                    numZoomLevels: 10
                });
                cidade_layer.addFeatures([feature]);
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(function (position) {
                        var current_lonlat = new OpenLayers.LonLat(
                        position.coords.longitude,
                        position.coords.latitude).transform(epsg4326, epsg900913);
                        var current_point = new OpenLayers.Geometry.Point(
                        current_lonlat.lon,
                        current_lonlat.lat);
                        if (feature.geometry.intersects(current_point)) {
                            map.setCenter(current_point, zoom);
                        }
                    });
                }
            }
        }
    });
}