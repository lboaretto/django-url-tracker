import url_tracker

from django.core.urlresolvers import reverse


class Project(url_tracker.URLTrackingMixin, models.Model):
    slug = models.SlugField(max_length=20)

    def get_absolute_url_using_reverse(self):
        return reverse('project', kwargs={'slug', self.slug})

    @models.permalink
    def get_absolute_url_using_permalink(self):
        return ('project', (), {'slug', self.slug})

    def return_slug_or_none(self):
        return slug if slug


url_tracker.track_url_changes_for_model(Project)
