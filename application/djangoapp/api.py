from django.http import HttpResponse
from django.shortcuts import redirect
from apipkg import api_manager
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import random
from .models import *
from . import internalFunctions
import os
from apipkg import queue_manager as queue



#Catalogue
# Récupère les nouveaux produits
def get_new_products(jsonLoad):
    products = jsonLoad["body"]["produits"]
    for product in products:
        new_product = Product.objects.create(
            codeProduit=product["codeProduit"],
            familleProduit=product["familleProduit"],
            descriptionProduit=product["descriptionProduit"],
            quantiteMin=product["quantiteMin"],
            packaging=product["packaging"],
            prix=product["prix"],
            quantite=0
        )

        new_product.save()
    nb_products = len(products)
    print(str(nb_products) + " products were saved")

    return redirect(internalFunctions.display_products)

# Magasin

# Traitement d"une demande de réapprovisionnement
@csrf_exempt
def place_order(request):
    # load la requête de magasin
    jsonfile = json.loads(request.body)
    list_asked = jsonfile["Produits"]

    jsonfile["livraison"] = 0
    # Transmet la requête à Stock
    headers = {"Host": "gestion-stock"}
    response = requests.post(api_manager.api_services_url + "api/get-from-stock", headers=headers, json=internalFunctions.dict_to_json(jsonfile))
    stock_response = json.loads(response.text)["Response"]

    list_sent = stock_response["Produits"]

    for n in range(0, len(list_asked)):
        new_product = DeliveryRequest.objects.create(
            identifiantBon=stock_response["idCommande"],
            product=list_sent[n]["codeProduit"],
            quantiteDemandee=list_asked[n]["quantite"],
            quantiteLivree=list_sent[n]["quantite"]
            )
        new_product.save()
    return JsonResponse(internalFunctions.dict_to_json(stock_response))


def get_order_magasin(jsonLoad, simulate=False):
    body = jsonLoad["body"]
    body["livraison"] = 0
    products = body["produits"]


    newDeliveryRequest = DeliveryRequest.objects.create( identifiantBon=body["idCommande"])
    newDeliveryRequest.save()
    for product in products:
        newRequestProduct = RequestProduct.objects.create(
            deliveryRequest= newDeliveryRequest,
            product=Product.objects.filter(codeProduit=product["codeProduit"])[0],
            quantiteDemandee=product["quantite"],
            quantiteLivree=0
        )
        newRequestProduct.save()

    time = api_manager.send_request('scheduler', 'clock/time')
    message = None
    if simulate:
        message = '{ "from":"' + os.environ[
            'DJANGO_APP_NAME'] + '", "to":"gestion-commerciale", "datetime": ' + time + ', "body": ' + json.dumps(
            body) + ', "functionname":"simulate_get_order_stocks"}'
        queue.send('gestion-commerciale', message)
    else:
        message = '{ "from":"' + os.environ[
        'DJANGO_APP_NAME'] + '", "to":"gestion-stock", "datetime": ' + time + ', "body": ' + json.dumps(
        body) + ', "functionname":"get_order_stocks"}'
        queue.send('gestion-stock', message)
    return redirect(internalFunctions.display_products)


# Stock

# Reçoit l'état des stocks
def get_stocks(jsonLoad, simulate=False):
    products = jsonLoad["body"]["produits"]
    for product in products:
        p = Product.objects.filter(codeProduit=product["codeProduit"])[0]
        p.quantite = product["quantite"]
        p.save()
    internalFunctions.reorderStock(simulate)

# gestion de l"envoi de ressources à Stock
def stock_reorder(request):
    date = api_manager.send_request("scheduler", "clock/time")[1:-1]
    id_bon = 0
    for s in date:
        if s.isdigit():
            id_bon = id_bon * 10 + int(s)

    data = api_manager.send_request("gestion-stock", "api/get-all")
    jsonfile = json.loads(data)

    if "stock" in jsonfile :
        if not jsonfile["stock"]:
            jsonfile["Produits"] = internalFunctions.initialize_stock(request)
        else:
            jsonfile["Produits"] = jsonfile["stock"]
    else:
        HttpResponse("Stock changed their json return value")

    jsonfile.pop("stock", None)
    list_products = jsonfile["Produits"]
    for product in list_products:
        modulo = random.randrange(10, 30)
        new_product = StockReorder.objects.create(
            identifiantBon=id_bon,
            codeProduit=product["codeProduit"],
            quantiteAvant=product["quantite"],
            quantiteLivree=modulo,
            dateLivraison=date
            )
        new_product.save()
        product["quantite"] = modulo
    jsonfile["livraison"] = 1
    jsonfile["idCommande"] = id_bon

    headers = {"Host": "gestion-stock"}
    requests.post(api_manager.api_services_url + "api/add-to-stock", headers=headers, json=internalFunctions.dict_to_json(jsonfile))
    return redirect(internalFunctions.display_stock_reorder)

def get_stock_order_response(jsonLoad, simulate=False):
    body = jsonLoad["body"]
    products = jsonLoad["body"]["produits"]
    deliveryRequest = DeliveryRequest.objects.filter(identifiantBon=body["idCommande"])[0]
    for product in products:
        p = Product.objects.filter(codeProduit=product["codeProduit"])[0]
        p.quantite += product["quantite"]
        p.save()

        requestProduct = RequestProduct.objects.filter(deliveryRequest=deliveryRequest, product=p)[0]

        requestProduct.quantiteLivree = product["quantite"]
        requestProduct.save()

    time = api_manager.send_request('scheduler', 'clock/time')
    if simulate:
        message = '{ "from":"' + os.environ[
            'DJANGO_APP_NAME'] + '", "to":"gestion-commerciale", "datetime": ' + time + ', "body": ' + json.dumps(
            body) + ', "functionname":"simulate_magasin_get_order_response"}'
        queue.send('gestion-commerciale', message)
    else:
        message = '{ "from":"' + os.environ[
        'DJANGO_APP_NAME'] + '", "to":"gestion-magasin", "datetime": ' + time + ', "body": ' + json.dumps(
        body) + ', "functionname":"get_order_response"}'
        queue.send('gestion-magasin', message)
    return redirect(internalFunctions.display_products)

def fournisseur_stock_response(jsonLoad, simulate=False):

    body = jsonLoad["body"]
    products = jsonLoad["body"]["produits"]

    stockReorder = StockReorder.objects.filter(identifiantBon=body["identifiantBon"])[0]
    for product in products:
        p = Product.objects.filter(codeProduit=product["codeProduit"])[0]
        p.quantite = product["quantite"]
        p.save()

        reorderProduct = ReorderProduct.objects.filter(stockReorder=stockReorder, product=p)[0]


        reorderProduct.quantiteLivree = product["quantite"]
        reorderProduct.save()

    time = api_manager.send_request('scheduler', 'clock/time')
    if simulate:
        message = '{ "from":"' + os.environ[
            'DJANGO_APP_NAME'] + '", "to":"gestion-commerciale", "datetime": ' + time + ', "body": ' + json.dumps(
            body) + ', "functionname":"simulate_stock_reorder"}'
        queue.send('gestion-commerciale', message)
    else:
        message = '{ "from":"' + os.environ[
        'DJANGO_APP_NAME'] + '", "to":"gestion-stock", "datetime": ' + time + ', "body": ' + json.dumps(
        body) + ', "functionname":"stock_reorder"}'
        queue.send('gestion-stock', message)
    return redirect(internalFunctions.display_products)



