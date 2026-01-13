from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from djangoldp.models import Model
from .models import Notification, NotificationSetting, Subscription


@admin.register(Notification)
class NotificationAdmin(DjangoLDPAdmin):
    list_display = ('urlid', 'user', 'author', 'type', 'object', 'unread')
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    search_fields = ['urlid', 'user__urlid', 'author', 'object', 'type', 'summary']
    ordering = ['-urlid']

    def get_queryset(self, request):
        # Hide distant notification
        queryset = super(NotificationAdmin, self).get_queryset(request)
        internal_ids = [x.pk for x in queryset if not Model.is_external(x)]
        return queryset.filter(pk__in=internal_ids)


@admin.register(Subscription)
class SubscriptionAdmin(DjangoLDPAdmin):
    list_display = ('urlid', 'object', 'inbox', 'field')
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    search_fields = ['urlid', 'object', 'inbox', 'field']
    ordering = ['urlid']


@admin.register(NotificationSetting)
class NotificationSettingAdmin(DjangoLDPAdmin):
    list_display = ('urlid', 'user', 'receiveMail')
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    search_fields = ['urlid', 'user', 'receiveMail']
    ordering = ['urlid']


