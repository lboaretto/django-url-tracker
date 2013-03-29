# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'URLChangeRecord'
        db.delete_table(u'url_tracker_urlchangerecord')

        # Adding model 'URLChangeMethod'
        db.create_table(u'url_tracker_urlchangemethod', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.TextField')()),
            ('method_name', self.gf('django.db.models.fields.TextField')()),
            ('current_url', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'url_tracker', ['URLChangeMethod'])

        # Adding M2M table for field old_urls on 'URLChangeMethod'
        db.create_table(u'url_tracker_urlchangemethod_old_urls', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('urlchangemethod', models.ForeignKey(orm[u'url_tracker.urlchangemethod'], null=False)),
            ('oldurl', models.ForeignKey(orm[u'url_tracker.oldurl'], null=False))
        ))
        db.create_unique(u'url_tracker_urlchangemethod_old_urls', ['urlchangemethod_id', 'oldurl_id'])

        # Adding model 'OldURL'
        db.create_table(u'url_tracker_oldurl', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.TextField')(unique=True)),
        ))
        db.send_create_signal(u'url_tracker', ['OldURL'])


    def backwards(self, orm):
        # Adding model 'URLChangeRecord'
        db.create_table(u'url_tracker_urlchangerecord', (
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('new_url', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('old_url', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('date_changed', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('url_tracker', ['URLChangeRecord'])

        # Deleting model 'URLChangeMethod'
        db.delete_table(u'url_tracker_urlchangemethod')

        # Removing M2M table for field old_urls on 'URLChangeMethod'
        db.delete_table('url_tracker_urlchangemethod_old_urls')

        # Deleting model 'OldURL'
        db.delete_table(u'url_tracker_oldurl')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'url_tracker.oldurl': {
            'Meta': {'object_name': 'OldURL'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        u'url_tracker.urlchangemethod': {
            'Meta': {'object_name': 'URLChangeMethod'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'current_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method_name': ('django.db.models.fields.TextField', [], {}),
            'object_id': ('django.db.models.fields.TextField', [], {}),
            'old_urls': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'model_method'", 'symmetrical': 'False', 'to': u"orm['url_tracker.OldURL']"})
        }
    }

    complete_apps = ['url_tracker']