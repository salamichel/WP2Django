from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q

from blog.models import Post, Page, Category, Tag


def home(request):
    emergency_posts = Post.objects.filter(status="published").filter(
        Q(is_emergency=True) | Q(adoption_status="recherche_fa")
    ).select_related("author", "featured_image").prefetch_related("categories", "tags")[:4]

    latest_posts = Post.objects.filter(status="published").select_related(
        "author", "featured_image"
    ).prefetch_related("categories", "tags")[:6]

    return render(request, "blog/home.html", {
        "emergency_posts": emergency_posts,
        "posts": latest_posts,
    })


def _render_post_catalogue(request, base_queryset=None, initial_filters=None, page_title=None, category=None):
    if base_queryset is None:
        queryset = Post.objects.filter(status="published")
    else:
        queryset = base_queryset.filter(status="published")

    queryset = queryset.select_related("author", "featured_image").prefetch_related("categories", "tags")

    init_f = initial_filters or {}

    # Extract Filters (Query params take priority if provided)
    q = request.GET.get("q", init_f.get("q", "")).strip()

    if "species" in request.GET:
        species = request.GET.get("species", "").strip()
    else:
        species = init_f.get("species", "").strip()

    sex = request.GET.get("sex", init_f.get("sex", "")).strip()
    adoption_status = request.GET.get("status", init_f.get("status", "")).strip()
    ok_dogs = request.GET.get("ok_dogs", init_f.get("ok_dogs", "")).strip()
    ok_cats = request.GET.get("ok_cats", init_f.get("ok_cats", "")).strip()
    ok_children = request.GET.get("ok_children", init_f.get("ok_children", "")).strip()
    housing = request.GET.get("housing", init_f.get("housing", "")).strip()

    if "emergency" in request.GET:
        emergency = request.GET.get("emergency", "").strip()
    else:
        emergency = str(init_f.get("emergency", "")).strip()

    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) |
            Q(animal_name__icontains=q) |
            Q(breed__icontains=q) |
            Q(content__icontains=q) |
            Q(excerpt__icontains=q)
        )
    if species:
        queryset = queryset.filter(species=species)
    if sex:
        queryset = queryset.filter(sex=sex)
    if adoption_status:
        queryset = queryset.filter(adoption_status=adoption_status)
    if ok_dogs:
        queryset = queryset.filter(ok_dogs=ok_dogs)
    if ok_cats:
        queryset = queryset.filter(ok_cats=ok_cats)
    if ok_children:
        queryset = queryset.filter(ok_children=ok_children)
    if housing:
        queryset = queryset.filter(housing_requirement=housing)
    if emergency in ["1", "true", "True", "urgence", "urgences"]:
        queryset = queryset.filter(is_emergency=True)

    total_count = queryset.count()
    paginator = Paginator(queryset, settings.POSTS_PER_PAGE)
    page = request.GET.get("page")
    posts = paginator.get_page(page)

    current_filters = {
        "q": q,
        "species": species,
        "sex": sex,
        "status": adoption_status,
        "ok_dogs": ok_dogs,
        "ok_cats": ok_cats,
        "ok_children": ok_children,
        "housing": housing,
        "emergency": emergency,
    }

    context = {
        "posts": posts,
        "total_count": total_count,
        "filters": current_filters,
        "has_filters": any(current_filters.values()),
        "page_title": page_title,
        "category": category,
    }

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.GET.get("ajax") == "1"
    template_name = "includes/_post_grid.html" if is_ajax else "blog/post_list.html"

    return render(request, template_name, context)


def post_list(request):
    return _render_post_catalogue(request, page_title="Nos protégés & Actualités")


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.select_related("author", "featured_image").prefetch_related(
            "categories", "tags", "comments",
            "gallery_images__media",
        ),
        slug=slug,
        status="published",
    )
    comments = post.comments.filter(status="approved", parent__isnull=True).prefetch_related("replies")
    gallery_images = post.gallery_images.select_related("media").all()
    return render(request, "blog/post_detail.html", {
        "post": post,
        "comments": comments,
        "gallery_images": gallery_images,
    })


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, status="published")
    return render(request, "blog/page_detail.html", {"page": page})


