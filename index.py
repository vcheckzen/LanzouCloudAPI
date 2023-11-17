import os
import re
import sys
from enum import Enum
from random import randint
from time import time
from urllib.parse import parse_qs, quote_plus, unquote, urlencode, urlparse

import requests
from cacheout import Cache
from flask import Flask, abort, jsonify, make_response, redirect, request

cache = Cache(maxsize=1024)
app = Flask(__name__)
ORIGIN = 'https://lanzoux.com'
RAND_IP = ''


class Client(Enum):
    PC = 0
    MOBILE = 1


def change_ip():
    global RAND_IP
    RAND_IP = '.'.join(str(randint(1, 254)) for _ in range(4))


def gen_headers(client: Client):
    return {
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': ORIGIN,
        'User-Agent': [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36'
        ][client.value],
        'X-Forwarded-For': RAND_IP
    }


def get(url, client: Client):
    return requests.get(url, headers=gen_headers(client), allow_redirects=False)


def post_data(url, data, client: Client):
    return requests.post(url, data, headers={
        **gen_headers(client),
        'Content-Type': 'application/x-www-form-urlencoded'
    })


def find_all(pattern, text):
    return re.finditer(pattern, text, re.MULTILINE)


def find_first(pattern, text):
    match = re.findall(pattern, text, re.MULTILINE)
    if match:
        return match[0]


def get_url(fid: str, client: Client, pwd=None):
    def get_fake_url(params):
        result = post_data(f'{ORIGIN}/ajaxm.php', params, client).json()
        return f"{result['dom']}/file/{result['url']}"

    if client == Client.PC:
        text = get(f'{ORIGIN}/{fid}', client).text
        if pwd:
            old_ver = find_first(r"^[^/]+?data *?: *?'([^']+?)'", text)
            if old_ver:
                params = old_ver + pwd
            else:
                try:
                    for m in find_all(r"^\s*?[^/]+? ([^\d\s][\$\w]+? *?= *?'.*?')", text):
                        exec(m.group(1))
                    for m in find_all(r"^[^/]+?data *?: *?({.+?})", text):
                        data = eval(m.group(1))
                        if len(data.get('sign')) > 10:
                            break
                except Exception:
                    pass
                params = urlencode(data, quote_via=quote_plus)
        else:
            fn = find_first(r'iframe.+?src=\"([^\"]{20,}?)\"', text)
            text = get(f'{ORIGIN}/{fn}',  client).text

            try:
                for m in find_all(r"^\s*?[^/]+? ([^\d\s][\$\w]+? *?= *?'.*?')", text):
                    exec(m.group(1))
            except Exception:
                pass

            data = eval(find_first(r"^[^/]+?data *?: *?({.+?})", text))
            params = urlencode(data, quote_via=quote_plus)

        fake_url = get_fake_url(params)

    else:
        if not fid.startswith('i'):
            text = get(f'{ORIGIN}/{fid}', client).text
            fid = find_first(r"[^/\n;]+? *?= *?'tp/([^']+?)'", text)

        text = get(f'{ORIGIN}/tp/{fid}', client).text
        if pwd:
            try:
                for m in find_all(r"^\s*?[^/]+? ([^\d\s][\$\w]+? *?= *?'.*?')", text):
                    exec(m.group(1))
            except Exception:
                pass

            params = eval(find_first(r"^[^/]+? *?data *?: *?({.+?})", text))
            fake_url = get_fake_url(params)
        else:
            url_pre = find_first(r"^[^/]+? *?= *?'(https?://[^']+)'", text)
            url_suf = find_first(r"^[^/]+?[$\w\s]+? *?= *?'(\?[^']+?)'", text)
            fake_url = url_pre + url_suf

    return get(fake_url, client).headers['location']


def fmt_size(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)


def get_ttl(url):
    e = parse_qs(urlparse(url).query).get('e', [time() + 600])[0]
    return int(e) - int(time()) - 60


def get_full_info(cache_key, ttl, url):
    info = cache.get(cache_key)
    if info:
        print(f'hit cache: {info}')
        return info

    headers = requests.head(url, allow_redirects=False).headers
    info = {
        'name': unquote(headers.get('Content-Disposition').split('filename=')[-1].strip()),
        'size': fmt_size(int(headers.get('Content-Length'))),
        'url': url,
    }
    cache.set(cache_key, info, ttl=ttl)
    return info


def gen_json_response(code, msg, extra={}):
    return make_response(jsonify({
        'code': code,
        'msg': msg,
        **extra
    }))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    url = request.args.get('url', '')
    fid = url.split('/')[-1]
    if not re.match(r"[\w]{4,}.*", fid):
        return gen_json_response(
            -1,
            'invalid link',
            {
                'examples': [
                    f'{request.base_url}?url={ORIGIN}/i4wk2oh&type=down',
                    f'{request.base_url}?url={ORIGIN}/i7tit9c&pwd=6svq&type=json',
                ]
            }
        )

    pwd = request.args.get('pwd')
    accept_type = request.args.get('type')
    def respond(url, ttl=None):
        if accept_type == 'down':
            return redirect(url)
        else:
            return gen_json_response(
                200,
                'success',
                {'data': get_full_info(f'{fid}/{pwd}/info', ttl, url)}
            )

    cache_key = f'{fid}/{pwd}/url'
    url = cache.get(cache_key)
    if url:
        print(f'hit cache: {url}')
        return respond(url)

    change_ip()
    errors = []
    for client in Client:
        try:
            url = get_url(fid, client, pwd)
            # https://rollbar.com/blog/throwing-exceptions-in-python/
            # assert (url.startswith('1http')), f'Parse Error: fid: {fid}, client: {client}, pwd: {pwd}, url: {url}'

            ttl = get_ttl(url)
            cache.set(cache_key, url, ttl=ttl)
            return respond(url, ttl)
        except Exception as e:
            errors.append(e)
            pass

    abort(500, errors)


@app.errorhandler(Exception)
def server_error(e):
    return gen_json_response(
        -2,
        f'Link does not match pwd, or LanZouCloud has changed their webpage. Errors: {e}'
    )


@app.after_request
def cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


def test():
    def request(fid, client: Client, pwd=None):
        print(f'fid={fid}, client={client}, pwd={pwd}')
        print(get_url(fid, client, pwd))
        print('--------------------------------------')

    for fid, pwd in {
        'i5nuK1lijzmh': '9oy8',
        'iDuWS1iy0s0h': None,
        'i7tit9c': '6svq',
        'i4wk2oh': None,
        'iRujgdfrkza': None,
        'dkbdv7': None,
    }.items():
        for c in Client:
            request(fid, c, pwd)


if __name__ == '__main__':
    port = int(os.getenv('PORT', '3000'))
    if len(sys.argv) <= 1 or sys.argv[1] != 'production':
        test()
        app.config['JSON_AS_ASCII'] = False
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.run(host='127.0.0.1', port=port)
