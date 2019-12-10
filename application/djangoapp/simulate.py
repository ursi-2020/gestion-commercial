from . import internalFunctions
from apipkg import api_manager

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.shortcuts import render, redirect


def index(request):
    context = {}
    return render(request, "simulate.html", context)

def test_index(request):
    return render (request, "test.html", {})


def test_send_stock_magasin(request):
    return 0


def test_send_order_stock(request) :
    body = {
            "livraison": 0,
            "idCommande": 123,
            "produits": [
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
    internalFunctions.sendAsyncMsg("gestion-stock", internalFunctions.dict_to_json(body), "get_order_stocks")

    return test_index(request)

# Simule le catalogue quand il envoie de nouveaux produits
def simulate_get_new_products(request):
    body = \
        {
            "produits": [
                {
                    "id": 1664,
                    "codeProduit": "X1664",
                    "familleProduit": "Bière",
                    "descriptionProduit": "1664",
                    "quantiteMin": 24,
                    "packaging": 1,
                    "prix": 666,
                    "exclusivite": ""
                },
                {
                    "id": 1,
                    "codeProduit": "X3-0",
                    "familleProduit": "Surgelés",
                    "descriptionProduit": "Pizza",
                    "quantiteMin": 1,
                    "packaging": 2,
                    "prix": 12,
                    "exclusivite": "ecommerce"
                },
            ]
        }

    internalFunctions.sendAsyncMsg("gestion-commerciale", body, "get_new_products")
    return redirect(internalFunctions.display_products)


# OLD REQUETE  EN SYNCHRONE !
# Simule le comportement du magain quand il commande du stock
def simulate_placing_order(request):
    body = \
        {
            "idCommande": 123,
            "produits": [
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
    r = requests.post(api_manager.api_services_url + "place-order", headers=headers, json=internalFunctions.dict_to_json(body))
    print(r.text)
    return redirect(internalFunctions.display_orders)

# Simule le comportement du magain quand il commande du stock
def simulate_order_magasin(request):
    body = \
        {
            "idCommande": 123,
            "produits": [
                {
                    "codeProduit": "X1664",
                    "quantite": 10,
                },
                {
                    "codeProduit": "X3-0",
                    "quantite": 1,
                },
            ]
        }
    internalFunctions.sendAsyncMsg("gestion-commerciale", body, "get_order_magasin")
    return redirect(internalFunctions.display_orders)


## Simule le comportement des stocks quand il envoie des stocks
def simulate_get_stocks(request):
    body = \
        {
            "produits": [
                {
                    "codeProduit": "X1664",
                    "quantite": 12,
                },
                {
                    "codeProduit": "X3-0",
                    "quantite": 10,
                },
            ]
        }
    internalFunctions.sendAsyncMsg("gestion-commerciale", body, "get_stocks")
    return redirect(internalFunctions.display_products)



def simulate_get_order_stocks(jsonLoad):
    internalFunctions.sendAsyncMsg("gestion-commerciale", jsonLoad["body"], "get_stock_order_response")
    return redirect(internalFunctions.display_stock_reorder)


@csrf_exempt
def simulate_stock_response(request):
    return JsonResponse(json.loads(request.body))


def simulate_fournisseur_stock(jsonLoad):
    internalFunctions.sendAsyncMsg("gestion-commerciale", jsonLoad["body"], "fournisseur_stock_response")
    return redirect(internalFunctions.display_stock_reorder)
