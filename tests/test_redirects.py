from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings

from url_tracker.models import OldURL, URLChangeMethod
from url_tracker.middleware import URLChangePermanentRedirectMiddleware
from .models import TestModel


@override_settings(APPEND_SLASH=False)
class RedirectTests(TestCase):

    def setUp(self):
        self.TestModel = TestModel.objects.create()
        self.OldUrl = OldURL.objects.create(
            url='/initial',
        )
        self.URLChangeMethod = URLChangeMethod.objects.create(
            content_object=self.TestModel,
            method_name='get_absolute_url_using_reverse',
            current_url='/new_target',
        )
        self.URLChangeMethod.old_urls.add(self.OldUrl)

    def test_redirect(self):
        response = self.client.get('/initial')
        self.assertRedirects(
            response,
            '/new_target',
            status_code=301,
            target_status_code=404
        )

    @override_settings(APPEND_SLASH=True)
    def test_redirect_with_append_slash(self):
        self.OldUrl.url += '/'
        self.URLChangeMethod.current_url += '/'
        self.OldUrl.save()
        self.URLChangeMethod.save()

        response = self.client.get('/initial')
        self.assertRedirects(
            response,
            '/new_target/',
            status_code=301,
            target_status_code=404
        )

    @override_settings(APPEND_SLASH=True)
    def test_redirect_with_append_slash_and_query_string(self):
        self.OldUrl.url = '/initial/?foo'
        self.URLChangeMethod.current_url += '/'
        self.OldUrl.save()
        self.URLChangeMethod.save()

        response = self.client.get('/initial?foo')
        self.assertRedirects(
            response,
            '/new_target/',
            status_code=301,
            target_status_code=404
        )

    def test_response_gone(self):
        """When the redirect target is '', return a 410"""
        self.URLChangeMethod.current_url = ''
        self.URLChangeMethod.save()

        response = self.client.get('/initial')
        self.assertEqual(response.status_code, 410)

    @override_settings(
        INSTALLED_APPS=[app for app in settings.INSTALLED_APPS
                        if app != 'url_tracker'])
    def test_sites_not_installed(self):
        with self.assertRaises(ImproperlyConfigured):
            URLChangePermanentRedirectMiddleware()
