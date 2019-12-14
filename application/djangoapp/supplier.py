import json

from apipkg import api_manager as api
from django.http import HttpResponse


def supplier_order(request):
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

    (code, resp) = api.post_request2('fo', 'order', json.dumps(ouiouibaguett))
    print(code)
    print(resp)
    return HttpResponse(resp.text)
