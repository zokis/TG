if(typeof $.fn.mover_v == "undefined") {
    $.fn.extend({
        mover_v: function(parent) {
            return $(this).each(function() {
                var body_padding = parseInt($('body').css('padding-top'));
                var $el = $(parent);
                $el.css('top', body_padding + 4);
                var dragging = false;
                var start_y = 0;
                var start_t = 0;
                $el.mousedown(function(ev) {
                    dragging = true;
                    start_y = ev.clientY;
                    start_t = $el.css('top');
                });
                $(window).mousemove(function(ev) {
                    ev.preventDefault();
                    if (dragging) {
                        // calculate new top
                        var new_top = parseInt(start_t) + (ev.clientY - start_y);
                        //stay in parent
                        var max_top =  $el.parent().height()-$el.height();

                        if(new_top > max_top){
                            new_top = max_top;
                        }
                        if(new_top < body_padding){
                            new_top = body_padding;
                        }

                        $el.css('top', new_top);
                    }
                }).mouseup(function() {
                    dragging = false;
                });
            });
        }
    });
}

if(typeof $.fn.mover_h == "undefined") {
    $.fn.extend({
        mover_h: function(parent) {
            return $(this).each(function() {
                var $el = $(parent);
                $el.css('left', 45);
                var dragging = false;
                var start_x = 0;
                var start_t = 0;
                $el.mousedown(function(ev) {
                    dragging = true;
                    start_x = ev.clientX;
                    start_t = $el.css('left');
                });
                $(window).mousemove(function(ev) {
                    ev.preventDefault();
                    if (dragging) {
                        // calculate new left
                        var new_left = parseInt(start_t) + (ev.clientX - start_x);
                        
                        //stay in parent
                        var max_left =  $( window ).width()-$el.width();
                        
                        if(new_left > max_left){
                            new_left = max_left;
                        }
                        if(new_left < 0){
                            new_left = 0;
                        }

                        $el.css('left', new_left );
                    }
                }).mouseup(function() {
                    dragging = false;
                });
            });
        }
    });
}


function mapa_cidadao_draw_component(geom, container){

    var component_style = '<style type="text/css">' +
        '#draw-point{' +
        'position:absolute; ' +
        'right:80px; ' +
        'top:70px;' +
        'z-index:10000; ' +
        '}' +
        '#draw-polygon{' +
        'position:absolute; ' +
        'right:160px; ' +
        'top:70px; ' +
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
        '<button class="btn" id="draw-point" title="Adicionar um Ponto">' +
        '<img width="26" height="26" src="https://cdn1.iconfinder.com/data/icons/mirrored-twins-icon-set-hollow/128/PixelKit_point_marker_icon.png">' +
        '</button>' +
        '<button class="btn" id="draw-polygon" title="Adicionar um Poligono">' +
        '<img width="26" height="26" src="https://cdn1.iconfinder.com/data/icons/windows8_icons_iconpharm/26/polygon.png">' +
        '</button>' +
        '<button class="btn btn-success" id="pam" title="Mover-se pelo Mapa">' +
        '<img width="26" height="26" src="https://cdn3.iconfinder.com/data/icons/wpzoom-developer-icon-set/500/142-48.png">' +
        '</button>';
    
    $(container).append(component_html);

    var pontos_layer = new OpenLayers.Layer.Vector("Pontos");
    var poligonos_layer = new OpenLayers.Layer.Vector("Áreas");

    map.addLayers([pontos_layer, poligonos_layer]);

    if(geom !== ''){
        geom = wkt.read(geom);
        if(geom.geometry.x || geom.geometry.y){
            pontos_layer.addFeatures(geom);
        }
        else{
            poligonos_layer.addFeatures(geom);
        }
    }

    var point_control = new OpenLayers.Control.DrawFeature(
        pontos_layer,
        OpenLayers.Handler.Point
    );
    map.addControl(point_control);
    var polygon_control = new OpenLayers.Control.DrawFeature(
        poligonos_layer,
        OpenLayers.Handler.Polygon, {handlerOptions: {freehand: false}}
    );
    map.addControl(polygon_control);

    function add_new_feature(layer, new_feature){

        $('#id_geom').val(wkt.write(new_feature));

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

    poligonos_layer.events.on({
        'beforefeatureadded': function(event){
            add_new_feature(poligonos_layer, event.feature);
        }
    });

    $('#draw-point').click(function (){
        point_control.activate();
        polygon_control.deactivate();
        poligonos_layer.removeAllFeatures();
        $(this).addClass("btn-success");
        $('#draw-polygon').removeClass("btn-success");
        $('#pam').removeClass("btn-success");
    });
    $('#draw-polygon').click(function (){
        polygon_control.activate();
        point_control.deactivate();
        pontos_layer.removeAllFeatures();
        $(this).addClass("btn-success");
        $('#draw-point').removeClass("btn-success");
        $('#pam').removeClass("btn-success");
        
    });
    $('#pam').click(function (){
        point_control.deactivate();
        polygon_control.deactivate();
        $(this).addClass("btn-success");
        $('#draw-polygon').removeClass("btn-success");
        $('#draw-point').removeClass("btn-success");
    });
}
