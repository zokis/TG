# coding: utf-8
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import render_to_response
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from municipios.models import Municipio

from mapa_cidadao.core.forms import OcorrenciaForm, ContatoForm, SearchForm
from mapa_cidadao.core.models import Categoria, Ocorrencia, Spam


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


@cache_page(60 * 25)
def estatisticas(request):

    sete_dias = timezone.now().date() - timedelta(days=7)

    users = User.objects.filter(is_staff=False, is_active=True).count()
    oco_total = Ocorrencia.objects.all().count()
    ocos_cats = []

    for cat in Categoria.objects.all():
        oco = Ocorrencia.objects.filter(categoria=cat).count()
        ocos_cats.append((cat.nome, oco, (oco * 100.0) / oco_total))

    oco_7_dias = Ocorrencia.objects.filter(date_add__gte=sete_dias).count()
    oco_abertas = Ocorrencia.objects.filter(status=1).count()
    oco_resolvidas = Ocorrencia.objects.filter(status=2).count()
    oco_reabertas = Ocorrencia.objects.filter(status=3).count()
    oco_inapropriadas = Ocorrencia.objects.filter(status=4).count()
    oco_spam = Ocorrencia.objects.filter(status=5).count()

    oco_abertas_100 = (oco_abertas * 100.0) / oco_total
    oco_resolvidas_100 = (oco_resolvidas * 100.0) / oco_total
    oco_reabertas_100 = (oco_reabertas * 100.0) / oco_total
    oco_inapropriadas_100 = (oco_inapropriadas * 100.0) / oco_total
    oco_spam_100 = (oco_spam * 100.0) / oco_total

    return render(
        request,
        'estatisticas.html',
        {
            'oco_7_dias': oco_7_dias,
            'oco_abertas': oco_abertas,
            'oco_abertas_100': oco_abertas_100,
            'oco_inapropriadas': oco_inapropriadas,
            'oco_inapropriadas_100': oco_inapropriadas_100,
            'oco_reabertas': oco_reabertas,
            'oco_reabertas_100': oco_reabertas_100,
            'oco_resolvidas': oco_resolvidas,
            'oco_resolvidas_100': oco_resolvidas_100,
            'oco_spam': oco_spam,
            'oco_spam_100': oco_spam_100,
            'oco_total': oco_total,
            'ocos_cats': ocos_cats,
            'users': users,
        }
    )


def contact(request):
    form = ContatoForm(request.GET or None)
    return render_to_response(
        'contact.html',
        {
            'form': form,
            'user': request.user,
            'title': u'Contato'
        }
    )


def about(request):
    return render_to_response('about.html', {'title': u'Sobre'})


def votar(request, pk, op='voto'):
    if request.method == "POST":
        ocorrencia = get_object_or_404(Ocorrencia, pk=pk)
        try:
            if op == 'voto':
                ocorrencia.votar(request.user)
            else:
                ocorrencia.vetar(request.user)
            messages.success(request, u"Voto computado")
        except Exception as e:
            messages.error(request, unicode(e))
    return redirect(reverse('ocorrencia_detail', args=(pk,)))


def change_status(request, pk, status):
    ocorrencia = get_object_or_404(Ocorrencia, pk=pk)
    if request.user.pk != ocorrencia.user.pk:
        raise Http404
    ocorrencia.status = int(status)
    ocorrencia.save()

    return redirect(reverse('ocorrencia_detail', args=(pk,)))


def spam(request, pk):
    if request.method == "POST":
        ocorrencia = get_object_or_404(Ocorrencia, pk=pk)
        try:
            ocorrencia.vetar(request.user)
            Spam.add_spam(ocorrencia)
            messages.success(request, u"Ocorrência Marcada como Spam")
        except:
            messages.error(request, u"Você não pode marcar essa ocorrência como Spam!")
    return redirect(reverse('ocorrencia_detail', args=(pk,)))


@login_required
def ocorrencia_crud(request, pk=None):
    geom = EMPTY_STRING
    if pk:
        ocorrencia = get_object_or_404(Ocorrencia, pk=pk, user=request.user)
        geom = ocorrencia.ponto or ocorrencia.poligono
        title = u'Editar Ocorrência'
    else:
        ocorrencia = None
        title = u'Nova Ocorrência'

    form = OcorrenciaForm(request.POST or None, instance=ocorrencia, request_user=request.user)

    if request.method == 'POST':
        if form.is_valid():
            ocorrencia = form.save()
            messages.success(request, u'Ocorrência salva com sucesso!')
            return redirect(reverse('ocorrencia_crud', args=(ocorrencia.pk,)))
        else:
            geom = form.cleaned_data.get('ponto', EMPTY_STRING)
            if geom != EMPTY_STRING:
                geom = '%s' % geom

    return render(
        request,
        'ocorrencia_form.html',
        {
            'form': form,
            'request': request,
            'user': request.user,
            'geom': geom,
            'title': title
        }
    )


class OcorrenciaDetailView(DetailView):
    queryset = Ocorrencia.objects
    template_name = 'ocorrencia_detail.html'

    def get_context_data(self, **kwargs):
        context = super(OcorrenciaDetailView, self).get_context_data(**kwargs)
        context['title'] = u'Detalhes'
        context['FACEBOOK_APP_ID'] = settings.FACEBOOK_APP_ID
        return context


ocorrencia_detalhes = OcorrenciaDetailView.as_view()


class OcorrenciaListView(ListView):
    model = Ocorrencia
    template_name = 'ocorrencia_list.html'

    def get_context_data(self, **kwargs):
        context = super(OcorrenciaListView, self).get_context_data(**kwargs)
        context['title'] = u'Minhas Ocorrências'
        return context

    def get_queryset(self):
        return super(OcorrenciaListView, self).get_queryset().filter(user=self.request.user).order_by('-date_add')


ocorrencia_list = OcorrenciaListView.as_view()


@login_required
def generic_delete_from_model(request, app_model=None, object_id=None):
    _next = request.GET.get('next', 'home')
    app_name, model_name = app_model.split('.', 1)
    model = get_model(app_name, model_name)
    obj = get_object_or_404(model, pk=object_id)
    can_delete = True
    if hasattr(obj, 'user_can_delete'):
        if not obj.user_can_delete(request.user):
            messages.success(request, u"Não foi possível deletar")
            can_delete = False
    if can_delete:
        obj.delete()
        messages.success(request, u"Deletado com sucesso")
    return redirect(_next)
