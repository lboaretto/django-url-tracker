class URLTrackingMixin(object):
    url_tracking_methods = [
        'get_absolute_url',
    ]
    _old_urls = {}

    def get_url_tracking_methods(self):
        return self.url_tracking_methods
