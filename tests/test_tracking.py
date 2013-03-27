"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from mock import Mock

from django.test import TestCase

from url_tracker import URLTrackingError
from url_tracker import trackers
from url_tracker.models import URLChangeRecord
from url_tracker.mixins import URLTrackingMixin


class TrackedModelMock(URLTrackingMixin, Mock):
    pass


class TestTracking(TestCase):

    def setUp(self):
        class DoesNotExist(BaseException):
            pass

        self.model_mock = TrackedModelMock
        self.model_mock.get_absolute_url = Mock()

        self.tracked_model = self.model_mock(name='TrackedModel')
        self.tracked_model._get_tracked_url = lambda: u'/the/new/one/'

        def raise_exception(*args, **kwargs):
            raise self.tracked_model.__class__.DoesNotExist

        class_objects = Mock(name="MockModelManager")
        class_objects.get = raise_exception

        self.tracked_model.__class__.objects = class_objects
        self.tracked_model.__class__.DoesNotExist = DoesNotExist

        self.tracked_db_model = self.model_mock(name='TrackeDatabaseModel')
        self.tracked_db_model._get_tracked_url = lambda: u'/the/old/one/'

    def test_trackers_model_without_url_method(self):
        instance = TrackedModelMock()
        instance.url_tracking_methods = []
        self.assertRaises(
            URLTrackingError,
            trackers.track_url_changes_for_model,
            instance,
        )

    def test_lookup_url_with_existing_instance(self):
        def return_instance(pk):
            return self.tracked_db_model

        class_objects = Mock(name='MockModelManager')
        class_objects.get = return_instance
        self.tracked_model.__class__.objects = class_objects
        self.tracked_model.get_absolute_url.return_value = u'/the/old/one/'

        trackers.track_url_changes_for_model(TrackedModelMock)
        trackers.lookup_previous_url(self.tracked_model)

        expected_dict = {'get_absolute_url': u'/the/old/one/'}
        self.assertEquals(self.tracked_model._old_urls, expected_dict)

    def test_create_delete_record_for_url_method_returning_none(self):
        instance = self.tracked_model
        instance.get_absolute_url.return_value = None
        instance._old_urls = {'get_absolute_url': u'/the/old/one/'}

        trackers.track_changed_url(instance)
        self.assertEquals(URLChangeRecord.objects.count(), 1)
        record = URLChangeRecord.objects.all()[0]
        self.assertEquals(record.deleted, True)

    def test_track_changed_url_with_new_instance(self):
        instance = self.tracked_model
        instance.get_absolute_url.return_value = u'/the/new/one/'
        instance._old_urls = {'get_absolute_url': None}

        trackers.track_changed_url(instance)
        self.assertEquals(URLChangeRecord.objects.count(), 0)

    def test_track_changed_url_with_unchanged_url(self):
        instance = self.tracked_model
        instance.get_absolute_url.return_value = u'/the/old/one/'
        instance._old_urls = {'get_absolute_url': u'/the/old/one/'}

        trackers.track_changed_url(instance)
        self.assertEquals(URLChangeRecord.objects.count(), 0)

    def test_track_changed_url_without_existing_records(self):
        instance = self.tracked_model
        instance.get_absolute_url.return_value = u'/the/new/one/'
        instance._old_urls = {'get_absolute_url': u'/the/old/one/'}

        trackers.track_changed_url(instance)
        self.assertEquals(URLChangeRecord.objects.count(), 1)
        record = URLChangeRecord.objects.all()[0]
        self.assertEquals(record.new_url, u'/the/new/one/')
        self.assertEquals(record.old_url, u'/the/old/one/')
        self.assertEquals(record.deleted, False)

    def test_track_changed_url_with_existing_records(self):
        URLChangeRecord.objects.create(old_url='/the/oldest/one/', new_url='/the/old/one/')
        URLChangeRecord.objects.create(old_url='/one/', new_url='/the/')

        instance = self.tracked_model
        instance.get_absolute_url.return_value = u'/the/new/one/'
        instance._old_urls = {'get_absolute_url': u'/the/old/one/'}

        trackers.track_changed_url(instance)
        self.assertEquals(URLChangeRecord.objects.count(), 3)
        record = URLChangeRecord.objects.get(pk=1)
        self.assertEquals(record.old_url, u'/the/oldest/one/')
        self.assertEquals(record.new_url, u'/the/new/one/')
        self.assertEquals(record.deleted, False)
        record = URLChangeRecord.objects.get(pk=3)
        self.assertEquals(record.old_url, u'/the/old/one/')
        self.assertEquals(record.new_url, u'/the/new/one/')
        self.assertEquals(record.deleted, False)

    def test_track_changed_url_with_existing_records_and_old_url(self):
        URLChangeRecord.objects.create(old_url='/the/oldest/one/', new_url='/the/old/one/')
        URLChangeRecord.objects.create(old_url='/the/old/one/', new_url='/the/')

        instance = self.tracked_model
        instance.get_absolute_url.return_value = u'/the/new/one/'
        instance._old_urls = {'get_absolute_url': u'/the/old/one/'}

        trackers.track_changed_url(instance)
        self.assertEquals(URLChangeRecord.objects.count(), 2)
        record = URLChangeRecord.objects.get(pk=1)
        self.assertEquals(record.old_url, u'/the/oldest/one/')
        self.assertEquals(record.new_url, u'/the/new/one/')
        self.assertEquals(record.deleted, False)
        record = URLChangeRecord.objects.get(pk=2)
        self.assertEquals(record.old_url, u'/the/old/one/')
        self.assertEquals(record.new_url, u'/the/new/one/')
        self.assertEquals(record.deleted, False)

    def test_track_changed_url_with_existing_deleted_record(self):
        URLChangeRecord.objects.create(old_url='/the/oldest/one/',
                                       new_url='/the/old/one/',
                                       deleted=True)
        URLChangeRecord.objects.create(old_url='/one/', new_url='/the/')

        instance = self.tracked_model
        instance.get_absolute_url.return_value = u'/the/new/one/'
        instance._old_urls = {'get_absolute_url': u'/the/old/one/'}

        trackers.track_changed_url(instance)

        record = URLChangeRecord.objects.get(pk=3)
        self.assertEquals(record.old_url, u'/the/old/one/')
        self.assertEquals(record.new_url, u'/the/new/one/')
        self.assertEquals(record.deleted, False)

    def test_track_deleted_url_without_existing_records(self):
        instance = self.tracked_model
        instance.get_absolute_url.return_value = u'/the/new/one/'
        instance._old_urls = {'get_absolute_url': u'/the/old/one/'}

        trackers.track_deleted_url(instance)

        self.assertEquals(URLChangeRecord.objects.count(), 1)
        record = URLChangeRecord.objects.all()[0]
        self.assertEquals(record.new_url, None)
        self.assertEquals(record.old_url, '/the/old/one/')
        self.assertEquals(record.deleted, True)

    def test_track_changed_url_deleting_exsiting_record_with_new_url(self):
        URLChangeRecord.objects.create(old_url='/the/new/one/', new_url='/the/')

        instance = self.tracked_model
        instance.get_absolute_url.return_value = u'/the/new/one/'
        instance._old_urls = {'get_absolute_url': '/the/old/one/'}

        trackers.track_changed_url(instance)
        self.assertEquals(URLChangeRecord.objects.count(), 1)
        record = URLChangeRecord.objects.get(pk=1)
        self.assertEquals(record.old_url, u'/the/old/one/')
        self.assertEquals(record.new_url, u'/the/new/one/')
        self.assertEquals(record.deleted, False)
