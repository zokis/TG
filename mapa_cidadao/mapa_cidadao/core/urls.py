# coding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'mapa_cidadao.core.views.index', name='index'),
    url(r'^get_current_geom/$', 'mapa_cidadao.core.views.get_current_geom', name='get_current_geom'),
)
