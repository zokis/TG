# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mapa_cidadao.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoria',
            name='marker',
            field=models.FileField(null=True, upload_to=mapa_cidadao.core.models.MarkerRename(), blank=True),
            preserve_default=True,
        ),
    ]
