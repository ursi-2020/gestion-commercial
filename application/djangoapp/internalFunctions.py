from django.shortcuts import render, redirect
import json
from .models import *
from . import api

def index(request):
    context = {}
    return render(request, "index.html", context)


# Set la quantité initiale

def init_quantite(quantiteMin):
    return 2 * quantiteMin



# Supprimer la liste de bon de commandes

def delete_products(request):
    Product.objects.all().delete()
    return redirect(display_products)


def dict_to_json(py_dict):
    tmp = json.loads(json.dumps(py_dict))
    return tmp


# Display les produits du catalogue

def display_products(request):
    products = Product.objects.all().order_by("familleProduit")
    if Log.objects.count() > 0:
        log = Log.objects.filter(name="last_product_update").latest("time")
    else:
        log = None
    return render(request, "info_catalogue_produits.html", {"products": products, "log": log})






# Display toutes les demandes de stock

def display_orders(request):
    orders = DeliveryRequest.objects.all()
    return render(request, "info_commandes.html", {"commandes": orders})




# Vide la db contenant les demandes de réapprovisionnement

def empty_orders(request):
    DeliveryRequest.objects.all().delete()
    return redirect(display_orders)


# Display les reorder du stock

def display_stock_reorder(request):
    orders = StockReorder.objects.all()
    return render(request, "info_reorder_stock.html", {"commandes": orders})


def empty_stock_reorder(request):
    StockReorder.objects.all().delete()
    return redirect(display_stock_reorder)


# Initialize the jsonfile if stock do not have product at all

def initialize_stock(request):
    api.get_product_from_catalogue(request)
    jsonfile = []
    # Replace .all() with something like .justlecodeproduit
    for product in Product.objects.all():
        jsonfile.append({"codeProduit": product.codeProduit, "quantite": 0})
    return dict_to_json(jsonfile)





