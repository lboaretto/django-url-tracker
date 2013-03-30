from django.test import TransactionTestCase
from django.core.exceptions import ImproperlyConfigured

from url_tracker.trackers import lookup_previous_url, track_changed_url, track_url_changes_for_model
from url_tracker.models import URLChangeMethod

from .models import TestModel, reverse_model


class TestTrackUrlForModel(TransactionTestCase):

    def test_model_without_url_method(self):
        URLChangeMethod.url_tracking_methods = []
        self.assertRaises(
            ImproperlyConfigured,
            track_url_changes_for_model,
            URLChangeMethod,
        )


class TestLookupUrl(TransactionTestCase):

    def test_new_instance_dont_create(self):
        unsaved_instance = TestModel(slug='initial')
        lookup_previous_url(unsaved_instance)
        self.assertFalse(URLChangeMethod.objects.count())

    def test_url_no_reverse_dont_create(self):
        instance = TestModel.objects.create(slug='//')
        lookup_previous_url(instance)

        self.assertFalse(URLChangeMethod.objects.count())

    def test_url_blank_dont_create(self):
        instance = TestModel.objects.create(text='')
        lookup_previous_url(instance)

        self.assertFalse(URLChangeMethod.objects.filter(
            method_name__exact='get_text').count())

    def test_new_instance_create(self):
        instance = TestModel.objects.create(slug='initial')
        instance.get_absolute_url()
        lookup_previous_url(instance)

        self.assertEqual(URLChangeMethod.objects.count(), 1)
        url_method = URLChangeMethod.objects.all()[0]
        self.assertEqual(url_method.method_name, 'get_absolute_url')

        self.assertEqual(url_method.old_urls.count(), 1)
        old_url = url_method.old_urls.all()[0]
        self.assertEqual(old_url.url, reverse_model('initial'))


class TestChangedUrl(TransactionTestCase):
    def test_no_url_change_method(self):
        instance = TestModel.objects.create()
        track_changed_url(instance)

        self.assertFalse(URLChangeMethod.objects.count())

    def test_url_no_reverse_dont_create(self):
        instance = TestModel.objects.create(slug='//')
        track_changed_url(instance)

        self.assertFalse(URLChangeMethod.objects.count())

    def test_same_urls_delete_old_url(self):
        instance = TestModel.objects.create(slug='initial')
        url_method = URLChangeMethod.objects.create(
            content_object=instance,
            method_name='get_absolute_url',
        )
        url_method.old_urls.create(url=reverse_model('initial'))
        url_method.old_urls.create(url=reverse_model('another'))

        track_changed_url(instance)
        self.assertEqual(url_method.old_urls.count(), 1)

    def test_save_current_url(self):
        instance = TestModel.objects.create(slug='current')
        url_method = URLChangeMethod.objects.create(
            content_object=instance,
            method_name='get_absolute_url',
        )
        url_method.old_urls.create(url=reverse_model('another'))
        track_changed_url(instance)
        self.assertEqual(URLChangeMethod.objects.count(), 1)
        url_method = URLChangeMethod.objects.all()[0]
        self.assertEqual(url_method.current_url, reverse_model('current'))

    def test_same_url_dont_create(self):
        instance = TestModel.objects.create(slug='initial')
        url_method = URLChangeMethod.objects.create(
            content_object=instance,
            method_name='get_absolute_url',
        )
        url_method.old_urls.create(url=reverse_model('initial'))
        track_changed_url(instance)
        self.assertEqual(URLChangeMethod.objects.count(), 0)
