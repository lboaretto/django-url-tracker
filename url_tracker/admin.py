from django.contrib import admin

from url_tracker.models import URLChangeMethod, OldURL


class URLChangeMethodAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'method_name', 'current_url')
    list_filter = ('content_type', 'method_name')


class OldURLAdmin(admin.ModelAdmin):
    list_display = ('url',)


admin.site.register(URLChangeMethod, URLChangeMethodAdmin)
admin.site.register(OldURL, OldURLAdmin)
