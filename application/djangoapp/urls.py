from django.urls import path

from . import internalFunctions
from . import schedule
from . import simulate
from . import supplier

urlpatterns = [
    path('', internalFunctions.index, name='index'),

    # Schedule

    path('schedule/get-products', schedule.schedule_get_products_from_catalogue, name='schedule-get-product'),
    path('schedule/stock-reorder', schedule.schedule_stock_reorder, name='schedule-stock-reorder'),


    # Simulate

    path('simulate-index', simulate.index, name='simulate-index'),
    path('simulate-placing-order', simulate.simulate_placing_order, name='simulate-placing-order'),
    path('simulate-stock-response', simulate.simulate_stock_response, name='simulate-stock-response'),
    path('simulate-get-new-products', simulate.simulate_get_new_products, name='simulate-get-new-products'),
    path('simulate-get-stocks', simulate.simulate_get_stocks, name='simulate-get-stocks'),
    path('simulate-order-magasin', simulate.simulate_order_magasin, name='simulate-order-magasin'),

    # Test
    path('test-index', simulate.test_index, name='test-index'),
    path('test-send-stock-magasin', simulate.test_send_stock_magasin, name='test-send-stock-magasin'),
    path('test-send-order-stock', simulate.test_send_order_stock, name='test-send-order-stock'),

    # Internal functions

    # Gestion du catalogue
    path('display-products', internalFunctions.display_products, name='display-products'),
    path('delete-products', internalFunctions.delete_products, name='delete-products'),
    # Gestion réapro magasin
    path('display-orders', internalFunctions.display_orders, name='display-orders'),
    path('empty-orders', internalFunctions.empty_orders, name='empty-orders'),
    # Gestion réapro Stock
    path('display-stock-reorder', internalFunctions.display_stock_reorder, name='display-stock-reorder'),
    path('empty-stock-reorder', internalFunctions.empty_stock_reorder, name='empty-stock-reorder'),
    path('supplier-order', supplier.supplier_order, name='supplier-order'),



]
