# coding: utf-8
from os.path import join

from ujson import dumps, loads

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.db import IntegrityError
from django.utils.deconstruct import deconstructible

from jsonfield import JSONField


@deconstructible
class MarkerRename(object):
    def __call__(self, instance, filename):
        return join('markers', 'C_%s.png' % str(hash(instance.nome))[1:5])


marker_rename = MarkerRename()


class Categoria(models.Model):
    ESTILO = {
        'graphicWidth': 32,
        'graphicHeight': 32,
        'externalGraphic': 'http://104.131.23.39/media/markers/C_3674.png',
    }

    nome = models.CharField('nome', max_length=75)
    descricao = models.CharField(u'Descrição', max_length=200)
    marker = models.FileField(upload_to=marker_rename, blank=True, null=True)
    estilo = JSONField(default=dumps(ESTILO), blank=True, null=True)
    perigosa = models.BooleanField(default=False)

    def get_estilo(self):
        if self.estilo:
            try:
                estilo = loads(self.estilo)
            except TypeError:
                estilo = None

        if not self.estilo or not estilo:
            estilo = self.ESTILO.copy()

        if self.marker:
            estilo['externalGraphic'] = self.marker.url
        return estilo

    def get_estilo_json(self):
        if self.estilo:
            return self.estilo
        else:
            return dumps(self.get_estilo())

    def __unicode__(self):
        return u'%s' % (self.nome)


class OcorrenciaManager(models.GeoManager):
    def filter_by_geom_and_bbox(self, geom, bbox):
        qs = super(OcorrenciaManager, self).get_queryset()
        if bbox:
            intersection = geom.intersection(bbox)
            if bbox.area == intersection.area:
                return qs.filter(ponto__bboverlaps=bbox)
            else:
                return qs.filter(ponto__intersects=intersection)
        else:
            return qs.filter(ponto__intersects=geom)


class Ocorrencia(models.Model):
    STATUS_CHOICES = (
        (1, u'Aberto'),
        (2, u'Reaberto'),
        (3, u'Resolvido'),
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

    def get_estilo_json(self):
        return dumps(self.get_estilo())

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
        return estilo

    def can_votar(self, user):
        return Voto.can_votar(user, self)

    def can_vetar(self, user):
        return Veto.can_vetar(user, self)

    def votar(self, user):
        if self.can_votar(user):
            return Voto.objects.create(ocorrencia=self, user=user)
        else:
            raise Voto.VotoException(u'Você não pode votar nesta Ocorrência')

    def vetar(self, user):
        if self.can_vetar(user):
            return Veto.objects.create(ocorrencia=self, user=user)
        else:
            raise Veto.VetoException(u'Você não pode vetar esta Ocorrência')

    def get_votos(self):
        return Voto.objects.filter(ocorrencia=self).count()

    def get_vetos(self):
        return Veto.objects.filter(ocorrencia=self).count()

    def set_ponto(self, ponto):
        self.ponto = ponto

    def save(self, *args, **kwargs):
        if not self.ponto:
            raise IntegrityError(u'Cadastre um ponto ou um poligono')
        return super(Ocorrencia, self).save(*args, **kwargs)

    objects = OcorrenciaManager()


class Spam(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia)
    contagem = models.IntegerField(default=0)

    @classmethod
    def add_spam(cls, ocorrencia):
        spam = cls.objects.get_or_create(ocorrencia=ocorrencia)
        spam.contagem = (spam.contagem or 0) + 1
        if spam.contagem >= settings.SPAM_DELETE:
            ocorrencia.delete()
        else:
            spam.save()


class Voto(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia)
    user = models.ForeignKey(User)
    date_add = models.DateTimeField(auto_now_add=True)

    class VotoException(Exception):
        pass

    @classmethod
    def can_votar(cls, user, ocorrencia):
        if user == ocorrencia.user:
            return False
        if user.is_anonymous():
            return False
        votou = cls.objects.filter(user=user, ocorrencia=ocorrencia).count()
        vetou = Veto.objects.filter(user=user, ocorrencia=ocorrencia).count()
        return not votou and not vetou

    class Meta:
        ordering = ('date_add',)


class Veto(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia)
    user = models.ForeignKey(User)
    date_add = models.DateTimeField(auto_now_add=True)

    class VetoException(Exception):
        pass

    @classmethod
    def can_vetar(cls, user, ocorrencia):
        if user == ocorrencia.user:
            return False
        if user.is_anonymous():
            return False
        vetou = cls.objects.filter(user=user, ocorrencia=ocorrencia).count()
        votou = Voto.objects.filter(user=user, ocorrencia=ocorrencia).count()
        return not vetou and not votou

    class Meta:
        ordering = ('date_add',)
