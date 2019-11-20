from django.http import HttpResponse
# from django.http import JsonResponse
from django.shortcuts import render, redirect
from apipkg import api_manager as api
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import random
from .models import *


def index(request):
    context = {}
    return render(request, "index.html", context)


# Set la quantité initiale

def init_quantite(quantiteMin):
    return 2 * quantiteMin

# Get le catalogue

@csrf_exempt
def get_product_fom_catalogue(request):
    Product.objects.all().delete()

    data = api.send_request("catalogue-produit", "api/get-all")
    products = json.loads(data)["produits"]
    for product in products:
        new_product = Product.objects.create(
            codeProduit=product["codeProduit"],
            familleProduit=product["familleProduit"],
            descriptionProduit=product["descriptionProduit"],
            quantiteMin=product["quantiteMin"],
            packaging=product["packaging"],
            prix=product["prix"],
            quantite=init_quantite(product["quantiteMin"])
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
        return redirect(display_products)
    else:
        return HttpResponse()


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


# Simule le comportement du magain quand il commande du stock

def simulate_placing_order(request):
    body = \
        {
            "idCommande": 123,
            "Produits": [
                {
                    "codeProduit": "X1-1",
                    "quantite": 1,
                },
                {
                    "codeProduit": "X1-2",
                    "quantite": 11,
                },
            ]
        }
    headers = {"Host": "gestion-commerciale"}
    r = requests.post(api.api_services_url + "place-order", headers=headers, json=dict_to_json(body))
    print(r.text)
    return redirect(display_orders)

# Simule le comportement de stock vis à vis du bon de commande

@csrf_exempt
def simulate_stock_response(request):
    return JsonResponse(json.loads(request.body))


# Display toutes les demandes de stock

def display_orders(request):
    orders = DeliveryRequest.objects.all()
    return render(request, "info_commandes.html", {"commandes": orders})


# Traitement d"une demande de réapprovisionnement

@csrf_exempt
def place_order(request):
    # load la requête de magasin
    jsonfile = json.loads(request.body)
    list_asked = jsonfile["Produits"]

    jsonfile["livraison"] = 0
    # Transmet la requête à Stock
    headers = {"Host": "gestion-stock"}
    response = requests.post(api.api_services_url + "api/get-from-stock", headers=headers, json=dict_to_json(jsonfile))
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
    return JsonResponse(dict_to_json(stock_response))


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
    get_product_fom_catalogue(request)
    jsonfile = []
    # Replace .all() with something like .justlecodeproduit
    for product in Product.objects.all():
        jsonfile.append({"codeProduit": product.codeProduit, "quantite": 0})
    return dict_to_json(jsonfile)


# gestion de l"envoi de ressources à Stock

def stock_reorder(request):
    date = api.send_request("scheduler", "clock/time")[1:-1]
    id_bon = 0
    for s in date:
        if s.isdigit():
            id_bon = id_bon * 10 + int(s)

    data = api.send_request("gestion-stock", "api/get-all")
    jsonfile = json.loads(data)

    if "stock" in jsonfile :
        if not jsonfile["stock"]:
            jsonfile["Produits"] = initialize_stock(request)
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
    requests.post(api.api_services_url + "api/add-to-stock", headers=headers, json=dict_to_json(jsonfile))
    return redirect(display_stock_reorder)


# Scheduler

def schedule_stock_reorder(request):
    clock_time = api.send_request("scheduler", "clock/time")
    time = datetime.strptime(clock_time, '"%d/%m/%Y-%H:%M:%S"')
    time = time + timedelta(seconds=80)
    time_str = time.strftime('%d/%m/%Y-%H:%M:%S')
    body = {
        "target_url": "stock-reorder",
        "target_app": "gestion-commerciale",
        "time": time_str,
        "recurrence": "jour",
        "data": "{}",
        "source_app": "gestion-commerciale",
        "name": "gesco-stock-reorder"
    }
    r = schedule_task(body)
    return render(request, "index.html", {})


def schedule_get_products_from_catalogue(request):
    clock_time = api.send_request("scheduler", "clock/time")
    time = datetime.strptime(clock_time, '"%d/%m/%Y-%H:%M:%S"')
    time = time + timedelta(seconds=80)
    time_str = time.strftime('%d/%m/%Y-%H:%M:%S')
    body = {
        "target_url": "get-products",
        "target_app": "gestion-commerciale",
        "time": time_str,
        "recurrence": "jour",
        "data": "{}",
        "source_app": "gestion-commerciale",
        "name": "gesco-get-product-catalogue"
    }
    r = schedule_task(body)
    return render(request, "index.html", {})


def schedule_task(body):
    headers = {"Host": "scheduler"}
    r = requests.post(api.api_services_url + "schedule/add", headers=headers, json=body)
    print(r.status_code)
    print(r.text)
    return r.text