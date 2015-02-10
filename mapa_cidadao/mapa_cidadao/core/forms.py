# coding: utf-8
from django import forms
from django.conf import settings
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.text import smart_split
from django.utils.translation import ugettext_lazy as _

from django.contrib.gis.geos import GEOSGeometry


from .models import Ocorrencia


DEFAULT_STOPWORDS = ('de,o,a,os,as')

if settings.DATABASES:
    DATABASE_ENGINE = settings.DATABASES[settings.DATABASES.keys()[0]]['ENGINE'].split('.')[-1]
else:
    DATABASE_ENGINE = settings.DATABASE_ENGINE


class BaseSearchForm(forms.Form):
    """See http://gregbrown.co.nz/code/django-simple-search/ for details"""

    STOPWORD_LIST = DEFAULT_STOPWORDS.split(',')
    DEFAULT_OPERATOR = Q.__and__

    q = forms.CharField(label=_('Search'), required=False)

    def clean_q(self):
        return self.cleaned_data['q'].strip()

    order_by = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        abstract = True

        base_qs = None

        # example: ['name', 'category__name', '@description', '=id']
        search_fields = None

        # should be a list of  pairs, of the form ('field1,field2', WEIGHTING)
        # where WEIGHTING is an integer. Assumes the relevant indexes have been
        # created

        fulltext_indexes = None

    def __init__(self, *args, **kwargs):
        super(BaseSearchForm, self).__init__(*args, **kwargs)
        self.fields['q'].widget.attrs = {'placeholder': self.get_q_placeholder()}

    def get_advanced_search_fields(self):
        return [field for idx, field in enumerate(self) if idx not in (0, 1)]

    def get_q_placeholder(self):
        return ''

    def construct_search(self, field_name, first):
        if field_name.startswith('^'):
            if first:
                return "%s__istartswith" % field_name[1:]
            else:
                return "%s__icontains" % field_name[1:]
        elif field_name.startswith('='):
            return "%s__iexact" % field_name[1:]
        elif field_name.startswith('@'):
            if DATABASE_ENGINE == 'mysql':
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name[1:]
        else:
            return "%s__icontains" % field_name

    def get_text_query_bits(self, query_string):
        """filter stopwords but only if there are useful words"""

        split_q = list(smart_split(query_string))
        filtered_q = [bit for bit in split_q if bit not in self.STOPWORD_LIST]

        if len(filtered_q):
            return filtered_q
        else:
            return split_q

    def get_text_search_query(self, query_string):
        filters = []
        first = True

        for bit in self.get_text_query_bits(query_string):
            or_queries = [Q(**{self.construct_search(str(field_name), first): bit}) for field_name in self.Meta.search_fields]
            filters.append(reduce(Q.__or__, or_queries))
            first = False

        if len(filters):
            return reduce(self.DEFAULT_OPERATOR, filters)
        else:
            return False

    def construct_filter_args(self, cleaned_data):
        args = []

        # if its an instance of Q, append to filter args
        # otherwise assume an exact match lookup
        for field in cleaned_data:

            if hasattr(self, 'prepare_%s' % field):
                q_obj = getattr(self, 'prepare_%s' % field)()
                if q_obj:
                    args.append(q_obj)
            elif isinstance(cleaned_data[field], Q):
                args.append(cleaned_data[field])
            elif field == 'order_by':
                pass  # special case - ordering handled in get_result_queryset
            elif cleaned_data[field]:
                if isinstance(cleaned_data[field], list) or isinstance(cleaned_data[field], QuerySet):
                    args.append(Q(**{field + '__in': cleaned_data[field]}))
                else:
                    args.append(Q(**{field: cleaned_data[field]}))

        return args

    def get_result_queryset(self):
        qs = self.Meta.base_qs

        cleaned_data = self.cleaned_data.copy()
        query_text = cleaned_data.pop('q', None)

        qs = qs.filter(*self.construct_filter_args(cleaned_data))

        if query_text:
            # construct text search for sqlite, or for when no fulltext indexes are defined
            text_q = self.get_text_search_query(query_text)
            if text_q:
                qs = qs.filter(text_q)
            else:
                qs = qs.none()

        if self.cleaned_data['order_by']:
            qs = qs.order_by(*self.cleaned_data['order_by'].split(','))

        return qs

    def get_result_queryset_by_user(self, user):
        return self.get_result_queryset().by_user(user)


class OcorrenciaForm(forms.ModelForm):
    geom = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super(OcorrenciaForm, self).__init__(*args, **kwargs)
        self.fields['descricao'].widget.attrs['rows'] = "5"
        self.fields['descricao'].widget.attrs['cols'] = "40"
        self.fields['categoria'].empty_label = None

        for key, field in self.fields.items():
            field.widget.attrs['class'] = 'input-xxlarge'

    def clean(self):
        cleaned_data = super(OcorrenciaForm, self).clean()

        if not cleaned_data.get('geom', False):
            raise forms.ValidationError(u'Desenhe um polígono ou adicione um ponto')
        try:
            GEOSGeometry(cleaned_data['geom'])
        except:
            raise forms.ValidationError(u'Geometria Inválida')
        return cleaned_data

    def save(self, *args, **kwargs):
        commit = kwargs.get('commit', True)
        kwargs['commit'] = False

        instance = super(OcorrenciaForm, self).save(*args, **kwargs)

        geom = GEOSGeometry(self.cleaned_data['geom'])
        if geom.geom_type == 'Point':
            instance.set_ponto(geom)
        else:
            instance.set_poligono(geom)

        instance.user = self.request_user

        if commit:
            instance.save()
        return instance

    class Meta:
        model = Ocorrencia
        fields = ('categoria', 'titulo', 'descricao')


class ContatoForm(forms.Form):
    assuntos = (
        (1, u'Escolha uma Opção'),
        (2, u'Assunto Geral'),
        (3, u'Sugestão'),
        (4, u'Encontrei um Problema'),
        (5, u'Suporte')
    )
    nome = forms.CharField(max_length=25, label="Nome", widget=forms.TextInput(attrs={'class': 'contact-form'}))
    email = forms.EmailField(label="Email", widget=forms.TextInput(attrs={'class': 'contact-form'}))
    assunto = forms.ChoiceField(choices=assuntos, widget=forms.Select(attrs={'class': 'contact-form'}))

    mensagem = forms.CharField(widget=forms.Textarea(attrs={'class': 'contact-form'}))