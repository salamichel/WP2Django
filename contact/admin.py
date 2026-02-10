from django.contrib import admin
from django.utils.html import format_html
from contact.models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "read_badge")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "created_at")
    list_per_page = 25
    actions = ["mark_read", "mark_unread"]

    def read_badge(self, obj):
        if obj.is_read:
            return format_html(
                '<span style="padding:3px 10px;border-radius:50px;font-size:0.78rem;'
                'font-weight:600;color:#065f46;background:#ecfdf5">Lu</span>'
            )
        return format_html(
            '<span style="padding:3px 10px;border-radius:50px;font-size:0.78rem;'
            'font-weight:600;color:#e8734a;background:#fdf0ec">Nouveau</span>'
        )
    read_badge.short_description = "Statut"
    read_badge.admin_order_field = "is_read"

    @admin.action(description="Marquer comme lu")
    def mark_read(self, request, queryset):
        count = queryset.update(is_read=True)
        self.message_user(request, f"{count} message(s) marque(s) comme lu(s).")

    @admin.action(description="Marquer comme non lu")
    def mark_unread(self, request, queryset):
        count = queryset.update(is_read=False)
        self.message_user(request, f"{count} message(s) marque(s) comme non lu(s).")
