from django.http import HttpResponse
from django.http import HttpResponseRedirect
from apipkg import api_manager as api
from application.djangoapp.models import *
from django.shortcuts import render
from .forms import UserForm, ArticleForm
from django.http import JsonResponse
from .models import User
from django.views.decorators.csrf import csrf_exempt
import json


def index(request):
    context = {}
    return render(request, 'index.html', context)


def info(request):
    users = User.objects.all()
    context = {'users' : users}
    return render(request, 'info.html', context)


def add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect('/info')
    else:
        form = UserForm()
    return render(request, 'add_user.html', {'form' : form})


def api_info(request):
    users = list(User.objects.all().values())
    return JsonResponse({'users' : users})

@csrf_exempt
def api_add_user(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        print(body)
        new_user = User(nom=body["nom"], prenom=body["prenom"], age=body["age"])
        new_user.save()
        return HttpResponseRedirect('/info')
    return HttpResponse("OK")


def info_catalogue_produits(request):
    data = api.send_request('catalogue-produit', 'api-info')
    context = json.loads(data)
    return render(request, 'info_catalogue_produits.html', context)

def add_article_catalogue_produits(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            clean_data = form.cleaned_data
            dump = json.dumps(clean_data)
            sent = api.post_request('catalogue-produit', 'api-add-article', dump)
    else:
        form = ArticleForm()
    return render(request, 'add_article.html', {'form': form})