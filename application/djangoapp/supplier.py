import json

from apipkg import api_manager as api, api_manager
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from . import internalFunctions


def supplier_order(json_order):
    clock_time = api_manager.send_request("scheduler", "clock/time")
    time = datetime.strptime(clock_time, '"%d/%m/%Y-%H:%M:%S"')
    time = time + timedelta(days=2)
    time_str = time.strftime('%Y-%m-%d')

    if type(json_order) != dict:
        json_order = {'produits': [{'codeProduit': 'X1-60', 'quantite': 12}], 'idCommande': 1, 'dateLivraison': '08/02/2019-11:52:05'}

    json_order_edit = {}
    json_order_edit["commande"] = {}
    json_order_edit["commande"]["items"] = json_order["produits"]
    json_order_edit["commande"]["numeroCommande"] = str(json_order["idCommande"])

    json_order_edit["commande"]["dateLivraison"] = time_str

    (code, resp) = api.post_request2('fo', 'order', json.dumps(json.loads(json.dumps(json_order_edit))))
    internalFunctions.sendAsyncMsg("business-intellignece", internalFunctions.dict_to_json(json_order_edit), "Commande fournisseur")
    return HttpResponse(resp.text)


@csrf_exempt
def supplier_receive(request):
    internalFunctions.myprint('!!!!!!! WHY AM I USED ?????????????????????????????????????          !!!!!!!')
    internalFunctions.myprint("received supplier response :")
    body = json.loads(request.body)
    body["livraison"] = 1
    internalFunctions.sendAsyncMsg("gestion-stock", body, "resupply")
    return HttpResponse(request)


@csrf_exempt
def ship_orders_to_customer(request):
    internalFunctions.myprint('!!!!!!! Received supplier delivery !!!!!!!')
    internalFunctions.myprint(request.body)
    body = json.loads(request.body)
    for l in body["livraisons"]:
        b = {}
        b["idCommande"] = l["numeroCommande"]
        b["produits"] = l["items"]
        b["livraison"] = 1
        #FIXME : find the id in the database and update the amount delivred
        internalFunctions.sendAsyncMsg("gestion-stock", b, "resupply")

    return HttpResponse('salut les enfants :) ')

@csrf_exempt
def test(request):
    internalFunctions.myprint('Received facture')
    internalFunctions.sendAsyncMsg("business-intelligence", json.dumps(json.loads(request.body)), "get_bill")
    return HttpResponse("okidoki les amis :)")