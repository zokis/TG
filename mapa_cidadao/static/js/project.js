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
                        var max_top = $(window).height()-$el.height();

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


$(document).ready(function() {
  $('.datepicker').pickadate({
    labelMonthNext: 'Próximo Mês',
    labelMonthPrev: 'Mês Anterior',
    labelMonthSelect: 'Selecione um mês',
    labelYearSelect: 'Selecione um ando',
    monthsFull: [ 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro' ],
    monthsShort: [ 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Aug', 'Set', 'Out', 'Nov', 'Dez' ],
    weekdaysFull: [ 'Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado' ],
    weekdaysShort: [ 'Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab' ],
    weekdaysLetter: [ 'D', 'S', 'T', 'Q', 'Q', 'S', 'S' ],
    today: 'Hoje',
    clear: 'Limpar',
    close: 'Fechar',
    format: 'd/mm/yyyy'
  });
  $('select').material_select();
  $('a#toggle-search').click(function(){
    var search = $('div#search');

    if(search.is(":visible")){
      search.hide();
    }
    else{
      search.show();
    }
    return false;
  });
  $('.dropdown-button').dropdown({
      inDuration: 300,
      outDuration: 225,
      constrain_width: true,
      hover: false,
      alignment: 'right',
      gutter: 10,
      belowOrigin: true
    }
  );
  $('.button-collapse').sideNav();
});
