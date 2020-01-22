from django.shortcuts import render
from apipkg import api_manager
from datetime import datetime, timedelta
import requests




def schedule_stock_reorder(request):
    clock_time = api_manager.send_request("scheduler", "clock/time")
    time = datetime.strptime(clock_time, '"%d/%m/%Y-%H:%M:%S"')
    time = time + timedelta(seconds=80)
    time_str = time.strftime('%d/%m/%Y-%H:%M:%S')
    body = {
        "target_url": "stock-reorder",
        "target_app": "gestion-commerciale",
        "time": time_str,
        "recurrence": "jour",
        "data": "{}",
        "source_app": "gestion-commerciale",
        "name": "gesco-stock-reorder"
    }
    r = schedule_task(body)
    return render(request, "index.html", {})


def schedule_get_products_from_catalogue(request):
    clock_time = api_manager.send_request("scheduler", "clock/time")
    time = datetime.strptime(clock_time, '"%d/%m/%Y-%H:%M:%S"')
    time = time + timedelta(seconds=80)
    time_str = time.strftime('%d/%m/%Y-%H:%M:%S')
    body = {
        "target_url": "get-products",
        "target_app": "gestion-commerciale",
        "time": time_str,
        "recurrence": "jour",
        "data": "{}",
        "source_app": "gestion-commerciale",
        "name": "gesco-get-product-catalogue"
    }
    r = schedule_task(body)
    return render(request, "index.html", {})


def schedule_task(body):
    headers = {"Host": "scheduler"}
    r = requests.post(api_manager.api_services_url + "schedule/add", headers=headers, json=body)
    print(r.status_code)
    print(r.text)
    return r.text