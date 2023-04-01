import json
import os

import requests

from unifi.settings import KNU_URL

import urllib3
urllib3.disable_warnings()  # insecure warning --> strongly advise to add TLS for unifi.


def get_all_sites():
    session = knu_auth()
    sites_url = KNU_URL + '/api/self/sites'
    response = json.loads(session.get(sites_url).text)
    res = deserialize_json(response)
    return res


def knu_auth():
    session = requests.session()
    payload = {
        "username": os.getenv("KNU_USERNAME"),
        "password": os.getenv("KNU_PASSWORD")
    }
    knu_auth_url = KNU_URL + '/api/login'
    session.post(knu_auth_url,
                 headers={
                     "Accept": "application/json",
                     "Content-Type": "application/json"
                 },
                 data=json.dumps(payload),
                 verify=False
                 )
    return session


def deserialize_json(json_to_deserialize):
    response = {
        key: json_to_deserialize[key] for key in json_to_deserialize.keys() & {"data"}
    }.get("data")
    return response
