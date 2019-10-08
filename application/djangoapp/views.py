from django.http import HttpResponse
# from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from apipkg import api_manager as api
from application.djangoapp.models import *
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
import json
import requests


def index(request):
    context = {}
    return render(request, 'index.html', context)


@csrf_exempt
def get_product_fom_catalogue(request):
    Product.objects.all().delete()
    data = api.send_request('catalogue-produit', 'api/data')
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


def delete_products(request):
    Product.objects.all().delete()
    return redirect(display_products)


def display_products(request):
    produits = Product.objects.all().order_by("familleProduit")
    if Log.objects.count() > 0:
        log = Log.objects.filter(name="last_product_update").latest('time')
    else:
        log = None
    return render(request, 'info_catalogue_produits.html', {"produits": produits, "log": log})


def display_orders(request):
    return HttpResponse("This is where you'll be able to see all current orders")


def place_order(request):
    return HttpResponse("This is where you'll be able to place an order")


def stock_reorder(request):
    return HttpResponse("This is where you'll be able to reorder to provide for the stocks")


def schedule_get_products_from_catalogue(request):
    clock_time = api.send_request('scheduler', 'clock/time')
    time = datetime.strptime(clock_time, '"%d/%m/%Y-%H:%M:%S"')
    time = time + timedelta(seconds=80)
    time_str = time.strftime('%d/%m/%Y-%H:%M:%S')
    body = {
        "target_url": 'get-products',
        "target_app": 'gestion-commerciale',
        "time": time_str,
        "recurrence": "minute",
        "data": '{}',
        "source_app": "gestion-commerciale",
        "name": "test"
    }
    r = schedule_task(body)
    return render(request, 'index.html', {})


def schedule_task(body):
    headers = {'Host': 'scheduler'}
    r = requests.post(api.api_services_url + 'schedule/add', headers=headers, json=body)
    print(r.status_code)
    print(r.text)
    return r.text