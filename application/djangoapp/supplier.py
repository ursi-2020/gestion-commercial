import json

from apipkg import api_manager as api
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from . import internalFunctions


def supplier_order(json_order):
    print("supply_order activated")
    ouiouibaguett = {
        "commande": {
            "numeroCommande": '32',
            "dateLivraison": '2019-02-05',
            "items":  [
                {"codeProduit": 'X1-33', "quantite": 3},
                {"codeProduit": 'X1-25', "quantite": 3}
            ]

        }
    }

    #   (code, resp) = api.post_request2('fo', 'order', json.dumps(ouiouibaguett))

    (code, resp) = api.post_request2('gestion-commerciale', 'supplier-receive', json.dumps(json_order))
    return HttpResponse(resp.text)
    #   return HttpResponse(404)


@csrf_exempt
def supplier_receive(request):
    print('!!!!!!! SUPPLY RECEVED!!!!!!!')
    print("received supplier response :")
    body = json.loads(request.body)
    body["livraison"] = 1
    internalFunctions.sendAsyncMsg("gestion-stock", body, "resupply")
    return HttpResponse(request)


@csrf_exempt
def ship_orders_to_customer(request):
    print('!!!!!!! SHIP ORDER TO CUSTOMER !!!!!!!')
    print(request.body)
    internalFunctions.sendAsyncMsg("business-intellignece", json.loads(request.body), "myvalue")
    return HttpResponse('salut les enfants :) ')

@csrf_exempt
def test(request):
    print('this is a test §!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(request.body)
    return HttpResponse("TEST")

# /control/shippings

