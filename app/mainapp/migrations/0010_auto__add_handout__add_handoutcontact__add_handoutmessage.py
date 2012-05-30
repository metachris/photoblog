# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Handout'
        db.create_table('mainapp_handout', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('views', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('description_md', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description_html', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('mainapp', ['Handout'])

        # Adding M2M table for field contacts on 'Handout'
        db.create_table('mainapp_handout_contacts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('handout', models.ForeignKey(orm['mainapp.handout'], null=False)),
            ('handoutcontact', models.ForeignKey(orm['mainapp.handoutcontact'], null=False))
        ))
        db.create_unique('mainapp_handout_contacts', ['handout_id', 'handoutcontact_id'])

        # Adding M2M table for field photos on 'Handout'
        db.create_table('mainapp_handout_photos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('handout', models.ForeignKey(orm['mainapp.handout'], null=False)),
            ('photo', models.ForeignKey(orm['mainapp.photo'], null=False))
        ))
        db.create_unique('mainapp_handout_photos', ['handout_id', 'photo_id'])

        # Adding M2M table for field tags on 'Handout'
        db.create_table('mainapp_handout_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('handout', models.ForeignKey(orm['mainapp.handout'], null=False)),
            ('tag', models.ForeignKey(orm['mainapp.tag'], null=False))
        ))
        db.create_unique('mainapp_handout_tags', ['handout_id', 'tag_id'])

        # Adding model 'HandoutContact'
        db.create_table('mainapp_handoutcontact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('tel', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('subscribed_to_mail_list', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('mainapp', ['HandoutContact'])

        # Adding model 'HandoutMessage'
        db.create_table('mainapp_handoutmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('handout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mainapp.Handout'])),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('from_contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mainapp.HandoutContact'], null=True, blank=True)),
            ('description_md', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description_html', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('mainapp', ['HandoutMessage'])


    def backwards(self, orm):
        # Deleting model 'Handout'
        db.delete_table('mainapp_handout')

        # Removing M2M table for field contacts on 'Handout'
        db.delete_table('mainapp_handout_contacts')

        # Removing M2M table for field photos on 'Handout'
        db.delete_table('mainapp_handout_photos')

        # Removing M2M table for field tags on 'Handout'
        db.delete_table('mainapp_handout_tags')

        # Deleting model 'HandoutContact'
        db.delete_table('mainapp_handoutcontact')

        # Deleting model 'HandoutMessage'
        db.delete_table('mainapp_handoutmessage')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'mainapp.handout': {
            'Meta': {'object_name': 'Handout'},
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['mainapp.HandoutContact']", 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_md': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'photos': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['mainapp.Photo']", 'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['mainapp.Tag']", 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'mainapp.handoutcontact': {
            'Meta': {'object_name': 'HandoutContact'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'subscribed_to_mail_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tel': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'mainapp.handoutmessage': {
            'Meta': {'object_name': 'HandoutMessage'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_md': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'from_contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mainapp.HandoutContact']", 'null': 'True', 'blank': 'True'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'handout': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mainapp.Handout']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'mainapp.location': {
            'Meta': {'object_name': 'Location'},
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lng': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'})
        },
        'mainapp.photo': {
            'Meta': {'object_name': 'Photo'},
            'date_captured': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_md': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'external_url': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mainapp.Location']", 'null': 'True', 'blank': 'True'}),
            'sets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['mainapp.Set']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['mainapp.Tag']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'views': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'mainapp.set': {
            'Meta': {'object_name': 'Set'},
            'cover_photo': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'set_cover'", 'null': 'True', 'to': "orm['mainapp.Photo']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_md': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'mainapp.tag': {
            'Meta': {'object_name': 'Tag'},
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'})
        },
        'mainapp.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'accepted_eula': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['mainapp']