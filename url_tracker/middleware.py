from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django import http

from url_tracker.models import OldURL


class URLChangePermanentRedirectMiddleware(object):
    def __init__(self):
        if 'url_tracker' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured(
                "You cannot use URLChangePermanentRedirectMiddleware when "
                "url_tracker is not installed."
            )

    def process_response(self, request, response):
        if response.status_code != 404:
            return response  # No need to check for a redirect for non-404 responses.

        full_path = request.get_full_path()

        old_url = None
        try:
            old_url = OldURL.objects.get(url__exact=full_path)
        except OldURL.DoesNotExist:
            pass
        if settings.APPEND_SLASH and not request.path.endswith('/'):
            # Try appending a trailing slash.
            path_len = len(request.path)
            full_path = full_path[:path_len] + '/' + full_path[path_len:]
            try:
                old_url = OldURL.objects.get(url__exact=full_path)
            except OldURL.DoesNotExist:
                pass
        if old_url:
            new_url = old_url.get_new_url()
            if not new_url:
                return http.HttpResponseGone()
            return http.HttpResponsePermanentRedirect(new_url)

        # No redirect was found. Return the response.
        return response
