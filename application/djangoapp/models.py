from django.db import models


class Article(models.Model):
    nom = models.CharField(max_length=200)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return 'Article: {}'.format(self.nom)


class Vente(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    date = models.DateTimeField()

    def __str__(self):
        return 'Vente: {} - {}'.format(self.article.nom, self.date)


class User(models.Model):
    nom = models.CharField(max_length=200)
    prenom = models.CharField(max_length=200)
    age = models.PositiveIntegerField()

    def __str__(self):
        return 'User: {}'.format(self.nom)


class Log(models.Model):
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=80)
    body = models.TextField()
    time = models.DateTimeField()


class DeliveryRequest(models.Model):
    identifiantBon = models.CharField(max_length=200)
    codeProduit = models.CharField(max_length=200)
    quantiteDemandee = models.PositiveIntegerField()
    quantiteLivree = models.PositiveIntegerField()


class StockReorder(models.Model):
    identifiantBon = models.CharField(max_length=200)
    dateLivraison = models.CharField(max_length=200)
    codeProduit = models.PositiveIntegerField()
    quantiteAvant = models.PositiveIntegerField()
    quantiteLivree = models.PositiveIntegerField()


class Product(models.Model):
    codeProduit = models.CharField(max_length=200)
    familleProduit = models.CharField(max_length=200)
    descriptionProduit = models.CharField(max_length=200)
    quantiteMin = models.PositiveIntegerField()
    packaging = models.PositiveIntegerField()
    prix = models.PositiveIntegerField()

    def __str__(self):
        return "{\"codeProduit\":{}, \"familleProduit\":{}, \"descriptionProduit\":{},\"quantiteMin\":{}, \"packaging\":{}, \"prix\":{}}".format(
            self.codeProduit, self.familleProduit, self.descriptionProduit, self.quantiteMin, self.packaging, self.prix)
