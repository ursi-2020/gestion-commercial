from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from apipkg import api_manager as api
from application.djangoapp.models import *
from .forms import UserForm, ArticleForm
from .models import User
from django.views.decorators.csrf import csrf_exempt
import json


def index(request):
    context = {}
    return render(request, 'index.html', context)


def get_product_fom_catalogue(request):
    Product.objects.all().delete()
    data = api.send_request('catalogue-produit', 'catalogueproduit/api/data')
    products = json.loads(data)['produits']
    for product in products:
        new_product = Product(**product)
        new_product.save()
    return redirect(display_products)


def display_products(request):
    produits = Product.objects.all().order_by("familleProduit")
    return render(request, 'info_catalogue_produits.html', {"produits": produits})
