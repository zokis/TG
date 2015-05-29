# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20150525_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoria',
            name='estilo',
            field=jsonfield.fields.JSONField(default=b'{"graphicHeight":32,"externalGraphic":"http:\\/\\/104.131.23.39\\/media\\/markers\\/C_3674.png","graphicWidth":32}', null=True, blank=True),
            preserve_default=True,
        ),
    ]
