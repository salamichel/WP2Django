from django.urls import path
from blog import views

app_name = "blog"

urlpatterns = [
    path("", views.home, name="home"),
    path("adoptions/", views.post_list, name="post_list"),
    path("adoptions/<slug:slug>/", views.post_detail, name="post_detail"),
    path("articles/", views.legacy_articles_redirect, name="legacy_articles"),
    path("articles/<slug:slug>/", views.legacy_post_detail_redirect, name="legacy_post_detail"),
    path("categories/les-adoptes/<int:year>/", views.adoptions_by_year, name="adoptions_by_year"),
    path("categories/<slug:slug>/", views.category_detail, name="category"),
    path("categorie/les-adoptes/<int:year>/", views.adoptions_by_year, name="adoptions_by_year_singular"),
    path("categorie/<slug:slug>/", views.category_detail, name="category_singular"),
    path("tag/<slug:slug>/", views.tag_detail, name="tag"),
    path("archives/<int:year>/", views.archive_year, name="archive_year"),
    path("archives/<int:year>/<int:month>/", views.archive_month, name="archive_month"),
    path("recherche/", views.search, name="search"),
    path("pages/<slug:slug>/", views.page_detail, name="page_detail_alias"),
    path("<slug:slug>/", views.page_detail, name="page_detail"),
]
