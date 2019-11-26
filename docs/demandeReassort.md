[Retour à l'index](index.md)

[Retour à la liste des use cases](userCases.md)

# Demande de réassort

Réaprovisionner le magasin

![UML](uml/réassortMagasin.png)

## Applications concernées
Magasin, Stocks

## API mises à disposition

### get_order_magasin

Récupère la commande du magasin.

JSON : 
body = 
 
    {
        "idCommande": 123, 
        "produits": [
            {
                "codeProduit": "X1664",
                "quantite": 1,
            },
            {
                "codeProduit": "X3-0",
                "quantite": 11,
            },
        ]
    }

### get_order_stock

Recoit les quantités disponibles.

JSON :
body = 

    {
        "idCommande": 123,
        "produits": [
            {
                "codeProduit": "X1664",
                "quantite": 1,
            },
            {
                "codeProduit": "X3-0",
                "quantite": 11,
            },
        ]
    }

## API utilisées 

### get_order_stock

Envoie la demande aux stocks.

JSON : 
body = 

    {
        "idCommande": 123,
        "produits": [
            {
                "codeProduit": "X1664",
                "quantite": 1,
            },
            {
                "codeProduit": "X3-0",
                "quantite": 11,
            },
        ]
    }
    
   
 

