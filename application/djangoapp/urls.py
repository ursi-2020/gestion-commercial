from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # Gestion du catalogue
    path('schedule/get-products', views.schedule_get_products_from_catalogue, name='schedule-get-product'),
    path('get-products', views.get_product_fom_catalogue, name='get-products'),
    path('display-products', views.display_products, name='display-products'),
    path('delete-products', views.delete_products, name='delete-products'),

    # Gestion réapro magasin
    path('display-orders', views.display_orders, name='display-orders'),
    path('place-order', views.place_order, name='place-order'),
    path('stock-reorder', views.stock_reorder, name='stock-reorder'),
    path('simulate-placing-order', views.simulate_placing_order, name='simulate-placing-order'),
    path('empty-orders', views.empty_orders, name='empty-orders'),
    path('simulate-stock-response', views.simulate_stock_response, name='simulate-stock-response'),

    # Gestion réapro Stock
    path('stock-reorder', views.stock_reorder, name='stock-reorder'),
    path('display-stock-reorder', views.display_stock_reorder, name='display-stock-reorder'),
    path('empty-stock-reorder', views.empty_stock_reorder, name='empty-stock-reorder'),
    path('schedule/stock-reorder', views.schedule_stock_reorder, name='schedule-stock-reorder'),

    path('test-async', views.test_async, name='test-async'),

    #simulate
    path('simulate-get-new-products', views.simulate_get_new_products, name='simulate-get-new-products'),

]
