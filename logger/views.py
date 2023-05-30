import urllib3
import json
import time
from channels.db import database_sync_to_async

from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from .forms import LoggerForm

from unifi.shared import knu_auth, get_all_sites
from unifi.settings import KNU_URL

from asgiref.sync import sync_to_async

from .models import Device

urllib3.disable_warnings()  # insecure warning --> strongly advise to add TLS for unifi.
stop_flag = False


def stop_log(request):
    global stop_flag
    stop_flag = True
    return HttpResponse(request)


async def index(request):
    global stop_flag
    stop_flag = False

    if request.method == 'POST':
        form = LoggerForm(request.POST)
        if form.is_valid():
            site_selector = form.cleaned_data['site_selector']
            period = int(form.cleaned_data['period_selector'])
            if period <= 0:
                if site_selector == 'ALL':
                    await log_all(request)
                await log(request, site_selector)
            else:
                while True:
                    if stop_flag:
                        break
                    start_time = time.time()
                    if site_selector == 'ALL':
                        await log_all(request)
                    else:
                        await log(request, site_selector)
                    elapsed_time = time.time() - start_time
                    if elapsed_time < period:
                        time.sleep(period - elapsed_time)
    else:
        form = LoggerForm()

    return render(request, 'log.html', {'form': form})


async def log(request, site):
    session = knu_auth()
    data_url = KNU_URL + f"/v2/api/site/{site}/clients/active?includeTrafficUsage=true"

    data = json.loads(session.get(data_url, verify=False).text)

    await networks_bulk(data)
    return HttpResponse(request)


async def log_all(request):
    all_sites = get_all_sites()
    for site in all_sites:
        await log(request, site['name'])


async def networks_bulk(networks):
    from tgbot.bot import send_message_tg
    ip_not_found = []

    sites = get_all_sites()
    site_dict = {
        site['_id']: site['desc'] for site in sites
    }

    bulk = []
    for network in networks:
        if network.get('type') == 'WIRED' or network.get('is_wired' == True):
            # Skip saving in the database for WIRED devices
            continue
        ip = network.get('ip', '')
        if (ip == '' or None) and network['uptime'] > 120:
            ip_not_found.append(network)

        device = Device(
            mac=network.get('mac'),
            site_id=site_dict.get(network['site_id']),
            ip=ip,
            logged_at=timezone.now(),
            uptime=network['uptime'],
        )
        bulk.append(device)

    print('Bulk inserted:', len(bulk))
    if bulk:
        await database_sync_to_async(Device.objects.bulk_create)(bulk)

    if ip_not_found:
        message = "No IP address found for the following devices:\n\n"
        for device in ip_not_found:
            site_id = device.get('site_id', '-')
            mac = device.get('mac', '-')
            ip = device.get('ip', '-')
            uptime = device.get('uptime', '-')
            message += f"Site ID: {site_id}\nMAC: {mac}\nIP: {ip}\nUptime: {uptime} seconds\n\n"
        await send_message_tg(message)
