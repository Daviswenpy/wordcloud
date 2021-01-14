import logging
import itertools
import collections
import redis
from datetime import timedelta

from django.contrib import admin
from django.utils import timezone
from django.core.cache import cache
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.http import urlquote
from django.utils.html import format_html
from django.utils.translation import ngettext

from . import models

# main add view
IS_POPUP_VAR = '_popup'
TO_FIELD_VAR = '_to_field'

from django.contrib.admin import helpers
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.forms.formsets import all_valid
from .models import Queryset

logger = logging.getLogger(__name__)


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.izip_longest(*args, fillvalue=fillvalue)


class RedisAdmin(admin.ModelAdmin):
    """use hash type hset aPxjb8jhnP
    TODO: 1 add deviceID list in register api
          2 add user list ["itm-admin", "postmantest"] in anywhere, no sk-admin
          3 add XRS list in somewhere
          3 add userId list in userservice?
          4 add modelID list in zodiac
          5 add nodeID list in zodiac
          6 add paramID in zodiac
          7 add bool list in somewhere
          8 add key/value type filter with some list
          9 add prefix userId_`key` in cache db1, exact XRS(tuple)
    """
    list_per_page = 19
    save_as_continue = False
    show_full_result_count = False
    fields = ('key', '_key_type', '_value_type', 'value', 'timeout', 'ttl', 'expires_at')
    list_display = ['key', 'key_type', 'value', 'value_type', 'ttl', 'expires_at', 'timeout', 'action_button']
    search_fields = 'key__contains',

    # Keep everything read-only for now, saving isn't implemented yet
    # readonly_fields = [f.name for f in models.RedisValue._meta.get_fields()]
    add_readonly_fields = ['ttl', 'expires_at', 'type']
    readonly_fields = ['key', 'key_type', 'ttl', 'expires_at', 'type']

    def get_queryset(self, request):
        return Queryset(self.model, slice_limit=self.list_per_page + 1)

    actions = ['delete_selected', 'touch_selected']

    def delete_selected(self, request, obj):
        size = 0
        for o in obj:
            size += 1
            o.delete()
        self.message_user(request, ngettext(
            '%d cache was deleted successfully.',
            '%d caches was deleted successfully.',
            size
        ) % size, messages.SUCCESS)

    def touch_selected(self, request, obj):
        success = fail = 0
        for o in obj:
            if o.touch():
                success += 1
            else:
                fail += 1
        self.message_user(request, ngettext(
            '%d cache was touched successfully, %d cache was touched unsuccessfully',
            '%d caches was touched successfully, %d caches was touched unsuccessfully.',
            (success, fail)
        ) % (success, fail), messages.SUCCESS)

    def action_button(self, obj):
        touch_button = """
            <a name="touch" class="changelink" href="/admin/cache_manager/cache_server/%s/touch">Touch</a>&nbsp&nbsp
        """ % (obj.key)

        delete_button = """
            <a name="delete" class="deletelink" href="/admin/cache_manager/cache_server/%s/delete/">Delete</a>
        """ % (obj.key)
        return format_html(touch_button + delete_button)

    action_button.short_description = "action buttons"

    def get_urls(self):
        from django.conf.urls import url
        """get_urls."""

        urls = super(RedisAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        urlpatterns = [
            url(r'^(.+)/touch/$', self.admin_site.admin_view(self.touch_view), name='%s_%s_touch' % info),
        ]
        return urlpatterns + urls

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        return super(RedisAdmin, self).change_view(request, object_id, extra_context=extra_context)

    def get_readonly_fields(self, request, obj=None):
        """
        Hook for specifying custom readonly fields.
        """
        if obj:
            print("change fields")
            return self.readonly_fields
        else:
            print("add fields")
            return self.add_readonly_fields

    # def changelist_view(self, request, extra_context=None):
    #     return super(RedisAdmin, self).changelist_view(request, extra_context=extra_context)

    def touch_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        msg_dict = {
            'name': opts.verbose_name,
            'obj': format_html('<a href="{}">{}</a>', urlquote(request.path), object_id),
        }
        if cache.ttl(object_id) >= 3600:
            msg = format_html(
                'The {name} "{obj}" was touched unsuccessfully. (The default timeout is too small.)',
                **msg_dict
            )
            self.message_user(request, msg, messages.WARNING)
        else:
            cache.touch(object_id, 3600)
            msg = format_html(
                'The {name} "{obj}" was touched successfully.',
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
        return redirect('/admin/cache_manager/cache_server/')

    class Media:
        css = {'all': ('cache_manager/css/hide_button.css', )}
        js = ("cache_manager/js/jquery.js", "cache_manager/js/autorefresh.js")


for server_model in models.server_models.values():
    admin.site.register(server_model, RedisAdmin)
