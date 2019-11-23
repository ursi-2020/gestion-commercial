from django.shortcuts import render, redirect
import json
from .models import *
from . import api
from . import internalFunctions
from django.views.decorators.csrf import csrf_exempt
from apipkg import api_manager
from datetime import datetime
from django.http import HttpResponse
from apipkg import queue_manager as queue
import os




def index(request):
    context = {}
    return render(request, "index.html", context)

# Set la quantité initiale d'un produit
def init_quantite(quantiteMin):
    return 2 * quantiteMin

# Supprimer la liste de bon de commandes
def delete_products(request):
    Product.objects.all().delete()
    return redirect(display_products)


def dict_to_json(py_dict):
    tmp = json.loads(json.dumps(py_dict))
    return tmp

## Catalogue

# Get le catalogue
@csrf_exempt
def get_product_from_catalogue(request):
    Product.objects.all().delete()

    data = api_manager.send_request("catalogue-produit", "api/get-all")
    products = json.loads(data)["produits"]
    for product in products:
        new_product = Product.objects.create(
            codeProduit=product["codeProduit"],
            familleProduit=product["familleProduit"],
            descriptionProduit=product["descriptionProduit"],
            quantiteMin=product["quantiteMin"],
            packaging=product["packaging"],
            prix=product["prix"],
            quantite=internalFunctions.init_quantite(product["quantiteMin"])
            )

        new_product.save()
    nb_products = len(products)
    print(str(nb_products) + " products were saved")
    if nb_products > 0:
        log = Log()
        log.name = "last_product_update"
        log.code = 200
        log.text = str(nb_products) + " products were saved"
        log.time = datetime.now()
        log.save()
    if request.method == "GET":
        return redirect(internalFunctions.display_products)
    else:
        return HttpResponse()

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





