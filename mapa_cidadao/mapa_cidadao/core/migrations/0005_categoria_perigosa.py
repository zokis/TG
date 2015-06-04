# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20150529_1806'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoria',
            name='perigosa',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
