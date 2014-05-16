# coding: utf-8
from os.path import join

from json import dumps

from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.db import IntegrityError

from jsonfield import JSONField

STATUS_CHOICES = (
    (1, u'Aberto'),
    (2, u'Resolvido'),
    (3, u'Reaberto'),
    (4, u'Inapropriado'),
    (5, u'Spam')
)


class Categoria(models.Model):
    _estilo_default = {
        'graphicWidth': 32,
        'graphicHeight': 32,
        'externalGraphic': 'https://cdn2.iconfinder.com/data/icons/snipicons/500/map-marker-32.png',
    }
    estilo_default = dumps(_estilo_default)

    nome = models.CharField('nome', max_length=20)
    descricao = models.CharField(u'Descrição', max_length=200)
    marker = models.FileField(upload_to=lambda i, f: join('markers', 'categoria_%s.png' % i.pk), blank=True, null=True)
    estilo = JSONField(default=estilo_default, blank=True, null=True)

    def get_estilo(self):
        if self.estilo:
            estilo = self.estilo
        else:
            estilo = self._estilo_default.copy()
            if self.marker:
                estilo['externalGraphic'] = self.marker.url
        return estilo

    def __unicode__(self):
        return u'%s' % (self.nome)


class Ocorrencia(models.Model):
    poligono = models.PolygonField('poligono', srid=900913, null=True, blank=True)
    ponto = models.PointField('ponto', srid=900913, null=True, blank=True)
    categoria = models.ForeignKey(Categoria)
    status = models.SmallIntegerField('status', choices=STATUS_CHOICES, default=1)
    titulo = models.CharField(u'Título', max_length=120, blank=False, null=False)
    descricao = models.TextField(u'Descrição', blank=True, null=True)
    user = models.ForeignKey(User)

    def get_estilo(self):
        estilo = self.categoria.get_estilo()
        if self.type == 'ponto':
            # Remove os atributos de estilo para um poligonos
            for remove in ['fillColor', 'fillOpacity', 'strokeWidth', 'strokeColor']:
                if remove in estilo:
                    del estilo[remove]
        else:
            # Remove os atributos de estilo para um pontos
            for remove in ['externalGraphic', 'graphicHeight', 'graphicWidth']:
                if remove in estilo:
                    del estilo[remove]
        if not estilo:
            estilo = {
                'fillColor': '#F00',
                'fillOpacity': 0.5,
                'strokeWidth': 1,
                'strokeColor': '#000',
            }
            if self.type == 'ponto':
                estilo['pointRadius'] = 4
        return dumps(estilo)

    def can_votar(self, user):
        return Voto.can_votar(user, self)

    def can_vetar(self, user):
        return Veto.can_vetar(user, self)

    def votar(self, user):
        if self.can_votar(user):
            if self.user == user:
                raise Exception(u'Você não pode votar em uma Ocorrência sua')
            else:
                return Voto.objects.create(ocorrencia=self, user=user)
        else:
            raise Exception(u'Você não pode votar em uma Ocorrência que você já votou ou vetou')

    def vetar(self, user):
        if self.can_vetar(user):
            if self.user == user:
                raise Exception(u'Você não pode vetar em uma Ocorrência sua')
            else:
                return Voto.objects.create(ocorrencia=self, user=user)
        else:
            raise Exception(u'Você não pode vetar em uma Ocorrência que você já vetou ou votou')

    def get_votos(self):
        return Voto.objects.filter(ocorrencia=self).count()

    def get_vetos(self):
        return Veto.objects.filter(ocorrencia=self).count()

    def set_ponto(self, ponto):
        self.ponto = ponto
        self.poligono = None

    def set_poligono(self, poligono):
        self.poligono = poligono
        self.ponto = None

    _types = {
        True: 'poligono',
        False: 'ponto'
    }

    def save(self, *args, **kwargs):
        if not self.poligono and not self.ponto:
            raise IntegrityError(u'Cadastre um ponto ou um poligono')
        elif self.poligono and self.ponto:
            raise IntegrityError(u'Cadastre apenas um ponto ou um poligono')
        else:
            return super(Ocorrencia, self).save(*args, **kwargs)

    @property
    def type(self):
        return self._types[self.ponto is None]

    objects = models.GeoManager()


class Spam(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia)
    contagem = models.IntegerField(default=0)

    @classmethod
    def add_spam(cls, ocorrencia):
        try:
            spam = cls.objects.get(ocorrencia=ocorrencia)
        except:
            spam = cls()
        if spam.contagem:
            spam.contagem += 1
        else:
            spam.contagem = 1

        if spam.contagem >= 10:
            spam.delete()
            return None
        else:
            spam.save()
            return spam


class Voto(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia)
    user = models.ForeignKey(User)
    date_add = models.DateTimeField(auto_now_add=True)

    @classmethod
    def can_votar(cls, user, ocorrencia):
        votou = cls.objects.filter(user=user, ocorrencia=ocorrencia).count()
        vetou = cls.objects.filter(user=user, ocorrencia=ocorrencia).count()
        return not votou and not vetou

    class Meta:
        ordering = ('date_add',)


class Veto(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia)
    user = models.ForeignKey(User)
    date_add = models.DateTimeField(auto_now_add=True)

    @classmethod
    def can_vetar(cls, user, ocorrencia):
        vetou = cls.objects.filter(user=user, ocorrencia=ocorrencia).count()
        votou = cls.objects.filter(user=user, ocorrencia=ocorrencia).count()
        return not vetou and not votou

    class Meta:
        ordering = ('date_add',)


def custom_objects(Manager=models.Manager, QuerySet=models.query.QuerySet):
    def oe_inner(Mixin, Manager=models.Manager, QuerySet=models.query.QuerySet):
        class MixinManager(Manager, Mixin):
            class MixinQuerySet(QuerySet, Mixin):
                pass

            def get_query_set(self):
                return self.MixinQuerySet(self.model, using=self._db)

        return MixinManager()

    if issubclass(Manager, models.Manager):
        return lambda Mixin: oe_inner(Mixin, Manager, QuerySet)
    else:
        return oe_inner(Mixin=Manager)
