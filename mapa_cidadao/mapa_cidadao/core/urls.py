# coding: utf-8
from django.conf.urls import patterns, url
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView

from mapa_cidadao.core.models import Categoria
from mapa_cidadao.core.models import Ocorrencia

urlpatterns = patterns(
    '',
    url(r'^$', 'mapa_cidadao.core.views.index', name='index'),
    url(r'^get_current_geom/$', 'mapa_cidadao.core.views.get_current_geom', name='get_current_geom'),
    url(r'^ocorrencia/nova/$', 'mapa_cidadao.core.views.ocorrencia_crud', name='ocorrencia_crud'),
    url(r'^ocorrencia/(?P<pk>\d+)/$', 'mapa_cidadao.core.views.ocorrencia_crud', name='ocorrencia_crud'),
    url(r'^ocorrencia/(?P<pk>\d+)/detalhes/$', DetailView.as_view(model=Ocorrencia), name='ocorrencia_detail'),
    url(r'^adiciona_categoria/$', CreateView.as_view(model=Categoria)),
)
