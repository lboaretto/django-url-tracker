import logging
import warnings

from django.db.models import signals

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
    in a ``pre_save`` state. The previous url is saved in the instance as
    *_old_url* so that it can be used after the instance was saved.

    If the instance has not been saved to the database (i.e. is new) the
    *_old_url* will be stored as ``None`` which will prevent further tracking
    after saving the instance.
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
        method = getattr(db_instance, method_name, None)
        if method:
            instance._old_urls[method_name] = method()


def track_changed_url(instance, **kwargs):
    """
    Track a URL change for *instance* after a new instance was saved. If
    the old URL is ``None`` (i.e. *instance* is new) or the new URL and
    the old one are equal (i.e. URL is unchanged), nothing will be changed
    in the database.

    For URL changes, the database will be checked for existing records that
    have a *new_url* entry equal to the old URL of *instance* and updates
    these records. Then, a new ``URLChangeRecord`` is created for the
    *instance*.
    """
    for method_name, old_url in getattr(instance._old_urls, {}).items():
        try:
            new_url = getattr(instance, method_name)()
        except AttributeError:
            continue

        # we don't want to store URL changes for unchanged URL
        if old_url == new_url:
            continue

        logger.debug(
            "tracking URL change for instance '%s' URL",
            instance.__class__.__name__
        )

        # check if the new URL is already in the table and
        # remove these entries
        for record in URLChangeRecord.objects.filter(old_url=new_url):
            record.delete()

        # updated existing records with the old URL being
        # the new URL in the record
        url_records = URLChangeRecord.objects.filter(new_url=old_url)
        for record in url_records:
            record.new_url = new_url
            record.deleted = False
            record.save()

        # create a new/updated record for this combination of old and
        # new URL. If the record already exists, it is assumed that the
        # current change is to be used and the existing new_url will be
        # detached from the old_url.
        try:
            logger.info(
                "a record for '%s' already exists and will be updated",
                instance._old_url,
            )
            record = URLChangeRecord.objects.get(old_url=instance._old_url)
            record.new_url = new_url
            record.deleted = False
            record.save()
        except URLChangeRecord.DoesNotExist:
            URLChangeRecord.objects.create(
                old_url=instance._old_url,
                new_url=new_url,
                deleted=False
            )


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
        # updated existing records with the old URL being the new_url
        # of this record. Changed the *deleted* flag to be ``False``
        url_records = URLChangeRecord.objects.filter(new_url=old_url)
        for record in url_records:
            record.new_url = ''
            record.deleted = True
            record.save()

        try:
            url_change = URLChangeRecord.objects.get(old_url=old_url)
            url_change.deleted = True
            url_change.save()
        except URLChangeRecord.DoesNotExist:
            URLChangeRecord.objects.create(
                old_url=old_url,
                deleted=True
            )


def track_url_changes_for_model(model, absolute_url_method='get_absolute_url'):
    """
    Keep track of URL changes of the specified *model*. This will connect the
    *model*'s ``pre_save``, ``post_save`` and ``post_delete`` signals to the
    tracking methods ``lookup_previous_url``, ``track_changed_url``
    and ``track_deleted_url`` respectively. URL changes will be logged in the
    ``URLChangeRecord`` table and are handled by the tracking middleware when
    a changed URL is called.
    """
    if not hasattr(model, 'get_url_tracking_methods'):
        warnings.warn(
            "the 'absolute_url_method' is deprecated, use the "
            "'UrlTrackingMixin' instead",
            PendingDeprecationWarning
        )
        model.url_tracking_methods = [absolute_url_method]
        model.get_url_tracking_methods = URLTrackingMixin.get_url_tracking_methods

    signals.pre_save.connect(lookup_previous_url, sender=model, weak=False)
    signals.post_save.connect(track_changed_url, sender=model, weak=False)
    signals.post_delete.connect(track_deleted_url, sender=model, weak=False)
