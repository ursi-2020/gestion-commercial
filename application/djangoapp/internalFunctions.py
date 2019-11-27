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
from django.http import JsonResponse


# Fonctions utiles

def index(request):
    context = {}
    return render(request, "index.html", context)

def sendAsyncMsg(to, body, functionName):
    time = api_manager.send_request('scheduler', 'clock/time')
    message = '{ "from":"' + os.environ[
        'DJANGO_APP_NAME'] + '", "to": "' + to + '", "datetime": ' + time + ', "body": ' + json.dumps(
       body) + ', "functionname":"' + functionName + '"}'
    queue.send(to, message)

def dict_to_json(py_dict):
    tmp = json.loads(json.dumps(py_dict))
    return tmp


# Catalogue

# Supprimer tous les produits
def delete_products(request):
    Product.objects.all().delete()
    return redirect(display_products)

# Display les produits du catalogue
def display_products(request):
    products = Product.objects.all().order_by("familleProduit")
    if Log.objects.count() > 0:
        log = Log.objects.filter(name="last_product_update").latest("time")
    else:
        log = None
    return render(request, "info_catalogue_produits.html", {"products": products, "log": log})



# Magasin

# Display toutes les demandes de réassort du magasin
def display_orders(request):
    requestProducts = RequestProduct.objects.all()
    return render(request, "info_commandes.html", {"requestProducts": requestProducts})


# Supprime les demandes de réassort du magasin
def empty_orders(request):
    RequestProduct.objects.all().delete()
    DeliveryRequest.objects.all().delete()
    return redirect(display_orders)




#Stock

# Display les reorders du stock
def display_stock_reorder(request):
    reorderProducts = ReorderProduct.objects.all()
    return render(request, "info_reorder_stock.html", {"reorderProducts": reorderProducts})

# Suprime les reorders du stocks
def empty_stock_reorder(request):
    StockReorder.objects.all().delete()
    return redirect(display_stock_reorder)

def reorderStock(simulate=False):
    products = Product.objects.all()

    commandeFournisseur = {}
    commandeFournisseur["produits"] = []

    date = api_manager.send_request("scheduler", "clock/time")[1:-1]
    id_bon = 0
    for s in date:
        if s.isdigit():
            id_bon = id_bon * 10 + int(s)

    commandeFournisseur["identifiantBon"] = id_bon

    newStockReorder = StockReorder.objects.create(identifiantBon=id_bon)
    newStockReorder.save()
    isEmpty = True
    for product in products:
        if product.quantite <= product.quantiteMin:
            if product.quantite == 0:
                product.quantiteMin = updateQuantiteMin(product)
                product.save()
            quantiteNeeded = product.quantiteMin - product.quantite
            newReorderProduct = ReorderProduct.objects.create(
                stockReorder=newStockReorder,
                product=Product.objects.filter(codeProduit=product.codeProduit)[0],
                quantiteDemandee=product.quantite,
                quantiteLivree=0
            )
            newReorderProduct.save()

            commandeFournisseur["produits"].append({"codeProduit":product.codeProduit,"quantite":quantiteNeeded})
            isEmpty = False

    if isEmpty:
        print ("Stocks are good. No need to reorder")
        return redirect(internalFunctions.display_products)

    body = internalFunctions.dict_to_json(commandeFournisseur)

    if simulate:
        internalFunctions.sendAsyncMsg("gestion-commerciale", body, "simulate_fournisseur_stock")
    else:
        #TODO: wait for socle technique
        internalFunctions.sendAsyncMsg("fournisseur", body, "fournisseur_stock")

    return redirect(internalFunctions.display_stock_reorder)


def updateQuantite(product):
    return 2 * product.quantiteMin

def updateQuantiteMin(product):
    return 2 * product.quantiteMin


