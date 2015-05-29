# coding: utf-8
from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^$', 'mapa_cidadao.core.views.index', name='index'),
    url(r'^contato/$', 'mapa_cidadao.core.views.contact', name='contact'),
    url(r'^sobre/$', 'mapa_cidadao.core.views.about', name='about'),
    url(r'^get_current_geom/$', 'mapa_cidadao.core.views.get_current_geom', name='get_current_geom'),
    url(r'^ocorrencia/nova/$', 'mapa_cidadao.core.views.ocorrencia_crud', name='ocorrencia_crud'),
    url(r'^ocorrencia/(?P<pk>\d+)/$', 'mapa_cidadao.core.views.ocorrencia_crud', name='ocorrencia_crud'),
    url(r'^ocorrencia/(?P<pk>\d+)/detalhes/$', 'mapa_cidadao.core.views.ocorrencia_detalhes', name='ocorrencia_detail'),
    url(r'^ocorrencia/(?P<pk>\d+)/(?P<op>(votar|vetar))/$', 'mapa_cidadao.core.views.votar', name='votar'),
    url(r'^ocorrencia/(?P<pk>\d+)/spam/$', 'mapa_cidadao.core.views.spam', name='spam'),
    url(r'^ocorrencia/(?P<pk>\d+)/(?P<status>(2|3))/$', 'mapa_cidadao.core.views.change_status', name='change_status'),
    url(
        r'^ocorrencia/(?P<object_id>\d+)/delete/$',
        'mapa_cidadao.core.views.generic_delete_from_model',
        {'app_model': 'core.Ocorrencia'},
        name='ocorrencia_delete'
    ),
    url(r'^ocorrencias/$', 'mapa_cidadao.core.views.ocorrencia_list', name='ocorrencia_list'),
    url(r'^estatisticas/$', 'mapa_cidadao.core.views.estatisticas', name='estatisticas'),
    url(r'^ocorrencias/json/$', 'mapa_cidadao.core.views.load_ocorrencias', name='load_ocorrencias'),
    url(
        r'^ocorrencias/json/%s$' % (
            ''.join(map(lambda x: "(?P<%s>(?:\-)?\d+(?:\.\d+)?)/" % x, ['x0', 'y0', 'x1', 'y1']))
        ),
        'mapa_cidadao.core.views.load_ocorrencias',
        name='load_ocorrencias'
    ),
)
