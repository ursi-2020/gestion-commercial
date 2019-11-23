from django.urls import path

from . import internalFunctions
from . import api
from . import schedule
from . import simulate

urlpatterns = [
    path('', internalFunctions.index, name='index'),

    # Api

    path('place-order', api.place_order, name='place-order'),
    path('stock-reorder', api.stock_reorder, name='stock-reorder'),




    # Schedule

    path('schedule/get-products', schedule.schedule_get_products_from_catalogue, name='schedule-get-product'),
    path('schedule/stock-reorder', schedule.schedule_stock_reorder, name='schedule-stock-reorder'),


    # Simulate

    path('simulate-index', simulate.index, name='simulate-index'),
    path('simulate-placing-order', simulate.simulate_placing_order, name='simulate-placing-order'),
    path('simulate-stock-response', simulate.simulate_stock_response, name='simulate-stock-response'),
    path('simulate-get-new-products', simulate.simulate_get_new_products, name='simulate-get-new-products'),
    path('simulate-stock-reorder', simulate.simulate_stock_reorder, name='simulate-stock-reorder'),
    path('simulate-get-stocks', simulate.simulate_get_stocks, name='simulate-get-stocks'),

    # Internal functions

    # Gestion du catalogue
    path('get-products', internalFunctions.get_product_from_catalogue, name='get-products'),
    path('display-products', internalFunctions.display_products, name='display-products'),
    path('delete-products', internalFunctions.delete_products, name='delete-products'),
    # Gestion réapro magasin
    path('display-orders', internalFunctions.display_orders, name='display-orders'),
    path('empty-orders', internalFunctions.empty_orders, name='empty-orders'),
    # Gestion réapro Stock
    path('display-stock-reorder', internalFunctions.display_stock_reorder, name='display-stock-reorder'),
    path('empty-stock-reorder', internalFunctions.empty_stock_reorder, name='empty-stock-reorder'),

]
