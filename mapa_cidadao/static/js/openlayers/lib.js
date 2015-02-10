OpenLayers.Control.MousePositionCustom = OpenLayers.Class(OpenLayers.Control.MousePosition, {
    
    formatCoords: function (base) {
        var north;
        var t;
        var t2;
        var degrees = Math.floor(base);
        var minutes = Math.floor(t = ( base - degrees ) * 60); // t = minutes
        var seconds = Math.floor(t2 = ( t - minutes ) * 60);
        var microseconds = Math.floor(( t2 - seconds) * 60);
        if (degrees <= 9) degrees = "0" + degrees;
        if (minutes <= 9) minutes = "0" + minutes;
        if (seconds <= 9) seconds = "0" + seconds;
        if (microseconds <= 9) microseconds = "0" + microseconds;
        return ("" + degrees + "\u00B0 " + minutes + "\u0027 " + seconds + "." + microseconds + "\u0022" );
    },

    formatOutput: function(lonLat) {
        var ns, ew;
        ns = (lonLat.lon > 0)?"E":"W";
        ew = (lonLat.lat > 0)?"N":"S";
        var newHtml = ns + " " + this.formatCoords(Math.abs(lonLat.lon)) + "&nbsp;&nbsp;&nbsp;" + ew + " " + this.formatCoords(Math.abs(lonLat.lat));
        return newHtml;
    },

    CLASS_NAME: "OpenLayers.Control.MousePosition"
});