from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('info', views.info, name='info'),
    path('info-catalogue-produits', views.info_catalogue_produits, name='info-catalogue-produits'),
    path('api/info', views.api_info, name='api-info'),
    path('add-user', views.add_user, name='add-user'),
]