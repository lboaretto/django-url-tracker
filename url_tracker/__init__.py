import logging
import warnings

from django.db.models import signals
from django.core.exceptions import ImproperlyConfigured

from .models import URLChangeRecord
from .mixins import URLTrackingMixin

logger = logging.getLogger(__file__)


class URLTrackingError(Exception):
    """
    Exception raised when an error occures during URL tracking.
    """
    pass


def lookup_previous_url(instance, **kwargs):
    """
    Look up the absolute URL of *instance* from the database while it is
    in a ``pre_save`` state. The previous urls are saved in the instance's
    *_old_urls* attribute as dictionary. The method name for the given URLs
    are used as the dictionary keys.

    If the instance has not been saved to the database (i.e. is new)
    the ``_old_urls`` dictionary is set to ``{}`` which will prevent a record
    to be created.
    """
    try:
        db_instance = instance.__class__.objects.get(pk=instance.pk)
        logger.debug("saving old URL for instance '%s' URL",
                     instance.__class__.__name__)
    except instance.__class__.DoesNotExist:
        logger.debug("new instance, no URL tracking required")
        instance._old_urls = {}
        return

    for method_name in instance.get_url_tracking_methods():
        try:
            method = getattr(db_instance, method_name)
        except AttributeError:
            raise ImproperlyConfigured(
                "model instance '%s' does not have a method '%s'" % (
                    db_instance.__class__.__name__,
                    method_name
                )
            )
        instance._old_urls[method_name] = method()


def _create_delete_record(url):
    """
    Create a delete record for the given *url*. This updates all records
    where *url* is the ``new_url`` (previous redirects). It also creates
    a new record with *url* being the ``old_url`` and no ``new_url`` and
    marked as deleted. This marks an endpoint in the chain of URL
    redirects.
    """
    # updated existing records with the old URL being the new_url
    # of this record. Changed the *deleted* flag to be ``False``
    url_records = URLChangeRecord.objects.filter(new_url=url).update(
        new_url='',
        deleted=True
    )

    record, created = URLChangeRecord.objects.get_or_create(old_url=url)
    record.deleted = True
    record.save()


def track_changed_url(instance, **kwargs):
    """
    Track a URL changes for *instance* after a new instance was saved. If
    no old URLs are available (i.e. *instance* is new) or if a new and old URL
    are the same (i.e. URL is unchanged), nothing will be changed in the
    database for this URL.

    For URLs that have changed, the database will be checked for existing
    records that have a *new_url* entry equal to the old URL of *instance* and
    updates these records. Then, a new ``URLChangeRecord`` is created for this
    URL.
    """
    for method_name, old_url in getattr(instance, '_old_urls', {}).items():
        try:
            new_url = getattr(instance, method_name)()
        except AttributeError:
            continue

        # if the new URL is None we assume that it has been deleted and
        # create a delete record for the old URL.
        if new_url is None:
            _create_delete_record(old_url)
            continue

        # we don't want to store URL changes for unchanged URL
        if old_url is None or old_url == new_url:
            continue

        logger.debug(
            "tracking URL change for instance '%s' URL",
            instance.__class__.__name__
        )

        # check if the new URL is already in the table and
        # remove these entries
        URLChangeRecord.objects.filter(old_url=new_url).delete()

        # updated existing records with the old URL being
        # the new URL in the record
        url_records = URLChangeRecord.objects.filter(new_url=old_url).update(
            new_url=new_url,
            deleted=False
        )

        # create a new/updated record for this combination of old and
        # new URL. If the record already exists, it is assumed that the
        # current change is to be used and the existing new_url will be
        # detached from the old_url.

        record, created = URLChangeRecord.objects.get_or_create(old_url=old_url)
        record.new_url = new_url
        record.deleted = False
        record.save()

def track_deleted_url(instance, **kwargs):
    """
    Track the URL of a deleted *instance*. It updates all existing
    records with ``new_url`` being set to the *instance*'s old URL and
    marks this record as deleted URL.

    A new ``URLChangeRecord`` is created for the old URL of *instance*
    that is marked as deleted.
    """
    logger.debug("tracking deleted instance '%s' URL",
                 instance.__class__.__name__)
    for old_url in getattr(instance, '_old_urls', {}).values():
        _create_delete_record(old_url)


def track_url_changes_for_model(model, absolute_url_method='get_absolute_url'):
    """
    Register the *model* for URL tracking. It requires the *model* to provide
    an attribute ``url_tracking_methods`` and/or a ``get_url_tracking_methods``
    method to return a list of methods to retrieve trackable URLs.
    The default setup provides ``url_tracking_methods = ['get_absolute_url']``.

    The ``pre_save``, ``post_save`` and ``post_delete`` methods are connected
    to different tracking methods for *model* and create/update
    ``URLChangeRecord``s as required.
    """
    if not hasattr(model, 'get_url_tracking_methods'):
        warnings.warn(
            "the 'absolute_url_method' is deprecated, use the "
            "'UrlTrackingMixin' instead",
            PendingDeprecationWarning
        )
        model.url_tracking_methods = [absolute_url_method]
        model.get_url_tracking_methods = URLTrackingMixin.get_url_tracking_methods

    # make sure that URL method names are specified for the given model
    if not getattr(model, 'url_tracking_methods', None):
        raise URLTrackingError("no URLs specified for model '%s'" % model)

    signals.pre_save.connect(lookup_previous_url, sender=model, weak=False)
    signals.post_save.connect(track_changed_url, sender=model, weak=False)
    signals.post_delete.connect(track_deleted_url, sender=model, weak=False)
