# coding: utf-8
from datetime import timedelta
from ujson import dumps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.gis.geos import Polygon
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from django.http import HttpResponse, Http404, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import render_to_response
from django.template import defaultfilters as filters
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, TemplateView, View
from django.views.generic.detail import DetailView

from django_user_agents.utils import get_user_agent

from mapa_cidadao.core.forms import OcorrenciaForm, ContatoForm, SearchForm
from mapa_cidadao.core.models import Categoria, Ocorrencia, Spam, Voto, Veto

from mapa_cidadao.core.utils import get_geom_from_cache, is_last


EMPTY_STRING = ''


class GetCurrentGeomView(View):
    def get(self, request):
        return HttpResponse(
            get_geom_from_cache().json,
            content_type="application/json"
        )

    def post(self, request):
        return self.get(request)

get_current_geom = GetCurrentGeomView.as_view()


class MobTemplateMixin(object):
    def get_template_names(self):
        user_agent = get_user_agent(self.request)
        if user_agent.is_mobile:
            return [self.template_name.replace('.html', '_mob.html')]
        return [self.template_name]


def streaming_ocorrencias(ocorrencias, dumps=dumps):
    yield '[\n'
    for ocorrencia, last in is_last(ocorrencias):
        yield dumps({
            'wkt': filters.safe(ocorrencia.ponto.wkt),
            'name': ocorrencia.titulo,
            'description': filters.wordwrap(ocorrencia.descricao, 10),
            'pk': ocorrencia.pk,
            'style': ocorrencia.get_estilo()
        })
        if not last:
            yield ',\n'
    yield '\n]'


class LoadOcorrenciasView(View):
    def get(self, request, x0=None, y0=None, x1=None, y1=None):
        bbox = Polygon.from_bbox([x0, y0, x1, y1]) if x0 else None
        geom = get_geom_from_cache()
        ocorrencias = Ocorrencia.objects.filter_by_geom_and_bbox(geom, bbox)
        if not get_user_agent(request).is_mobile:
            ocorrencias = SearchForm(request.GET or None, queryset=ocorrencias).get_queryset()
        response = StreamingHttpResponse(streaming_ocorrencias(ocorrencias), content_type='application/json')
        response['Cache-Control'] = 'max-age=0, no-cache, no-store'
        return response

    def post(self, request, x0=None, y0=None, x1=None, y1=None):
        return self.get(request, x0, y0, x1, y1)

load_ocorrencias = LoadOcorrenciasView.as_view()


class IndexView(TemplateView):
    template_name = 'index.html'

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user_agent = get_user_agent(self.request)
        context = super(IndexView, self).get_context_data(**kwargs)
        context['params'] = self.request.POST
        if not user_agent.is_mobile:
            context['search_form'] = SearchForm(self.request.POST or None)
        else:
            context['search_form'] = None
        context['request'] = self.request
        context['user'] = self.request.user
        context['categorias'] = Categoria.objects.all()
        return context

index = IndexView.as_view()


class EstatisticasView(TemplateView):
    template_name = 'estatisticas.html'

    def get_context_data(self, **kwargs):
        context = super(EstatisticasView, self).get_context_data(**kwargs)
        users = User.objects.filter(is_staff=False, is_active=True).count()
        oco_total = Ocorrencia.objects.all().count()
        ocos_cats = []

        for cat in Categoria.objects.all():
            oco = Ocorrencia.objects.filter(categoria=cat).count()
            ocos_cats.append((cat.nome, oco, (oco * 100.0) / oco_total))

        oco_7_dias = Ocorrencia.objects.filter(date_add__gte=timezone.now().date() - timedelta(days=7)).count()
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

        context.update({
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
        })
        return context

estatisticas = cache_page(60 * 25)(EstatisticasView.as_view())


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


class AboutView(TemplateView):
    template_name = 'about.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        context['title'] = u'Sobre'
        return context

about = AboutView.as_view()


class VotoView(View):
    def post(self, request, pk, op='votar'):
        ocorrencia = get_object_or_404(Ocorrencia, pk=pk)
        try:
            if op == 'votar':
                ocorrencia.votar(request.user)
            else:
                ocorrencia.vetar(request.user)
            messages.success(request, u"Voto computado")
        except Voto.VotoException as e:
            messages.error(request,  unicode(e))
        except Veto.VetoException as e:
            messages.error(request,  unicode(e))
        return redirect(reverse('ocorrencia_detail', args=(pk,)))

votar = VotoView.as_view()


class ChangeStatusView(View):
    def get(self, request, pk, status):
        ocorrencia = get_object_or_404(Ocorrencia, pk=pk)
        if request.user.pk != ocorrencia.user.pk:
            raise Http404
        ocorrencia.status = int(status)
        ocorrencia.save()
        return redirect(reverse('ocorrencia_detail', args=(pk,)))

change_status = ChangeStatusView.as_view()


class SpamView(View):
    def post(self, request, pk):
        ocorrencia = get_object_or_404(Ocorrencia, pk=pk)
        try:
            ocorrencia.vetar(request.user)
            Spam.add_spam(ocorrencia)
            messages.success(request, u"Ocorrência Marcada como Spam")
        except:
            messages.error(request, u"Você não pode marcar essa ocorrência como Spam!")
        return redirect(reverse('ocorrencia_detail', args=(pk,)))

spam = SpamView.as_view()


@login_required
def ocorrencia_crud(request, pk=None):
    user_agent = get_user_agent(request)
    if not user_agent.is_mobile:
        template = 'ocorrencia_form.html'
    else:
        template = 'ocorrencia_form_mob.html'

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
        template,
        {
            'form': form,
            'request': request,
            'user': request.user,
            'geom': geom,
            'title': title
        }
    )


class OcorrenciaDetailView(MobTemplateMixin, DetailView):
    queryset = Ocorrencia.objects
    template_name = 'ocorrencia_detail.html'

    def get_context_data(self, **kwargs):
        context = super(OcorrenciaDetailView, self).get_context_data(**kwargs)
        context['title'] = u'Detalhes - %s' % context['object']
        context['FACEBOOK_APP_ID'] = settings.FACEBOOK_APP_ID
        return context

ocorrencia_detalhes = OcorrenciaDetailView.as_view()


class OcorrenciaListView(MobTemplateMixin, ListView):
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
