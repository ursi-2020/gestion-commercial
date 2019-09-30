from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('schedule/get-products', views.schedule_get_products_from_catalogue, name='schedule-get-product'),
    path('get-products', views.get_product_fom_catalogue, name='get-products'),
    path('display-products', views.display_products, name='display-products')
]