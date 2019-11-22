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
            codeProduit=list_sent[n]["codeProduit"],
            quantiteDemandee=list_asked[n]["quantite"],
            quantiteLivree=list_sent[n]["quantite"]
            )
        new_product.save()
    return JsonResponse(internalFunctions.dict_to_json(stock_response))


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