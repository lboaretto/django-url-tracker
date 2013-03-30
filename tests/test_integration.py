from django.test import TransactionTestCase

from url_tracker import track_url_changes_for_model
from url_tracker.models import URLChangeMethod

from .models import TestModel, reverse_model, RemoveSignals


class TestFullStack(TransactionTestCase, RemoveSignals):
    def setUp(self):
        track_url_changes_for_model(TestModel)
        self.instance = TestModel.objects.create(slug='initial')
        self.instance.slug = 'final'
        self.instance.save()

    def test_url_change_get_absolute_url(self):
        url_method = URLChangeMethod.objects.get(method_name='get_absolute_url')

        self.assertEqual(url_method.current_url, reverse_model('final'))

    def test_old_url_get_absolute_url(self):
        self.assertEqual(URLChangeMethod.objects.count(), 1)
        url_method = URLChangeMethod.objects.get(method_name='get_absolute_url')
        old_urls = url_method.old_urls
        self.assertEqual(old_urls.count(), 1)
        old_url = old_urls.all()[0]
        self.assertEqual(old_url.url, reverse_model('initial'))

    def test_redirect_get_absolute_url(self):
        response = self.client.get(reverse_model('initial'))
        self.assertRedirects(
            response,
            reverse_model('final'),
            status_code=301,
            target_status_code=200
        )
