from django.http import HttpResponse
# from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from apipkg import api_manager as api
from application.djangoapp.models import *
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import random


def index(request):
    context = {}
    return render(request, 'index.html', context)


# Get le catalogue

@csrf_exempt
def get_product_fom_catalogue(request):
    Product.objects.all().delete()
    data = api.send_request('catalogue-produit', 'api/get-all')
    products = json.loads(data)['produits']
    for product in products:
        new_product = Product(**product)
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


# Display les produits du catalogue

def display_products(request):
    produits = Product.objects.all().order_by("familleProduit")
    if Log.objects.count() > 0:
        log = Log.objects.filter(name="last_product_update").latest('time')
    else:
        log = None
    return render(request, 'info_catalogue_produits.html', {"produits": produits, "log": log})


# Simule le comportement du magain quand il commande du stock

def simulate_placing_order(request):
    body = \
        {
            "idCommande": 12,
            "Produits": [
                {
                    "codeProduit": 3291,
                    "quantite": 1,
                },
                {
                    "codeProduit": 32,
                    "quantite": 11,
                },
            ]
        }
    headers = {'Host': 'gestion-commerciale'}
    r = requests.post(api.api_services_url + 'place-order', headers=headers, json=body)

    return redirect(display_orders)


# Simule le comportement de stock vis à vis du bon de commande

@csrf_exempt
def simulate_stock_response(request):
    return JsonResponse(json.loads(request.body))


# Display toutes les demandes de stock

def display_orders(request):
    orders = DeliveryRequest.objects.all()
    return render(request, 'info_commandes.html', {"commandes": orders})


# Traitement d'une demande de réapprovisionnement

@csrf_exempt
def place_order(request):
    jsonfile = json.loads(request.body)
    list_asked = jsonfile['Produits']

    headers = {'Host': 'gestion-commerciale'}
    response = requests.post(api.api_services_url + 'simulate-stock-response', headers=headers, json=jsonfile)

    jsonfile = json.loads(response.text)
    list_sent = jsonfile['Produits']

    for n in range(0, len(list_asked)):
        new_product = DeliveryRequest.objects.create(
            identifiantBon=jsonfile['idCommande'],
            codeProduit=list_sent[n]['codeProduit'],
            quantiteDemandee=list_asked[n]['quantite'],
            quantiteLivree=list_sent[n]['quantite']
            )
        new_product.save()

    return JsonResponse(jsonfile)


# Vide la db contenant les demandes de réapprovisionnement

def empty_orders(request):
    DeliveryRequest.objects.all().delete()
    return redirect(display_orders)


# Display les reorder du stock

def display_stock_reorder(request):
    orders = StockReorder.objects.all()
    return render(request, 'info_reorder_stock.html', {"commandes": orders})


def empty_stock_reorder(request):
    StockReorder.objects.all().delete()
    return redirect(display_stock_reorder)


# gestion de l'envoi de ressources à Stock

def stock_reorder(request):
    # Call route pour get stock
    data = api.send_request('gestion-commerciale', 'simulate-reorder-stock')
    date = api.send_request('scheduler', 'clock/time')[1:-1]
    id_bon = 0
    for s in date:
        if s.isdigit():
            id_bon = id_bon * 10 + int(s)

    jsonfile = json.loads(data)
    for product in jsonfile["Produits"]:
        modulo = random.randrange(10, 30)
        new_product = StockReorder.objects.create(
            identifiantBon=id_bon,
            codeProduit=product['codeProduit'],
            quantiteAvant=product["quantite"],
            quantiteLivree=modulo,
            dateLivraison=date
            )
        new_product.save()
        product["quantité"] = modulo
    jsonfile['livraison'] = True

    #headers = {'Host': 'gestion-commerciale'}
    #requests.post(api.api_services_url + 'simulate-stock-response', headers=headers, json=jsonfile)
    return redirect(display_stock_reorder)


def simulate_reorder_stock(request):
    body = \
        {
            "Produits": [
                {
                    "codeProduit": 3291,
                    "quantite": 1,
                },
                {
                    "codeProduit": 32,
                    "quantite": 11,
                },
            ]
        }
    return JsonResponse(body)


# Scheduler

def schedule_stock_reorder(request):
    clock_time = api.send_request('scheduler', 'clock/time')
    time = datetime.strptime(clock_time, '"%d/%m/%Y-%H:%M:%S"')
    time = time + timedelta(seconds=80)
    time_str = time.strftime('%d/%m/%Y-%H:%M:%S')
    body = {
        "target_url": 'stock-reorder',
        "target_app": 'gestion-commerciale',
        "time": time_str,
        "recurrence": "jour",
        "data": '{}',
        "source_app": "gestion-commerciale",
        "name": "gesco-stock-reorder"
    }
    r = schedule_task(body)
    return render(request, 'index.html', {})


def schedule_get_products_from_catalogue(request):
    clock_time = api.send_request('scheduler', 'clock/time')
    time = datetime.strptime(clock_time, '"%d/%m/%Y-%H:%M:%S"')
    time = time + timedelta(seconds=80)
    time_str = time.strftime('%d/%m/%Y-%H:%M:%S')
    body = {
        "target_url": 'get-products',
        "target_app": 'gestion-commerciale',
        "time": time_str,
        "recurrence": "jour",
        "data": '{}',
        "source_app": "gestion-commerciale",
        "name": "gesco-get-product-catalogue"
    }
    r = schedule_task(body)
    return render(request, 'index.html', {})


def schedule_task(body):
    headers = {'Host': 'scheduler'}
    r = requests.post(api.api_services_url + 'schedule/add', headers=headers, json=body)
    print(r.status_code)
    print(r.text)
    return r.text