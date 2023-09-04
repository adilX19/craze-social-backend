import requests
from functools import partial
import re
import json
from time import sleep
import random
from datetime import datetime

def verify_cookies(username, cookies):
    username = username.lower()

    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "DNT": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "Referer": "https://www.instagram.com/"
    }
    # cookies = {
    #     'csrftoken': 'KraJPaSbf3NWmlt9yqHj0KWzRgF3TCUa',
    #     'ds_user_id': '31960392887',
    #     'ig_did': 'E7FD45E3-3408-43C7-A940-415E7DC67506',
    #     'ig_nrcb': '1',
    #     'mid': 'YoSL1gAEAAE-p0Xtlbb21fhZtaKS',
    #     'rur': 'CLN',
    #     'sessionid': '31960392887%3AQ0xHs7PQXQX6Up%3A22',
    # }

    res = requests.get(f'https://www.instagram.com/{username}/?__a=1', cookies=cookies, headers=headers)

    cookie_flag = False
    if res.status_code == 200:
        try:
            json_data = json.loads(res.text)
            insta_user_handle = json_data.get("graphql", {}).get("user", {}).get("username")
            cookie_flag = True
        except:
            insta_user_handle = ""
    return cookie_flag, insta_user_handle


def default_http_header():
    header = {
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Host': 'www.instagram.com',
        'Origin': 'https://www.instagram.com',
        'Referer': 'https://www.instagram.com/',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        'X-Instagram-AJAX': '1',
        'X-Requested-With': 'XMLHttpRequest'
    }
    return header

def get_json(session, path, params=None, host='www.instagram.com', _attempt=1):
        """Returns the CSRF Token"""
        is_graphql_query = 'query_hash' in params and 'graphql/query' in path
        resp = session.get('https://{0}/{1}'.format(host, path), params=params, allow_redirects=False)
        is_html_query = not is_graphql_query and not "__a" in params and host == "www.instagram.com"
        if is_html_query:
            match = re.search(r'window\._sharedData = (.*);</script>', resp.text)
            resp_json = json.loads(match.group(1))
            entry_data = resp_json.get('entry_data')
            post_or_profile_page = list(entry_data.values())[0] if entry_data is not None else None

            if 'graphql' not in post_or_profile_page[0]:
                match = re.search(r'window\.__additionalDataLoaded\(.*?({.*"graphql":.*})\);</script>', resp.text)
                if match is not None:
                    post_or_profile_page[0]['graphql'] = json.loads(match.group(1))['graphql']
            return resp_json
        else:
            resp_json = resp.json()
        if 'status' in resp_json and resp_json['status'] != "ok":
            if 'message' in resp_json:
                raise Exception(
                    "Returned \"{}\" status, message \"{}\".".format(resp_json['status'], resp_json['message']))
            else:
                raise Exception("Returned \"{}\" status.".format(resp_json['status']))

def verify_instagram_credentials_and_return_values(username, password):
    logged_in = False
    flag, userhandle = False, None
    cookies = {}

    session = requests.Session()

    session.cookies.update({'sessionid': '', 'mid': '', 'ig_pr': '1',
                        'ig_vw': '1920', 'ig_cb': '1', 'csrftoken': '',
                        's_network': '', 'ds_user_id': ''})

    session.headers.update(default_http_header())

    session.request = partial(session.request, timeout=300)

    csrf_json = get_json(session, 'accounts/login/', {})
    csrf_token = csrf_json['config']['csrf_token']
    session.headers.update({'X-CSRFToken': csrf_token})
    sleep(random.choice([3, 5, 6, 8, 10, 12, 11, 15]))

    enc_password = '#PWD_INSTAGRAM_BROWSER:0:{}:{}'.format(int(datetime.now().timestamp()), password)
    login = session.post('https://www.instagram.com/accounts/login/ajax/',
                        data={'enc_password': enc_password, 'username': username},
                        allow_redirects=True)

    if login.json().get("status") == "ok" and login.json().get("authenticated"):
        logged_in = True
        cookies = session.cookies.get_dict()
    else:
        print(f"Login Failed: {login.text}")

    if logged_in:
        flag, userhandle = verify_cookies(username, cookies)
    
    return flag, cookies, userhandle
 