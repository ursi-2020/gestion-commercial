from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('info', views.info, name='info'),
    path('info-catalogue-produits', views.info_catalogue_produits, name='info-catalogue-produits'),
    path('add-user', views.add_user, name='add-user'),
    path('api-info', views.api_info, name='api-info'),
    path('api-add-user', views.api_add_user, name='api-add-user'),
    path('add-article-catalogue-produits', views.add_article_catalogue_produits, name='add-article-catalogue-produits'),
]