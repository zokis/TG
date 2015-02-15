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
)
