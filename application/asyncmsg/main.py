import sys
import os

from django.shortcuts import redirect

import json


#from application.djangoapp import views


from apipkg import queue_manager as queue
sys.dont_write_bytecode = True

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from application.djangoapp.views import *

from application.djangoapp.models import *


def main():
    print("Liste des ventes:")
    for v in Vente.objects.all():
        print("ID: " + str(v.id) + "\tArticle: " + v.article.nom + "\tDate: " + str(v.date))


def callback(ch, method, properties, body):
    print(" [x] Received from queue %r" % body)

    products = json.loads(body)["body"]["produits"]
    print(json.dumps(products))
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

    return redirect(display_products)



#def config_callbacks():
    #callback(body="TEST")
    #queue.receive('gestion-commerciale', djangoapp.views.get_new_products)


if __name__ == '__main__':
    #config_callbacks()
    queue.receive('gestion-commerciale', callback)
    main()
