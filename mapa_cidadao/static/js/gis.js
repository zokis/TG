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
    var content = "" +
    "<h2>" +feature.attributes.name + "</h2>" +
    "" + feature.attributes.description.slice(0, 51) +
    '&nbsp;...' + 
    '<div class="row">' +
    '<a href="/ocorrencia/' + feature.attributes.pk + '/detalhes/" class="waves-effect waves-light btn">' +
    'Detalhes<i class="mdi-image-details right"></i>' +
    '</a></div>';
    popup = new OpenLayers.Popup.FramedCloud(
    "mc-"+feature.attributes.pk,
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

var mapa_cidadao_style = {
    fillColor: '#F00',
    fillOpacity: 0.5,
    strokeWidth: 1,
    strokeColor: '#000',
};

function mapa_cidadao_draw_component(geom, container){

    var component_style = '<style type="text/css">' +
        '#draw-point{' +
        'position:absolute; ' +
        'right:80px; ' +
        'top:70px;' +
        'z-index:10000; ' +
        '}' +
        '#pam{' +
        'position:absolute; ' +
        'right:240px; ' +
        'top:70px; ' +
        'z-index:10000; ' +
        '}' +
        '</style>';

    $('html > head').append(component_style);

    var component_html = '' +
        '<i id="draw-point" class="mdi-maps-pin-drop" title="Adicionar Novo Ponto"></i>' +
        '<i id="pam" class="mdi-maps-navigation blue" title="Mover-se pelo Mapa">';
    
    $(container).append(component_html);

    var pontos_layer = new OpenLayers.Layer.Vector("Pontos");

    map.addLayers([pontos_layer]);

    if(geom !== ''){
        geom = wkt.read(geom);
        geom.style = mapa_cidadao_style;
        if(geom.geometry.x || geom.geometry.y){
            geom.style.pointRadius = 4;
            pontos_layer.addFeatures(geom);
        }
    }

    var point_control = new OpenLayers.Control.DrawFeature(
        pontos_layer,
        OpenLayers.Handler.Point
    );
    map.addControl(point_control);

    function add_new_feature(layer, new_feature){
        new_feature.style = mapa_cidadao_style;
        if(new_feature.geometry.x || new_feature.geometry.y){
            new_feature.style.pointRadius = 4;
        }

        $('#id_ponto').val(wkt.write(new_feature));

        var features_len = layer.features.length;
        for(var i=features_len; i--;){
            var feature = layer.features[i];
            if(feature.id != new_feature.id){
                layer.removeFeatures(feature);
            }
        }
    }

    pontos_layer.events.on({
        'beforefeatureadded': function(event){
            add_new_feature(pontos_layer, event.feature);
        }
    });

    $('#draw-point').click(function (){
        point_control.activate();
        $(this).addClass("blue");
        $('#pam').removeClass("blue");
    });
    $('#pam').click(function (){
        point_control.deactivate();
        $(this).addClass("blue");
        $('#draw-point').removeClass("blue");
    });
}