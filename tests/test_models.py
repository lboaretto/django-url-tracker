from django.test import TransactionTestCase

from url_tracker.models import OldURL, URLChangeMethod

from .models import TestModel, RemoveSignals


class TestOldUrlGetNewUrl(TransactionTestCase, RemoveSignals):
    def setUp(self):
        instance = TestModel.objects.create()
        self.url_method_blank = URLChangeMethod.objects.create(
            content_object=instance,
            method_name='get_absolute_url',
            current_url=''
        )
        self.url_method_initial = URLChangeMethod.objects.create(
            content_object=instance,
            method_name='get_absolute_url',
            current_url='initial'
        )
        self.url_method_initial_2 = URLChangeMethod.objects.create(
            content_object=instance,
            method_name='get_absolute_url',
            current_url='initial'
        )
        self.old_url = OldURL.objects.create(url='old_url')

    def test_one_url_returns(self):
        self.old_url.model_method.add(self.url_method_initial)
        self.assertEqual(self.old_url.get_new_url(), 'initial')

    def test_blank_returns_false(self):
        self.old_url.model_method.add(self.url_method_blank)
        self.assertFalse(self.old_url.get_new_url())

    def test_blank_and_other_returns_true(self):
        self.old_url.model_method.add(self.url_method_blank)
        self.old_url.model_method.add(self.url_method_initial)

        self.assertEqual(self.old_url.get_new_url(), 'initial')

    def test_blank_and_other_returns_true_reverse_order(self):
        self.old_url.model_method.add(self.url_method_initial)
        self.old_url.model_method.add(self.url_method_blank)

        self.assertEqual(self.old_url.get_new_url(), 'initial')

    def test_two_urls_returns_true(self):
        self.old_url.model_method.add(self.url_method_initial)
        self.old_url.model_method.add(self.url_method_initial_2)
        self.assertEqual(self.old_url.get_new_url(), 'initial')
