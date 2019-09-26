from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get-products', views.get_product_fom_catalogue, name='get-products'),
    path('display-products', views.display_products, name='display-products')
]