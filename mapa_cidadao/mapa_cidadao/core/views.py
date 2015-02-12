# coding: utf-8
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import render_to_response

from municipios.models import Municipio

from mapa_cidadao.core.forms import OcorrenciaForm, ContatoForm, SearchForm
from mapa_cidadao.core.models import Ocorrencia


MUNICIPIO_ID = getattr(settings, 'MUNICIPIO_ID', 3549904)

MUNICIPIO = Municipio.objects.get(id_ibge=MUNICIPIO_ID)
ESTADO = MUNICIPIO.uf
END_GEOCODE_STR = u'%s - %s, Brasil' % (MUNICIPIO.nome, ESTADO.nome)

EMPTY_STRING = ''


def get_geom_from_cache():
    geom = cache.get("geom_%s" % MUNICIPIO_ID)
    if geom is None:
        geom = MUNICIPIO.geom
        geom.transform(900913)

        cache.set("geom_%s" % MUNICIPIO_ID, geom, 30*24*60*60)  # 1 mês
    return geom


def get_current_geom(request):
    geom = get_geom_from_cache()
    return HttpResponse(
        geom.json,
        content_type="application/json"
    )


def index(request):
    geom = get_geom_from_cache()
    search_form = SearchForm(request.POST or None, geom=geom)
    ocorrencias = search_form.get_queryset()

    return render(
        request,
        'index.html',
        {
            'ocorrencias': ocorrencias,
            'request': request,
            'search_form': search_form,
            'user': request.user,
        }
    )


def teste(request):
    geom = get_geom_from_cache()
    search_form = SearchForm(request.GET or None, geom=geom)
    ocorrencias = search_form.get_queryset()

    return render_to_response(
        'teste.html',
        {
            'ocorrencias': ocorrencias,
            'request': request,
            'search_form': search_form,
            'user': request.user,
        }
    )


def contact(request):
    form = ContatoForm(request.GET or None)
    return render_to_response(
        'forms/contact.html',
        {
            'form': form,
            'user': request.user,
        }
    )


def about(request):
    return render_to_response('forms/about.html', {})


@login_required
def ocorrencia_crud(request, pk=None):
    geom = EMPTY_STRING
    if pk:
        ocorrencia = get_object_or_404(Ocorrencia, pk=pk, user=request.user)
        template = 'forms/ocorrencia_edit.html'
        geom = ocorrencia.ponto or ocorrencia.poligono
    else:
        template = 'forms/ocorrencia_add.html'
        ocorrencia = None

    form = OcorrenciaForm(request.POST or None, instance=ocorrencia, request_user=request.user)

    if request.method == 'POST':
        if form.is_valid():
            ocorrencia = form.save()
            messages.success(request, u'Ocorrência salva com sucesso!')

            return redirect(reverse('ocorrencia_crud', args=(ocorrencia.pk,)))
        else:
            geom = form.cleaned_data.get('geom', EMPTY_STRING)
            if geom != EMPTY_STRING:
                geom = '%s' % geom

    return render(
        request,
        template,
        {
            'form': form,
            'request': request,
            'user': request.user,
            'geom': geom
        }
    )


@login_required
def generic_delete_from_model(request, app_model=None, object_id=None):
    next = request.GET.get('next', 'home')
    app_name, model_name = app_model.split('.', 1)
    if request.user.has_module_perms(app_name) or request.user.is_superuser:
        model = get_model(app_name, model_name)
        obj = get_object_or_404(model, pk=object_id)
        can_delete = True

        if hasattr(obj, 'user_can_delete'):
            if not obj.user_can_delete(request.user):
                messages.success(request, u"Não foi possível deletar")
                can_delete = False

        if can_delete:
            obj.delete()
            messages.success(request, "Deletado com sucesso")

        return redirect(next)
    raise Http404
