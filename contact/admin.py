from django.contrib import admin
from contact.models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "created_at")
    actions = ["mark_read"]

    @admin.action(description="Marquer comme lu")
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
