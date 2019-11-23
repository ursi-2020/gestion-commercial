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

from application.djangoapp.api import *
from application.djangoapp.models import *


def main():
    print("Liste des ventes:")
    for v in Vente.objects.all():
        print("ID: " + str(v.id) + "\tArticle: " + v.article.nom + "\tDate: " + str(v.date))


# Récupère les nouveaux produits
def get_new_products(products):
    for product in products:
        new_product = Product.objects.create(
            codeProduit=product["codeProduit"],
            familleProduit=product["familleProduit"],
            descriptionProduit=product["descriptionProduit"],
            quantiteMin=product["quantiteMin"],
            packaging=product["packaging"],
            prix=product["prix"],
            quantite=12
        )

        new_product.save()
    nb_products = len(products)
    print(str(nb_products) + " products were saved")

    return redirect(internalFunctions.display_products)

## Demandes de stock
# def get_stocks():
#     body = None
#     time = api_manager.send_request('scheduler', 'clock/time')
#     message = '{ "from":"' + os.environ[
#         'DJANGO_APP_NAME'] + '", "to":"gestion-commerciale", "datetime": ' + time + ', "body": ' + json.dumps(
#         body) + '}'
#     queue.send('gestion-commerciale', message)


def dispatch(ch, method, properties, body):
    print(" [x] Received from queue %r" % body)
    jsonLoad = json.loads(body)
    fromApp = jsonLoad["from"]
    functionName = ""
    if 'functionname' in jsonLoad:
        functionName = jsonLoad["functionname"]
    if fromApp == 'catalogue-produit':
        #if functionName == 'get_new_products':
        get_new_products(jsonLoad["body"]["produits"])
    elif fromApp == 'gestion-commerciale':
        if functionName == "simulate_get_new_product":
            get_new_products(jsonLoad["body"]["produits"])

    else:
        print("Le nom de l'application donné dans le json n'existe pas.")



if __name__ == '__main__':
    queue.receive('gestion-commerciale', dispatch)
    #queue.receive('gestion-commerciale', get_stocks)
    main()
