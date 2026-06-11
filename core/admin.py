from django.contrib import admin
from .models import EventPhoto, EventSetting


@admin.register(EventSetting)
class EventSettingAdmin(admin.ModelAdmin):
    list_display = ('event_name',)


@admin.register(EventPhoto)
class EventPhotoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'guest_name',
        'table_number',
        'uploaded_at',
        'is_approved',
    )
    list_filter = ('is_approved', 'uploaded_at')
    search_fields = ('guest_name', 'table_number')
    list_editable = ('is_approved',)
    ordering = ('-uploaded_at',)