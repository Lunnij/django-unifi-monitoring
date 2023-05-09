import urllib3
import json
import time

from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from .forms import LoggerForm
from logger.models import Device
from unifi.shared import knu_auth, deserialize_json, get_all_sites
from unifi.settings import KNU_URL

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async


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


async def log_all(request):
    all_sites = get_all_sites()
    for site in all_sites:
        await log(request, site['name'])


async def log(request, site):
    session = knu_auth()
    data_url = KNU_URL + f"/v2/api/site/{site}/clients/active?includeTrafficUsage=true"

    data = json.loads(session.get(data_url, verify=False).text)

    await networks_bulk(data)
    return HttpResponse(request)

@sync_to_async
def get_telegram_users():
    from tgbot.models import TelegramUser
    return list(TelegramUser.objects.all())


async def send_message_tg(message):
    from tgbot.bot import bot, handle_err_notify
    users = await get_telegram_users()
    for user in users:
        await handle_err_notify(chat_id=user.chat_id, message=message, bot=bot.bot)


async def networks_bulk(networks):
    ip_not_found = []

    sites = get_all_sites()
    site_dict = {
        site['_id']: site['desc'] for site in sites
    }

    bulk = [
        Device(
            mac=network.get('mac'),
            site_id=site_dict.get(network['site_id']),
            ip=network.get('ip', ''),
            logged_at=timezone.now(),
            uptime=network['uptime'],
        )
        for network in networks
    ]
    await database_sync_to_async(Device.objects.bulk_create)(bulk)
    print('bulk inserted', len(bulk))

    for device in networks:
        if (device.get('ip', '') == '' or None) and device['uptime'] > 120:
            ip_not_found.append(device)

    if ip_not_found:
        message = "No IP address found for the following devices: \n\n"
        for device in ip_not_found:
            site_id = site_dict.get(device['site_id'])
            mac = device.get('mac', '-')
            ip = device.get('ip', '-')
            uptime = device.get('uptime', '-')
            message += f"Site ID: {site_id}\nMAC: {mac}\nIP: {ip}\nUptime: {uptime} seconds\n\n"
        await send_message_tg(message)
