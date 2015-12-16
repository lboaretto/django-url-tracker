import logging
import warnings

from django.db.models import signals
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__file__)


def lookup_previous_url(instance, **kwargs):
    """
    Gets the previous urls for the model. It will save them too a
    URLChangeMethod object, as OldURLs. If the url method won't resolve
    then the url is treated as if it doesn't exist. Also it won't create
    a URLChangeMethod if the old_url doesn't exist or is equal to the current
    url of that model

    When this method is called `instance` represents the presaved version of the instance.
    So to get the old URL, we get the object from the database, to get its current state
    """
    for method_name in instance.get_url_tracking_methods():

        # If the instance is new then don't create a url change
        try:
            instance = instance.__class__.objects.get(pk=instance.pk)
        except instance.__class__.DoesNotExist:
            continue

        old_url = getattr(instance, method_name)()
        if not old_url:
            return
        add_old_url(instance, method_name, old_url)


def add_old_url(instance, method_name, old_url):
    '''
    Saves an old_url for a method and an instance.

    It will create a OldUrl object for that url and add it to the url_method for that instance.
    '''
    from url_tracker.models import URLChangeMethod, OldURL
    from django.contrib.contenttypes.models import ContentType

    content_type = ContentType.objects.get_for_model(instance.__class__)
    url_method, created = URLChangeMethod.objects.get_or_create(
        content_type=content_type,
        object_id=instance.pk,
        method_name=method_name
    )
    old_url, __ = OldURL.objects.get_or_create(url=old_url)
    url_method.old_urls.add(old_url)
    url_method.save()


def track_changed_url(instance, **kwargs):
    """
    Saves the current_url for an instance.

    If that instance has not URLChangeMethod, then it will not create one.
    """
    from url_tracker.models import URLChangeMethod
    from django.contrib.contenttypes.models import ContentType

    for method_name in instance.get_url_tracking_methods():
        content_type = ContentType.objects.get_for_model(instance.__class__)
        try:
            url_method = URLChangeMethod.objects.get(
                content_type=content_type,
                object_id=instance.pk,
                method_name=method_name
            )
        except URLChangeMethod.DoesNotExist:
            continue
        current_url = getattr(instance, method_name)()

        logger.debug(
            "tracking URL change for instance '%s' URL",
            instance.__class__.__name__
        )

        url_method.current_url = current_url
        url_method.old_urls.filter(url=current_url).delete()
        if not url_method.old_urls.exists():
            url_method.delete()
            continue
        url_method.save()


def track_url_changes_for_model(model, absolute_url_method='get_absolute_url'):
    """
    Register the *model* for URL tracking. It requires the *model* to provide
    an attribute ``url_tracking_methods`` and/or a ``get_url_tracking_methods``
    method to return a list of methods to retrieve trackable URLs.
    The default setup provides ``url_tracking_methods = ['get_absolute_url']``.

    The ``pre_save`` and ``post_save`` methods are connected
    to different tracking methods for *model* and create/update
    ``URLChangeRecord``s as required.
    """
    if not hasattr(model, 'get_url_tracking_methods'):
        from url_tracker.mixins import URLTrackingMixin

        warnings.warn(
            "the 'absolute_url_method' is deprecated, use the "
            "'UrlTrackingMixin' instead",
            PendingDeprecationWarning
        )
        model.url_tracking_methods = [absolute_url_method]
        model.get_url_tracking_methods = URLTrackingMixin.get_url_tracking_methods

    # make sure that URL method names are specified for the given model
    if not getattr(model, 'url_tracking_methods', None):
        raise ImproperlyConfigured("no URLs specified for model '%s'" % model)

    for method_name in model.get_url_tracking_methods():
        if not hasattr(model, method_name):
            raise ImproperlyConfigured(
                "model instance '%s' does not have a method '%s'" % (
                    model.__name__,
                    method_name
                )
            )

    signals.pre_save.connect(lookup_previous_url, sender=model, weak=False)
    signals.post_save.connect(track_changed_url, sender=model, weak=False)
