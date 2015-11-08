# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='OldURL',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('url', models.TextField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='URLChangeMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('object_id', models.TextField()),
                ('method_name', models.TextField()),
                ('current_url', models.TextField(blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('old_urls', models.ManyToManyField(to='url_tracker.OldURL', related_name='model_method')),
            ],
        ),
    ]
