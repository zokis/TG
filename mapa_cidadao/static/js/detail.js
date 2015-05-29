$(document).ready(function(){
    init();
    load_cidade_geom();

    geom = wkt.read(geom);
    map.setCenter(geom.geometry.getBounds().getCenterLonLat(), 15);

    var votos_total = votos + vetos;

    var votos_percent = (votos * 100 / votos_total);
    var vetos_percent = (100 - votos_percent);
    if(isNaN(votos_percent))
        votos_percent = 0;
    if(isNaN(vetos_percent))
        vetos_percent = 0;
    votos_percent = votos_percent + '%';
    vetos_percent = vetos_percent + '%';

    $('#bar-votos .determinate').css('width', votos_percent);
    $('#bar-vetos .determinate').css('width', vetos_percent);

    $('#percent-votos').html('' + votos + ' - ' + votos_percent);
    $('#percent-vetos').html('' + vetos + ' - ' + vetos_percent);

    var pontos_layer = new OpenLayers.Layer.Vector("Pontos");
    map.addLayers([pontos_layer]);
    geom.style = mapa_cidadao_style;
    geom.style.pointRadius = 4;
    pontos_layer.addFeatures(geom);
});