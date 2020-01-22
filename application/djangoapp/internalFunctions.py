from django.shortcuts import render, redirect
import json
from .models import *
from . import supplier
from apipkg import api_manager
from apipkg import queue_manager as queue
import os


# Fonctions utiles

def index(request):
    context = {}
    return render(request, "index.html", context)


def sendAsyncMsg(to, body, functionName):
    time = api_manager.send_request('scheduler', 'clock/time')
    print(" [-] Sending Async message to", to, "with function", functionName)
    message = '{ "from":"' + os.environ[
        'DJANGO_APP_NAME'] + '", "to": "' + to + '", "datetime": ' + time + ', "body": ' + json.dumps(
       body) + ', "functionname":"' + functionName + '"}'
    queue.send(to, message)

def myprint(*args):
    IF_YOU_WANT_TO_PRINT_ANYTHING_SET_ME_TRUE = False
    if IF_YOU_WANT_TO_PRINT_ANYTHING_SET_ME_TRUE:
        for i in args:
            print(i, end='')
        print()


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

    commandeFournisseur["idCommande"] = id_bon

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
                quantiteDemandee=product.quantite,  #FIXME : not qtt demandee mais qtt actuelle ?
                quantiteLivree=None  #FIXME modifier ca quand on aura le fournisseur
            )
            newReorderProduct.save()

            commandeFournisseur["produits"].append({"codeProduit":product.codeProduit,"quantite":quantiteNeeded})
            isEmpty = False

    if isEmpty:
        myprint("Stocks are good. No need to reorder")
        return redirect(display_products)

    body = dict_to_json(commandeFournisseur)

    if simulate:
        sendAsyncMsg("gestion-commerciale", body, "simulate_fournisseur_stock")
    else:
        #TODO: wait for socle technique
        supplier.supplier_order(commandeFournisseur)

    return redirect(display_stock_reorder)


def updateQuantite(product):
    return 2 * product.quantiteMin


def updateQuantiteMin(product):
    #FIXME : j'ai bride l'update de qttmin pour les tests
    return 100