def _get_adoption_years():
    """Retrieve distinct adoption years from Post.adoption_date and Category slugs."""
    import re
    from django.db.models.functions import ExtractYear
    years = set(
        Post.objects.filter(status="published", adoption_date__isnull=False)
        .annotate(year=ExtractYear("adoption_date"))
        .values_list("year", flat=True)
    )
    for cat in Category.objects.filter(slug__regex=r"^les-adoptes-\d{4}$"):
        match = re.search(r"(\d{4})", cat.slug)
        if match:
            years.add(int(match.group(1)))

    return sorted([int(y) for y in years if y], reverse=True)


def adoptions_by_year(request, year):
    """Display adopted animals for a specific year, e.g. /categories/les-adoptes/2026/."""
    from django.db.models import Q
    year = int(year)

    category = Category.objects.filter(slug__in=[f"les-adoptes-{year}", f"adoptes-{year}"]).first()
    if not category:
        parent_cat, _ = Category.objects.get_or_create(slug="les-adoptes", defaults={"name": "Les Adoptés"})
        category, _ = Category.objects.get_or_create(
            slug=f"les-adoptes-{year}",
            defaults={"name": f"Les Adoptés {year}", "parent": parent_cat}
        )

    queryset = Post.objects.filter(status="published").filter(
        Q(adoption_date__year=year) | Q(categories=category) | Q(categories__slug=f"les-adoptes-{year}")
    ).distinct().select_related("author", "featured_image").prefetch_related("categories", "tags")

    paginator = Paginator(queryset, settings.POSTS_PER_PAGE)
    posts = paginator.get_page(request.GET.get("page"))

    return render(request, "blog/category.html", {
        "category": category,
        "posts": posts,
        "total_count": queryset.count(),
        "adoption_years": _get_adoption_years(),
        "current_adoption_year": year,
        "is_adoption_archive": True,
        "page_title": f"Les Adoptés {year}",
    })


def category_detail(request, slug):
    import re
    from django.db.models import Q

    # Check for yearly adoption category URL (e.g. les-adoptes-2026)
    match_year = re.match(r"^(?:les-)?adoptes-(\d{4})$", slug)
    if match_year:
        return adoptions_by_year(request, int(match_year.group(1)))

    possible_slugs = [slug]
    if slug.startswith("les-"):
        possible_slugs.append(slug[4:])
    else:
        possible_slugs.append(f"les-{slug}")

    category = Category.objects.filter(slug__in=possible_slugs).first()
    if not category:
        category = get_object_or_404(Category, slug=slug)

    canonical_slug = category.slug.replace("les-", "")

    animal_species_map = {
        "chiens": "chien",
        "chien": "chien",
        "chats": "chat",
        "chat": "chat",
        "rongeurs": "rongeur",
        "rongeur": "rongeur",
    }

    if canonical_slug in animal_species_map:
        return _render_post_catalogue(
            request,
            initial_filters={"species": animal_species_map[canonical_slug]},
            page_title=f"Nos {category.name} à l'adoption",
            category=category,
        )
    elif canonical_slug in ["urgences", "urgence"]:
        return _render_post_catalogue(
            request,
            initial_filters={"emergency": "1"},
            page_title="Urgences & Recherche FA",
            category=category,
        )
    elif canonical_slug in ["adoptes", "adopte"]:
        # All adopted animals with year navigation
        queryset = Post.objects.filter(status="published").filter(
            Q(categories=category) | Q(adoption_status="adopte") | Q(categories__slug__startswith="les-adoptes")
        ).distinct().select_related("author", "featured_image").prefetch_related("categories", "tags")
        paginator = Paginator(queryset, settings.POSTS_PER_PAGE)
        posts = paginator.get_page(request.GET.get("page"))
        return render(request, "blog/category.html", {
            "category": category,
            "posts": posts,
            "total_count": queryset.count(),
            "adoption_years": _get_adoption_years(),
            "current_adoption_year": None,
            "is_adoption_archive": True,
            "page_title": "Tous les adoptés",
        })
    else:
        # Standard non-animal categories (news, press)
        queryset = Post.objects.filter(
            status="published", categories=category
        ).select_related("author", "featured_image").prefetch_related("categories", "tags")
        paginator = Paginator(queryset, settings.POSTS_PER_PAGE)
        posts = paginator.get_page(request.GET.get("page"))
        return render(request, "blog/category.html", {
            "category": category,
            "posts": posts,
            "total_count": queryset.count(),
        })


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
