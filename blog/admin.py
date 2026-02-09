from django.contrib import admin
from blog.models import (
    Post, Page, Category, Tag, Comment, Media, Menu, MenuItem, Redirect, PluginData,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("title", "file", "mime_type", "uploaded_at")
    search_fields = ("title", "alt_text")
    list_filter = ("mime_type",)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("author_name", "content", "status", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "author", "published_at")
    list_filter = ("status", "categories", "published_at")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories", "tags")
    date_hierarchy = "published_at"
    inlines = [CommentInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "content", "excerpt", "status", "author")}),
        ("Relations", {"fields": ("categories", "tags", "featured_image")}),
        ("Publication", {"fields": ("published_at",)}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "menu_order", "parent")
    list_filter = ("status",)
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "content", "status", "author", "parent", "menu_order")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author_name", "post", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("author_name", "content")
    actions = ["approve_comments", "mark_spam"]

    @admin.action(description="Approuver les commentaires sélectionnés")
    def approve_comments(self, request, queryset):
        queryset.update(status="approved")

    @admin.action(description="Marquer comme spam")
    def mark_spam(self, request, queryset):
        queryset.update(status="spam")


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = ("title", "url", "position", "parent", "content_type", "object_id")


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "location")
    inlines = [MenuItemInline]


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ("old_path", "new_path", "is_permanent")
    search_fields = ("old_path", "new_path")


@admin.register(PluginData)
class PluginDataAdmin(admin.ModelAdmin):
    list_display = ("plugin_name", "source_table", "related_post", "created_at")
    list_filter = ("plugin_name",)
    search_fields = ("plugin_name", "source_table")
