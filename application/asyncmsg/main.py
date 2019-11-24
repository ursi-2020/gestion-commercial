import sys
import os
import json
from django.shortcuts import redirect
from apipkg import api_manager


from apipkg import queue_manager as queue
sys.dont_write_bytecode = True

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from application.djangoapp import api
from application.djangoapp import simulate
from application.djangoapp.models import *


def main():
    print("Liste des ventes:")
    for v in Vente.objects.all():
        print("ID: " + str(v.id) + "\tArticle: " + v.article.nom + "\tDate: " + str(v.date))





def dispatch(ch, method, properties, body):
    print(" [x] Received from queue %r" % body)
    jsonLoad = json.loads(body)
    fromApp = jsonLoad["from"]
    functionName = ""
    if 'functionname' in jsonLoad:
        functionName = jsonLoad["functionname"]

    if fromApp == 'catalogue-produit':
        #if functionName == 'get_new_products':
        api.get_new_products(jsonLoad)

    elif fromApp == 'gestion-stock':
        if functionName == 'get_stock':
            api.get_stocks(jsonLoad)
        elif functionName == "get_stock_order_response":
            api.get_stock_order_response(jsonLoad)

    elif fromApp == 'gestion-magasin':
        # if functionName == 'get_order_magasin
        api.get_order_magasin(jsonLoad)

    elif fromApp == 'gestion-commerciale':
        if functionName == "get_new_products":
            api.get_new_products(jsonLoad)
        elif functionName == "get_stocks":
            api.get_stocks(jsonLoad)
        elif functionName == "get_order_magasin":
            api.get_order_magasin(jsonLoad, simulate=True)
        elif functionName == "simulate_get_order_stocks":
            simulate.simulate_get_order_stocks(jsonLoad)
        elif functionName == "get_stock_order_response":
            api.get_stock_order_response(jsonLoad, simulate=True)
        elif functionName =="simulate_magasin_get_order_response":
            print("Magasin receive response")
        else:
            print("Le nom de la fonction dans le json n est pas valide")

    else:
        print("Le nom de l application du json n est pas valide")



if __name__ == '__main__':
    queue.receive('gestion-commerciale', dispatch)
    main()
