from django.urls import path
from blog import views

app_name = "blog"

urlpatterns = [
    path("", views.home, name="home"),
    path("articles/", views.post_list, name="post_list"),
    path("articles/<slug:slug>/", views.post_detail, name="post_detail"),
    path("categorie/<slug:slug>/", views.category_detail, name="category"),
    path("tag/<slug:slug>/", views.tag_detail, name="tag"),
    path("archives/<int:year>/", views.archive_year, name="archive_year"),
    path("archives/<int:year>/<int:month>/", views.archive_month, name="archive_month"),
    path("recherche/", views.search, name="search"),
    path("<slug:slug>/", views.page_detail, name="page_detail"),
]
