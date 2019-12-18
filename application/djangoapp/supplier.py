import json

from apipkg import api_manager as api
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from . import internalFunctions


def supplier_order(json_order):
    print("supply_order activated")
    ouiouibaguett = {
        "commande": {
            "numeroCommande": '1',
            "dateLivraison": '2019-08-21',
            "items":  [
                {"codeProduit": 'Y2-7', "quantite": 3},
                {"codeProduit": 'Y2-7', "quantite": 3}
            ]

        }
    }

    #(code, resp) = api.post_request2('fo', 'order', json.dumps(ouiouibaguett))

    (code, resp) = api.post_request2('gestion-commerciale', 'supplier-receive', json.dumps(json_order))
    return HttpResponse(resp.text)


@csrf_exempt
def supplier_receive(request):
    print("received supplier response :")
    body = json.loads(request.body)
    body["livraison"] = 1
    internalFunctions.sendAsyncMsg("gestion-stock", body, "get_order_stocks")
    return HttpResponse(request)