# coding: utf-8
from os.path import join

from json import dumps

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.db import IntegrityError

from jsonfield import JSONField


class Categoria(models.Model):
    ESTILO = {
        'graphicWidth': 32,
        'graphicHeight': 32,
        'externalGraphic': 'https://cdn2.iconfinder.com/data/icons/snipicons/500/map-marker-32.png',
    }

    nome = models.CharField('nome', max_length=20)
    descricao = models.CharField(u'Descrição', max_length=200)
    marker = models.FileField(upload_to=lambda i, f: join('markers', 'categoria_%s.png' % i.pk), blank=True, null=True)
    estilo = JSONField(default=dumps(ESTILO), blank=True, null=True)

    def get_estilo(self):
        if self.estilo:
            estilo = self.estilo
        else:
            estilo = self.ESTILO.copy()
            if self.marker:
                estilo['externalGraphic'] = self.marker.url
        return estilo

    def __unicode__(self):
        return u'%s' % (self.nome)


class Ocorrencia(models.Model):
    STATUS_CHOICES = (
        (1, u'Aberto'),
        (2, u'Resolvido'),
        (3, u'Reaberto'),
        (4, u'Inapropriado'),
        (5, u'Spam')
    )

    ponto = models.PointField('ponto', srid=900913, null=True, blank=True)
    categoria = models.ForeignKey(Categoria)
    status = models.SmallIntegerField('status', choices=STATUS_CHOICES, default=1)
    titulo = models.CharField(u'Título', max_length=120, blank=False, null=False)
    descricao = models.TextField(u'Descrição', blank=True, null=True)
    user = models.ForeignKey(User)
    date_add = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def user_can_delete(self, user):
        return user == self.user

    def get_estilo(self):
        estilo = self.categoria.get_estilo()
        if not estilo:
            estilo = {
                'fillColor': '#F00',
                'fillOpacity': 0.5,
                'strokeWidth': 1,
                'strokeColor': '#F00',
                'pointRadius': 4
            }
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

    def save(self, *args, **kwargs):
        if not self.poligono and not self.ponto:
            raise IntegrityError(u'Cadastre um ponto ou um poligono')
        elif self.poligono and self.ponto:
            raise IntegrityError(u'Cadastre apenas um ponto ou um poligono')
        else:
            return super(Ocorrencia, self).save(*args, **kwargs)

    objects = models.GeoManager()


class Spam(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia)
    contagem = models.IntegerField(default=0)

    @classmethod
    def add_spam(cls, ocorrencia):
        spam = cls.objects.get(ocorrencia=ocorrencia)
        spam.contagem = (spam.contagem or 1) + 1
        if spam.contagem >= settings.SPAM_DELETE:
            spam.ocorrencia.delete()
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
