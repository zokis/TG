# coding: utf-8
from django import forms

from django.contrib.gis.geos import GEOSGeometry


from mapa_cidadao.core.models import Categoria, Ocorrencia


class SearchForm(forms.Form):
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), label=u"Categoria", required=False)
    data_ini = forms.DateField(label=u"De", required=False)
    data_fim = forms.DateField(label=u"Até", required=False)
    status = forms.ChoiceField(choices=Ocorrencia.STATUS_CHOICES, label=u"Status", required=False)

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset', Ocorrencia.objects)
        super(SearchForm, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.is_valid():
            ocorrencias = self.queryset
            categoria = self.cleaned_data.get('categoria', False)
            if categoria:
                ocorrencias = ocorrencias.filter(categoria=categoria)
            status = self.cleaned_data.get('status', False)
            if status:
                ocorrencias = ocorrencias.filter(status=status)
            data_ini = self.cleaned_data.get('data_ini', False)
            if data_ini:
                ocorrencias = ocorrencias.filter(date_add__gte=data_ini)
            data_fim = self.cleaned_data.get('data_fim', False)
            if data_fim:
                ocorrencias = ocorrencias.filter(date_add__lte=data_fim)
            return ocorrencias
        else:
            return self.queryset


class OcorrenciaForm(forms.ModelForm):
    ponto = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super(OcorrenciaForm, self).__init__(*args, **kwargs)
        self.fields['descricao'].widget.attrs['rows'] = "5"
        self.fields['descricao'].widget.attrs['cols'] = "40"
        self.fields['categoria'].empty_label = None

    def clean(self):
        cleaned_data = super(OcorrenciaForm, self).clean()

        if not cleaned_data.get('ponto', False):
            raise forms.ValidationError(u'Adicione um ponto')
        try:
            self.geom = GEOSGeometry(cleaned_data['ponto'])
        except:
            raise forms.ValidationError(u'Geometria Inválida')
        return cleaned_data

    def save(self, *args, **kwargs):
        commit = kwargs.get('commit', True)
        kwargs['commit'] = False

        instance = super(OcorrenciaForm, self).save(*args, **kwargs)

        instance.set_ponto(self.geom)
        instance.user = self.request_user

        if commit:
            instance.save()
        return instance

    class Meta:
        model = Ocorrencia
        fields = ('categoria', 'titulo', 'descricao', 'ponto')


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
