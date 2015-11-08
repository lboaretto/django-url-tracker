class URLTrackingMixin(object):
    url_tracking_methods = [
        'get_absolute_url',
    ]

    @classmethod
    def get_url_tracking_methods(cls):
        return cls.url_tracking_methods
