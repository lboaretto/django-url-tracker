from django.test import TestCase

from url_tracker.models import URLChangeRecord


class TestUrlRecord(TestCase):

    def test_returns_404_for_invalid_url(self):
        response = self.client.get('/work/an-invalid-project/')
        self.assertEquals(response.status_code, 404)

    def test_returns_301_for_a_changed_url(self):
        URLChangeRecord.objects.create(
            old_url='/the/old-url/',
            new_url='/the/new/url/',
        )

        response = self.client.get('/the/old-url/')
        self.assertEquals(response.status_code, 301)
        self.assertEquals(response['location'], 'http://testserver/the/new/url/')

    def test_returns_410_for_a_deleted_url(self):
        URLChangeRecord.objects.create(
            old_url='/the/old-url/',
            new_url='',
            deleted=True
        )

        response = self.client.get('/the/old-url/')
        self.assertEquals(response.status_code, 410)

    def test_returns_301_for_a_changed_url_containing_querystring(self):
        old_url = '/the/old-url/afile.php?q=test&another=45'
        URLChangeRecord.objects.create(
            old_url=old_url,
            new_url='/the/new/url/',
        )

        response = self.client.get(old_url)
        self.assertEquals(response.status_code, 301)
