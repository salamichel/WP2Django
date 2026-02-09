from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q

from blog.models import Post, Page, Category, Tag


def home(request):
    posts = Post.objects.filter(status="published").select_related(
        "author", "featured_image"
    ).prefetch_related("categories", "tags")[:5]
    return render(request, "blog/home.html", {"posts": posts})


def post_list(request):
    queryset = Post.objects.filter(status="published").select_related(
        "author", "featured_image"
    ).prefetch_related("categories", "tags")
    paginator = Paginator(queryset, settings.POSTS_PER_PAGE)
    page = request.GET.get("page")
    posts = paginator.get_page(page)
    return render(request, "blog/post_list.html", {"posts": posts})


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.select_related("author", "featured_image").prefetch_related(
            "categories", "tags", "comments"
        ),
        slug=slug,
        status="published",
    )
    comments = post.comments.filter(status="approved", parent__isnull=True).prefetch_related("replies")
    return render(request, "blog/post_detail.html", {"post": post, "comments": comments})


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, status="published")
    return render(request, "blog/page_detail.html", {"page": page})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    queryset = Post.objects.filter(
        status="published", categories=category
    ).select_related("author", "featured_image")
    paginator = Paginator(queryset, settings.POSTS_PER_PAGE)
    posts = paginator.get_page(request.GET.get("page"))
    return render(request, "blog/category.html", {"category": category, "posts": posts})


def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    queryset = Post.objects.filter(
        status="published", tags=tag
    ).select_related("author", "featured_image")
    paginator = Paginator(queryset, settings.POSTS_PER_PAGE)
    posts = paginator.get_page(request.GET.get("page"))
    return render(request, "blog/tag.html", {"tag": tag, "posts": posts})


def archive_year(request, year):
    queryset = Post.objects.filter(
        status="published", published_at__year=year
    ).select_related("author", "featured_image")
    paginator = Paginator(queryset, settings.POSTS_PER_PAGE)
    posts = paginator.get_page(request.GET.get("page"))
    return render(request, "blog/archive.html", {"posts": posts, "year": year, "month": None})


def archive_month(request, year, month):
    queryset = Post.objects.filter(
        status="published", published_at__year=year, published_at__month=month
    ).select_related("author", "featured_image")
    paginator = Paginator(queryset, settings.POSTS_PER_PAGE)
    posts = paginator.get_page(request.GET.get("page"))
    return render(request, "blog/archive.html", {"posts": posts, "year": year, "month": month})


def search(request):
    query = request.GET.get("q", "").strip()
    posts = Post.objects.none()
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query) | Q(excerpt__icontains=query),
            status="published",
        ).select_related("author", "featured_image")
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    return render(request, "blog/search.html", {
        "posts": paginator.get_page(request.GET.get("page")),
        "query": query,
    })
