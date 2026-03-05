from django.contrib import admin
from .models import UserProfile, UploadRecord, AnonymousUploadRecord


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'subscription_status', 'stripe_customer_id', 'created_at']
    list_filter  = ['plan', 'subscription_status']
    search_fields = ['user__email', 'stripe_customer_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UploadRecord)
class UploadRecordAdmin(admin.ModelAdmin):
    list_display  = ['user', 'filename', 'file_size', 'created_at']
    list_filter   = ['created_at']
    search_fields = ['user__email', 'filename']


@admin.register(AnonymousUploadRecord)
class AnonymousUploadRecordAdmin(admin.ModelAdmin):
    list_display  = ['ip_address', 'created_at']
    list_filter   = ['created_at']
