from django.contrib import admin
from django.utils.html import format_html
from blog.models import (
    Post, Page, Category, Tag, Comment, Media, Menu, MenuItem, Redirect, PluginData,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "post_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def post_count(self, obj):
        count = obj.posts.count()
        return format_html('<span style="font-weight:600">{}</span>', count)
    post_count.short_description = "Articles"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "post_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def post_count(self, obj):
        count = obj.posts.count()
        return format_html('<span style="font-weight:600">{}</span>', count)
    post_count.short_description = "Articles"


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("thumbnail_preview", "title", "mime_type", "uploaded_at")
    search_fields = ("title", "alt_text")
    list_filter = ("mime_type",)
    list_display_links = ("thumbnail_preview", "title")

    def thumbnail_preview(self, obj):
        if obj.file and obj.mime_type and obj.mime_type.startswith("image/"):
            return format_html(
                '<img src="{}" style="width:48px;height:48px;object-fit:cover;'
                'border-radius:6px;border:1px solid #e9e5e0" />',
                obj.file.url,
            )
        return format_html(
            '<span style="display:inline-flex;width:48px;height:48px;border-radius:6px;'
            'background:#f5f3f0;align-items:center;justify-content:center;color:#636e72;'
            'font-size:0.7rem;text-align:center">{}</span>',
            (obj.mime_type or "?")[:10],
        )
    thumbnail_preview.short_description = ""


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("author_name", "content", "status", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "status_badge", "author", "category_list", "published_at")
    list_filter = ("status", "categories", "published_at")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories", "tags")
    date_hierarchy = "published_at"
    inlines = [CommentInline]
    list_per_page = 25
    fieldsets = (
        (None, {"fields": ("title", "slug", "content", "excerpt", "status", "author")}),
        ("Relations", {"fields": ("categories", "tags", "featured_image")}),
        ("Publication", {"fields": ("published_at",)}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )

    def status_badge(self, obj):
        colors = {
            "published": ("#065f46", "#ecfdf5", "#a7f3d0"),
            "draft": ("#92400e", "#fffbeb", "#fde68a"),
            "private": ("#636e72", "#f5f3f0", "#e9e5e0"),
        }
        labels = {
            "published": "Publie",
            "draft": "Brouillon",
            "private": "Prive",
        }
        color, bg, border = colors.get(obj.status, ("#636e72", "#f5f3f0", "#e9e5e0"))
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="padding:3px 10px;border-radius:50px;font-size:0.78rem;'
            'font-weight:600;color:{};background:{};border:1px solid {}">{}</span>',
            color, bg, border, label,
        )
    status_badge.short_description = "Statut"
    status_badge.admin_order_field = "status"

    def category_list(self, obj):
        cats = obj.categories.all()[:3]
        if not cats:
            return "-"
        return format_html(
            " ".join(
                '<span style="padding:2px 8px;border-radius:50px;font-size:0.75rem;'
                'background:#fdf0ec;color:#e8734a;font-weight:500">{}</span>'.format(c.name)
                for c in cats
            )
        )
    category_list.short_description = "Categories"


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "status_badge", "menu_order", "parent")
    list_filter = ("status",)
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "content", "status", "author", "parent", "menu_order")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )

    def status_badge(self, obj):
        colors = {
            "published": ("#065f46", "#ecfdf5"),
            "draft": ("#92400e", "#fffbeb"),
        }
        labels = {"published": "Publie", "draft": "Brouillon"}
        color, bg = colors.get(obj.status, ("#636e72", "#f5f3f0"))
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="padding:3px 10px;border-radius:50px;font-size:0.78rem;'
            'font-weight:600;color:{};background:{}">{}</span>',
            color, bg, label,
        )
    status_badge.short_description = "Statut"
    status_badge.admin_order_field = "status"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author_name", "post", "status_badge", "short_content", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("author_name", "content")
    list_per_page = 30
    actions = ["approve_comments", "mark_spam"]

    def status_badge(self, obj):
        colors = {
            "approved": ("#065f46", "#ecfdf5"),
            "pending": ("#92400e", "#fffbeb"),
            "spam": ("#991b1b", "#fef2f2"),
        }
        color, bg = colors.get(obj.status, ("#636e72", "#f5f3f0"))
        return format_html(
            '<span style="padding:3px 10px;border-radius:50px;font-size:0.78rem;'
            'font-weight:600;color:{};background:{}">{}</span>',
            color, bg, obj.status.capitalize(),
        )
    status_badge.short_description = "Statut"
    status_badge.admin_order_field = "status"

    def short_content(self, obj):
        text = obj.content[:80]
        if len(obj.content) > 80:
            text += "..."
        return text
    short_content.short_description = "Contenu"

    @admin.action(description="Approuver les commentaires selectionnes")
    def approve_comments(self, request, queryset):
        count = queryset.update(status="approved")
        self.message_user(request, f"{count} commentaire(s) approuve(s).")

    @admin.action(description="Marquer comme spam")
    def mark_spam(self, request, queryset):
        count = queryset.update(status="spam")
        self.message_user(request, f"{count} commentaire(s) marque(s) comme spam.")


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = (
        "position", "title", "linked_content_display",
        "linked_post", "linked_page", "linked_category",
        "url", "parent", "target",
    )
    readonly_fields = ("linked_content_display",)
    autocomplete_fields = ("linked_post", "linked_page", "linked_category", "parent")
    ordering = ("position",)

    def linked_content_display(self, obj):
        if not obj.pk:
            return "-"
        if obj.linked_post:
            return format_html(
                '<span style="padding:2px 8px;border-radius:50px;font-size:0.75rem;'
                'background:#fdf0ec;color:#e8734a;font-weight:500">Article</span> {}',
                obj.linked_post.title[:40],
            )
        if obj.linked_page:
            return format_html(
                '<span style="padding:2px 8px;border-radius:50px;font-size:0.75rem;'
                'background:#ecfdf5;color:#065f46;font-weight:500">Page</span> {}',
                obj.linked_page.title[:40],
            )
        if obj.linked_category:
            return format_html(
                '<span style="padding:2px 8px;border-radius:50px;font-size:0.75rem;'
                'background:#eff6ff;color:#1e40af;font-weight:500">Categorie</span> {}',
                obj.linked_category.name[:40],
            )
        if obj.content_type and obj.object_id:
            return format_html(
                '<span style="padding:2px 8px;border-radius:50px;font-size:0.75rem;'
                'background:#fef2f2;color:#991b1b;font-weight:500">Non mappe</span> '
                '{}:{}',
                obj.content_type, obj.object_id,
            )
        if obj.url:
            return format_html(
                '<span style="padding:2px 8px;border-radius:50px;font-size:0.75rem;'
                'background:#f5f3f0;color:#636e72;font-weight:500">URL</span> {}',
                obj.url[:50],
            )
        return "-"
    linked_content_display.short_description = "Contenu lie"

    class Media:
        css = {"all": ("css/admin_menu_inline.css",)}


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "location", "item_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    inlines = [MenuItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Elements"


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("title", "menu", "position", "linked_content_display", "parent")
    list_filter = ("menu",)
    search_fields = ("title",)
    list_editable = ("position",)
    autocomplete_fields = ("linked_post", "linked_page", "linked_category", "parent", "menu")
    list_per_page = 50
    fieldsets = (
        (None, {"fields": ("menu", "title", "position", "parent")}),
        ("Lien interne", {
            "fields": ("linked_post", "linked_page", "linked_category"),
            "description": "Selectionnez un article, une page ou une categorie. "
                          "Laissez vide pour utiliser l'URL personnalisee.",
        }),
        ("Lien externe", {
            "fields": ("url", "target", "css_classes"),
            "classes": ("collapse",),
        }),
    )

    def linked_content_display(self, obj):
        if obj.linked_post:
            return format_html(
                '<span style="padding:2px 8px;border-radius:50px;font-size:0.75rem;'
                'background:#fdf0ec;color:#e8734a;font-weight:500">Article</span> {}',
                obj.linked_post.title[:40],
            )
        if obj.linked_page:
            return format_html(
                '<span style="padding:2px 8px;border-radius:50px;font-size:0.75rem;'
                'background:#ecfdf5;color:#065f46;font-weight:500">Page</span> {}',
                obj.linked_page.title[:40],
            )
        if obj.linked_category:
            return format_html(
                '<span style="padding:2px 8px;border-radius:50px;font-size:0.75rem;'
                'background:#eff6ff;color:#1e40af;font-weight:500">Categorie</span> {}',
                obj.linked_category.name[:40],
            )
        if obj.content_type and obj.object_id:
            return format_html(
                '<span style="padding:2px 8px;border-radius:50px;font-size:0.75rem;'
                'background:#fef2f2;color:#991b1b;font-weight:500">Non mappe</span> '
                '{}:{}',
                obj.content_type, obj.object_id,
            )
        if obj.url:
            return format_html(
                '<span style="padding:2px 8px;border-radius:50px;font-size:0.75rem;'
                'background:#f5f3f0;color:#636e72;font-weight:500">URL</span> {}',
                obj.url[:50],
            )
        return "-"
    linked_content_display.short_description = "Contenu lie"


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ("old_path", "arrow_icon", "new_path", "redirect_type")
    search_fields = ("old_path", "new_path")
    list_per_page = 50

    def arrow_icon(self, obj):
        return format_html(
            '<span style="color:#e8734a;font-weight:bold;font-size:1.1rem">&rarr;</span>'
        )
    arrow_icon.short_description = ""

    def redirect_type(self, obj):
        if obj.is_permanent:
            return format_html(
                '<span style="padding:2px 8px;border-radius:50px;font-size:0.75rem;'
                'background:#ecfdf5;color:#065f46;font-weight:600">301</span>'
            )
        return format_html(
            '<span style="padding:2px 8px;border-radius:50px;font-size:0.75rem;'
            'background:#fffbeb;color:#92400e;font-weight:600">302</span>'
        )
    redirect_type.short_description = "Type"
    redirect_type.admin_order_field = "is_permanent"


@admin.register(PluginData)
class PluginDataAdmin(admin.ModelAdmin):
    list_display = ("plugin_name", "source_table", "related_post", "created_at")
    list_filter = ("plugin_name",)
    search_fields = ("plugin_name", "source_table")
