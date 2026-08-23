import mimetypes

from django import forms
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html
from blog.models import (
    Post, Animal, Article, Page, Category, Tag, Comment, Media, Menu, MenuItem, Redirect, PluginData,
    PostGalleryImage,
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


class GalleryImageInline(admin.TabularInline):
    model = PostGalleryImage
    extra = 1
    fields = ("media", "position")
    autocomplete_fields = ("media",)
    template = "admin/blog/post/gallery_inline.html"

    class Media:
        css = {"all": ("css/admin_gallery_dnd.css",)}
        js = ("js/admin_gallery_dnd.js",)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("author_name", "content", "status", "created_at")
    readonly_fields = ("created_at",)


class BasePostAdmin(admin.ModelAdmin):
    """Base Admin class providing media upload and visual badges."""
    inlines = [GalleryImageInline, CommentInline]

    def get_urls(self):
        model_name = self.model._meta.model_name
        custom = [
            path("upload-media/", self.admin_site.admin_view(self.upload_media), name=f"blog_{model_name}_upload_media"),
        ]
        return custom + super().get_urls()

    def upload_media(self, request):
        if request.method != "POST":
            return JsonResponse({"error": "POST required"}, status=405)
        if not request.user.has_perm("blog.add_media"):
            return JsonResponse({"error": "Permission denied"}, status=403)

        uploaded = request.FILES.getlist("files")
        if not uploaded:
            return JsonResponse({"error": "No files"}, status=400)

        results = []
        for f in uploaded:
            mime = f.content_type or mimetypes.guess_type(f.name)[0] or ""
            title = f.name.rsplit(".", 1)[0] if "." in f.name else f.name
            obj = Media.objects.create(title=title, file=f, mime_type=mime)
            is_image = mime.startswith("image/")
            results.append({
                "id": obj.pk,
                "title": obj.title,
                "mime_type": mime,
                "url": obj.file.url if is_image else "",
                "is_image": is_image,
            })
        return JsonResponse({"uploaded": results})

    def status_badge(self, obj):
        colors = {
            "published": ("#065f46", "#ecfdf5", "#a7f3d0"),
            "draft": ("#92400e", "#fffbeb", "#fde68a"),
            "private": ("#636e72", "#f5f3f0", "#e9e5e0"),
        }
        labels = {
            "published": "Publié",
            "draft": "Brouillon",
            "private": "Privé",
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

    def thumbnail_preview(self, obj):
        img_url = None
        if obj.featured_image and obj.featured_image.file:
            img_url = obj.featured_image.file.url
        else:
            first_gallery = obj.gallery_images.select_related("media").first()
            if first_gallery and first_gallery.media and first_gallery.media.file:
                img_url = first_gallery.media.file.url

        if img_url:
            return format_html(
                '<img src="{}" style="width:48px;height:48px;object-fit:cover;'
                'border-radius:8px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06)" />',
                img_url,
            )
        return format_html(
            '<div style="width:48px;height:48px;border-radius:8px;background:#f1f5f9;'
            'display:flex;align-items:center;justify-content:center;color:#94a3b8;font-size:1.3rem">🐾</div>'
        )
    thumbnail_preview.short_description = "Photo"


class AnimalAdminForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = "__all__"
        widgets = {
            "animal_name": forms.TextInput(attrs={
                "placeholder": "Ex: Milou, Luna, Filou...",
                "style": "font-size: 1.1rem; font-weight: 600; min-width: 260px;",
            }),
            "breed": forms.TextInput(attrs={"placeholder": "Ex: Berger Australien, Européen, Lapin nain..."}),
            "identification": forms.TextInput(attrs={"placeholder": "N° de puce (15 chiffres) ou tatouage..."}),
            "foster_family": forms.TextInput(attrs={"placeholder": "Nom, prénom ou ville de la FA..."}),
            "weight_kg": forms.NumberInput(attrs={"placeholder": "Ex: 14.5", "step": "0.1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["animal_name"].required = True
        self.fields["species"].required = True
        if "title" in self.fields:
            self.fields["title"].required = False
            self.fields["title"].help_text = "Laissé vide, le titre sera automatiquement généré depuis le nom et la race."
        if "slug" in self.fields:
            self.fields["slug"].required = False
            self.fields["slug"].help_text = "Laissé vide, le lien URL sera automatiquement généré."
        if not self.instance.pk:
            self.fields["species"].initial = "chien"
            self.fields["adoption_status"].initial = "adoptable"
            self.fields["status"].initial = "published"
            self.fields["housing_requirement"].initial = "indifferent"


@admin.register(Animal)
class AnimalAdmin(BasePostAdmin):
    form = AnimalAdminForm
    list_display = (
        "thumbnail_preview",
        "animal_name_display",
        "species_badge",
        "age_display_col",
        "adoption_badge",
        "compatibilities_badge",
        "status_badge",
        "published_at",
    )
    list_filter = (
        "species",
        "adoption_status",
        "is_emergency",
        "sex",
        "ok_dogs",
        "ok_cats",
        "ok_children",
        "is_vaccinated",
        "is_sterilized",
        "housing_requirement",
        "status",
        "published_at",
    )
    search_fields = ("animal_name", "breed", "identification", "foster_family", "title", "content")
    autocomplete_fields = ("featured_image",)
    filter_horizontal = ("categories", "tags")
    date_hierarchy = "published_at"
    list_per_page = 25
    actions = [
        "mark_as_adoptable",
        "mark_as_reserved",
        "mark_as_adopted",
        "mark_as_emergency",
        "remove_emergency",
    ]

    fieldsets = (
        ("🐾 1. Identité de l'animal", {
            "fields": (
                ("animal_name", "species"),
                ("breed", "sex"),
                ("birth_date", "weight_kg"),
            ),
        }),
        ("🏡 2. Ententes & Cadre de vie", {
            "fields": (
                ("ok_dogs", "ok_cats", "ok_children"),
                ("housing_requirement",),
            ),
        }),
        ("🩺 3. Santé & Suivi Vétérinaire", {
            "fields": (
                ("identification", "foster_family"),
                ("is_vaccinated", "is_sterilized"),
            ),
        }),
        ("❤️ 4. Statut d'adoption", {
            "fields": (
                ("adoption_status", "is_emergency"),
                ("adoption_date",),
            ),
        }),
        ("📷 5. Photos & Histoire", {
            "fields": (
                ("featured_image",),
                ("content",),
            ),
        }),
        ("⚙️ Options avancées (gérées automatiquement)", {
            "classes": ("collapse",),
            "fields": (
                ("title", "slug"),
                ("status", "author", "published_at"),
                ("categories", "tags"),
            ),
        }),
    )

    def animal_name_display(self, obj):
        name = obj.animal_name or obj.title or "Sans nom"
        subtitle_parts = []
        if obj.breed:
            subtitle_parts.append(obj.breed)
        if obj.sex and obj.get_sex_display():
            subtitle_parts.append(obj.get_sex_display())
        sub_text = " • ".join(subtitle_parts)
        return format_html(
            '<div style="font-weight:700;font-size:0.95rem;color:#0f172a">{}</div>'
            '<div style="font-size:0.78rem;color:#64748b;margin-top:2px">{}</div>',
            name, sub_text or "-"
        )
    animal_name_display.short_description = "Animal"
    animal_name_display.admin_order_field = "animal_name"

    def species_badge(self, obj):
        if not obj.species:
            return "-"
        colors = {"chien": "#e8734a", "chat": "#5b8c5a", "rongeur": "#f39c12", "autre": "#7f8c8d"}
        color = colors.get(obj.species, "#7f8c8d")
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 9px;border-radius:12px;font-size:0.75rem;font-weight:600">{}</span>',
            color, obj.get_species_display()
        )
    species_badge.short_description = "Espèce"
    species_badge.admin_order_field = "species"

    def age_display_col(self, obj):
        if not obj.birth_date:
            return format_html('<span style="color:#94a3b8">-</span>')
        return format_html(
            '<span style="font-weight:600;color:#334155;font-size:0.82rem">{}</span>',
            obj.age_display
        )
    age_display_col.short_description = "Âge"
    age_display_col.admin_order_field = "birth_date"

    def adoption_badge(self, obj):
        if not obj.species and not obj.animal_name:
            return "-"
        colors = {
            "adoptable": "#27ae60",
            "reserve": "#e67e22",
            "recherche_fa": "#e74c3c",
            "adopte": "#2b9348",
        }
        color = colors.get(obj.adoption_status, "#7f8c8d")
        label = obj.get_adoption_status_display()
        if obj.adoption_status == "adopte" and obj.adoption_date:
            label += f" ({obj.adoption_date.strftime('%d/%m/%Y')})"
        elif obj.is_emergency:
            label += " 🚨"
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 9px;border-radius:12px;font-size:0.75rem;font-weight:600">{}</span>',
            color, label
        )
    adoption_badge.short_description = "Adoption"
    adoption_badge.admin_order_field = "adoption_status"

    def compatibilities_badge(self, obj):
        items = [
            ("🐶", obj.ok_dogs, "Chiens"),
            ("🐱", obj.ok_cats, "Chats"),
            ("👶", obj.ok_children, "Enfants"),
        ]
        badges = []
        for icon, val, label in items:
            if val == "oui":
                bg, fg, sign = "#ecfdf5", "#065f46", "✓"
            elif val == "non":
                bg, fg, sign = "#fef2f2", "#991b1b", "✗"
            else:
                bg, fg, sign = "#f8fafc", "#94a3b8", "?"
            val_text = val or "Inconnu"
            badges.append(
                f'<span title="{label} : {val_text}" style="display:inline-flex;align-items:center;gap:2px;'
                f'background:{bg};color:{fg};padding:2px 6px;border-radius:6px;font-size:0.75rem;font-weight:600;'
                f'border:1px solid rgba(0,0,0,0.06)">{icon} {sign}</span>'
            )
        return format_html('<div style="display:flex;gap:4px">{}</div>', format_html("".join(badges)))
    compatibilities_badge.short_description = "Ententes"

    def save_model(self, request, obj, form, change):
        if not obj.author and request.user.is_authenticated:
            obj.author = request.user
        if not obj.published_at and obj.status == "published":
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        # Auto-assign category matching species if none chosen
        if not obj.categories.exists() and obj.species:
            species_slugs = {
                "chien": ["chiens", "chiens-a-ladoption", "les-chiens"],
                "chat": ["chats", "chats-a-ladoption", "les-chats"],
                "rongeur": ["rongeurs", "rongeurs-a-ladoption", "autres-animaux"],
            }
            target_slugs = species_slugs.get(obj.species, [])
            cat = Category.objects.filter(slug__in=target_slugs).first()
            if not cat and obj.species:
                cat = Category.objects.filter(name__icontains=obj.get_species_display()).first()
            if cat:
                obj.categories.add(cat)

        # If featured_image is empty, take the first gallery image
        if not obj.featured_image:
            first_gal = obj.gallery_images.select_related("media").first()
            if first_gal and first_gal.media:
                obj.featured_image = first_gal.media
                obj.save(update_fields=["featured_image"])

    @admin.action(description="🟢 Marquer comme Adoptable")
    def mark_as_adoptable(self, request, queryset):
        count = queryset.update(adoption_status="adoptable", is_adoptable=True)
        self.message_user(request, f"{count} fiche(s) animal(ux) marquée(s) comme Adoptable.")

    @admin.action(description="🟠 Marquer comme Réservé")
    def mark_as_reserved(self, request, queryset):
        count = queryset.update(adoption_status="reserve", is_adoptable=True)
        self.message_user(request, f"{count} fiche(s) animal(ux) marquée(s) comme Réservée(s).")

    @admin.action(description="🎉 Marquer comme Adopté (Retire l'urgence)")
    def mark_as_adopted(self, request, queryset):
        count = queryset.update(
            adoption_status="adopte",
            is_adoptable=False,
            is_emergency=False,
            adoption_date=timezone.now().date(),
        )
        self.message_user(request, f"{count} fiche(s) animal(ux) marquée(s) comme Adoptée(s).")

    @admin.action(description="🚨 Basculer en Urgence / À la une")
    def mark_as_emergency(self, request, queryset):
        eligible = queryset.exclude(adoption_status="adopte")
        count = eligible.update(is_emergency=True)
        skipped = queryset.count() - count
        msg = f"{count} fiche(s) basculée(s) en Urgence."
        if skipped > 0:
            msg += f" ({skipped} animal(ux) déjà adopté(s) ignoré(s))."
        self.message_user(request, msg)

    @admin.action(description="Retirer de l'Urgence")
    def remove_emergency(self, request, queryset):
        count = queryset.update(is_emergency=False)
        self.message_user(request, f"{count} fiche(s) retirée(s) de l'Urgence.")


@admin.register(Article)
class ArticleAdmin(BasePostAdmin):
    list_display = ("thumbnail_preview", "title", "category_list", "status_badge", "author", "published_at")
    list_filter = ("status", "categories", "tags", "published_at")
    search_fields = ("title", "content", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories", "tags")
    date_hierarchy = "published_at"
    list_per_page = 25
    fieldsets = (
        (None, {"fields": ("title", "slug", "content", "excerpt", "status", "author")}),
        ("Médias & Catégories", {"fields": ("featured_image", "categories", "tags")}),
        ("Publication", {"fields": ("published_at",)}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )

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
    category_list.short_description = "Catégories"

    def save_model(self, request, obj, form, change):
        if not obj.author and request.user.is_authenticated:
            obj.author = request.user
        if not obj.published_at and obj.status == "published":
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Hidden / Fallback PostAdmin if needed directly via URL and for autocomplete."""
    search_fields = ("title", "animal_name")

    def get_model_perms(self, request):
        # Hide Post from admin index so Animal and Article are the clean primary entries
        return {}


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


class MenuItemInline(admin.StackedInline):
    model = MenuItem
    extra = 1
    fieldsets = (
        (None, {
            "fields": (
                ("position", "title", "parent"),
                ("linked_post", "linked_page", "linked_category"),
            ),
        }),
        ("Lien externe / Options", {
            "classes": ("collapse",),
            "fields": (("url", "target"), "css_classes"),
        }),
    )
    autocomplete_fields = ("linked_post", "linked_page", "linked_category", "parent")
    ordering = ("position",)

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
