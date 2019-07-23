from django.http import HttpResponse
from django.http import HttpResponseRedirect
from apipkg import api_manager as api
from application.djangoapp.models import *
from django.shortcuts import render
from .forms import UserForm
from django.http import JsonResponse
from django.core import serializers


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
    user = serializers.serialize("json", User.objects.all())
    return JsonResponse({'users' : user})


def info_catalogue_produits(request):
    context = api.send_request('catalogueproduits', 'api/info')
    return render(request, 'info_catalogue_produits.html', context)