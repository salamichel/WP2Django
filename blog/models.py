from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, default="")
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )
    wp_term_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, default="")
    wp_term_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:tag", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Media(models.Model):
    title = models.CharField(max_length=512, blank=True, default="")
    file = models.FileField(upload_to="uploads/%Y/%m/")
    alt_text = models.CharField(max_length=512, blank=True, default="")
    caption = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    mime_type = models.CharField(max_length=100, blank=True, default="")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    wp_post_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    original_url = models.URLField(max_length=1024, blank=True, default="")

    class Meta:
        verbose_name_plural = "media"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title or self.file.name


class Post(models.Model):
    STATUS_CHOICES = [
        ("draft", "Brouillon"),
        ("published", "Publié"),
        ("pending", "En attente"),
        ("private", "Privé"),
        ("trash", "Corbeille"),
    ]

    title = models.CharField(max_length=512)
    slug = models.SlugField(max_length=512, unique=True)
    content = CKEditor5Field(blank=True, default="", config_name="default")
    excerpt = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    categories = models.ManyToManyField(Category, blank=True, related_name="posts")
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
    featured_image = models.ForeignKey(
        Media, null=True, blank=True, on_delete=models.SET_NULL, related_name="featured_for_posts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)

    # SEO
    seo_title = models.CharField(max_length=512, blank=True, default="")
    seo_description = models.TextField(blank=True, default="")

    # WordPress reference
    wp_post_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.slug})


class Page(models.Model):
    STATUS_CHOICES = [
        ("draft", "Brouillon"),
        ("published", "Publié"),
        ("private", "Privé"),
        ("trash", "Corbeille"),
    ]

    title = models.CharField(max_length=512)
    slug = models.SlugField(max_length=512, unique=True)
    content = CKEditor5Field(blank=True, default="", config_name="default")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )
    template = models.CharField(max_length=255, blank=True, default="")
    menu_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # SEO
    seo_title = models.CharField(max_length=512, blank=True, default="")
    seo_description = models.TextField(blank=True, default="")

    # WordPress reference
    wp_post_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["menu_order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:page_detail", kwargs={"slug": self.slug})


class Comment(models.Model):
    STATUS_CHOICES = [
        ("approved", "Approuvé"),
        ("pending", "En attente"),
        ("spam", "Spam"),
        ("trash", "Corbeille"),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author_name = models.CharField(max_length=255)
    author_email = models.EmailField(blank=True, default="")
    author_url = models.URLField(blank=True, default="")
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    wp_comment_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Commentaire de {self.author_name} sur {self.post}"


class Menu(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    location = models.CharField(max_length=100, blank=True, default="")
    wp_term_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=1024, blank=True, default="")
    target = models.CharField(max_length=50, blank=True, default="")
    css_classes = models.CharField(max_length=255, blank=True, default="")
    position = models.IntegerField(default=0)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )

    # Links to internal content
    content_type = models.CharField(max_length=50, blank=True, default="")
    object_id = models.PositiveIntegerField(null=True, blank=True)

    wp_post_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.title

    def get_url(self):
        if self.content_type == "post" and self.object_id:
            try:
                return Post.objects.get(wp_post_id=self.object_id).get_absolute_url()
            except Post.DoesNotExist:
                pass
        if self.content_type == "page" and self.object_id:
            try:
                return Page.objects.get(wp_post_id=self.object_id).get_absolute_url()
            except Page.DoesNotExist:
                pass
        if self.content_type == "category" and self.object_id:
            try:
                return Category.objects.get(wp_term_id=self.object_id).get_absolute_url()
            except Category.DoesNotExist:
                pass
        return self.url


class Redirect(models.Model):
    """Maps old WordPress URLs to new Django URLs."""
    old_path = models.CharField(max_length=1024, unique=True, db_index=True)
    new_path = models.CharField(max_length=1024)
    is_permanent = models.BooleanField(default=True)

    class Meta:
        ordering = ["old_path"]

    def __str__(self):
        return f"{self.old_path} -> {self.new_path}"


class PluginData(models.Model):
    """Stores data from detected WordPress plugins as structured JSON."""
    plugin_name = models.CharField(max_length=255, db_index=True)
    source_table = models.CharField(max_length=255)
    data = models.JSONField(default=dict)
    related_post = models.ForeignKey(
        Post, null=True, blank=True, on_delete=models.CASCADE, related_name="plugin_data"
    )
    related_page = models.ForeignKey(
        Page, null=True, blank=True, on_delete=models.CASCADE, related_name="plugin_data"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "plugin data"
        ordering = ["plugin_name", "-created_at"]

    def __str__(self):
        return f"{self.plugin_name}: {self.source_table}"
