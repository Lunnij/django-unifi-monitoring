import urllib3
import json
import time

from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from .forms import LoggerForm
from logger.models import Network
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
                await log(request, site_selector)
            else:
                while True:
                    if stop_flag:
                        break
                    start_time = time.time()
                    await log(request, site_selector)
                    elapsed_time = time.time() - start_time
                    if elapsed_time < period:
                        time.sleep(period - elapsed_time)
    else:
        form = LoggerForm()

    return render(request, 'log.html', {'form': form})


async def log(request, site):
    session = knu_auth()
    data_url = KNU_URL + f"/api/s/{site}/stat/device"

    data = json.loads(session.get(data_url, verify=False).text)
    data_json = deserialize_json(data)
    
    await test_networks_bulk(data_json)
    return HttpResponse(request)

@sync_to_async
def get_telegram_users():
    from tgbot.models import TelegramUser
    return list(TelegramUser.objects.all())


async def test_networks_bulk(networks):
    from tgbot.bot import handle_err_notify

    sites = get_all_sites()
    site_dict = {
        site['_id']: site['desc'] for site in sites
    }

    bulk = [
        Network(
            mac=network['mac'],
            network_name=site_dict.get(network.get('site_id'), 'offline'),
            ip=network['ip'],
            logged_at=timezone.now(),
            raw_data=network,
        )
        for network in networks
    ]
    await database_sync_to_async(Network.objects.bulk_create)(bulk)
    print('bulk inserted', len(bulk))

    no_ip_networks = [network for network in bulk if not network.ip]
    if no_ip_networks:
        from tgbot.bot import bot
        message = f"No IP address found for the following devices:\n"
        users = await get_telegram_users()
        for network in no_ip_networks:
            message += f"MAC address: {network.mac}\n"
            message += f"Site: {network.network_name}\n"
        for user in users:
            await handle_err_notify(chat_id=user.chat_id, message=message, bot=bot.bot)
