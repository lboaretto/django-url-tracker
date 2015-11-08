from django.test import TransactionTestCase
from django.core.exceptions import ImproperlyConfigured
from django.db.models import signals

from url_tracker.trackers import lookup_previous_url, track_changed_url, track_url_changes_for_model, add_old_url
from url_tracker.models import URLChangeMethod

from .models import TestModel, reverse_model, RemoveSignals


class TestTrackUrlForModel(RemoveSignals, TransactionTestCase):

    def setUp(self):
        self.function_from_signals = lambda signal: list(map(lambda _: _[1], signal.receivers))

    def test_model_without_url_method(self):
        TestModel.url_tracking_methods = []
        self.assertRaises(
            ImproperlyConfigured,
            track_url_changes_for_model,
            TestModel,
        )

    def test_adds_pre_save_signal(self):
        self.assertFalse(self.function_from_signals(signals.pre_save))
        track_url_changes_for_model(TestModel)
        self.assertIn(lookup_previous_url, self.function_from_signals(signals.pre_save))

    def test_adds_post_save_signal(self):
        self.assertFalse(self.function_from_signals(signals.pre_save))
        track_url_changes_for_model(TestModel)
        self.assertIn(track_changed_url, self.function_from_signals(signals.post_save))


class TestLookupUrl(RemoveSignals, TransactionTestCase):

    def test_new_instance_dont_create(self):
        unsaved_instance = TestModel(slug='initial')
        lookup_previous_url(unsaved_instance)
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


class TestChangedUrl(RemoveSignals, TransactionTestCase):
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


class TestAddOldUrl(RemoveSignals, TransactionTestCase):
    def test_without_previous_tracking(self):
        instance = TestModel.objects.create(slug='initial')
        add_old_url(instance, 'get_absolute_url', 'old_url')
        self.assertEqual(URLChangeMethod.objects.count(), 1)
        url_method = URLChangeMethod.objects.all()[0]
        self.assertEqual(url_method.method_name, 'get_absolute_url')
        self.assertEqual(url_method.old_urls.count(), 1)
        old_url = url_method.old_urls.all()[0]
        self.assertEqual(old_url.url, 'old_url')
