# coding: utf-8
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.db import IntegrityError

STATUS_CHOICES = (
    (1, u'Aberto'),
    (2, u'Resolvido'),
    (3, u'Reaberto'),
    (4, u'Inapropriado'),
    (5, u'Spam')
)


class Categoria(models.Model):
    nome = models.CharField('nome', max_length=20)
    descricao = models.CharField(u'Descrição', max_length=200)

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


class Voto(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia)
    user = models.ForeignKey(User)
    date_add = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_add',)


class Veto(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia)
    user = models.ForeignKey(User)
    date_add = models.DateTimeField(auto_now_add=True)

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
