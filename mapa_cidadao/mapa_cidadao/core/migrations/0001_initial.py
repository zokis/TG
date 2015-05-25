# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import django.contrib.gis.db.models.fields
from django.conf import settings
import mapa_cidadao.core.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=20, verbose_name=b'nome')),
                ('descricao', models.CharField(max_length=200, verbose_name='Descri\xe7\xe3o')),
                ('marker', models.FileField(null=True, upload_to=mapa_cidadao.core.models.MarkerRename(b'/avatars'), blank=True)),
                ('estilo', jsonfield.fields.JSONField(default=b'{"graphicHeight": 32, "externalGraphic": "https://cdn2.iconfinder.com/data/icons/snipicons/500/map-marker-32.png", "graphicWidth": 32}', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ocorrencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ponto', django.contrib.gis.db.models.fields.PointField(srid=900913, null=True, verbose_name=b'ponto', blank=True)),
                ('status', models.SmallIntegerField(default=1, verbose_name=b'status', choices=[(1, 'Aberto'), (2, 'Reaberto'), (3, 'Resolvido'), (4, 'Inapropriado'), (5, 'Spam')])),
                ('titulo', models.CharField(max_length=120, verbose_name='T\xedtulo')),
                ('descricao', models.TextField(null=True, verbose_name='Descri\xe7\xe3o', blank=True)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('categoria', models.ForeignKey(to='core.Categoria')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Spam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contagem', models.IntegerField(default=0)),
                ('ocorrencia', models.ForeignKey(to='core.Ocorrencia')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Veto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_add', models.DateTimeField(auto_now_add=True)),
                ('ocorrencia', models.ForeignKey(to='core.Ocorrencia')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('date_add',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Voto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_add', models.DateTimeField(auto_now_add=True)),
                ('ocorrencia', models.ForeignKey(to='core.Ocorrencia')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('date_add',),
            },
            bases=(models.Model,),
        ),
    ]
