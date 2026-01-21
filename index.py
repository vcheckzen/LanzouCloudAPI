import os
import re
import sys
from enum import Enum
from random import randint
from urllib.parse import quote_plus, unquote, urlencode

import requests
from cacheout import Cache
from flask import Flask, abort, jsonify, make_response, redirect, request

cache = Cache(maxsize=1024)
app = Flask(__name__)
ORIGIN = "https://lanzoux.com"
RAND_IP = ""


class Client(Enum):
    PC = 0
    MOBILE = 1


def change_ip():
    global RAND_IP
    RAND_IP = ".".join(str(randint(1, 254)) for _ in range(4))


def gen_headers(client: Client):
    return {
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": ORIGIN,
        "User-Agent": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36",
        ][client.value],
        "X-Forwarded-For": RAND_IP,
    }


def head(url, client: Client):
    return requests.head(url, headers=gen_headers(client), allow_redirects=False)


def get(url, client: Client):
    return requests.get(url, headers=gen_headers(client), allow_redirects=False)


def post_data(url, data, client: Client):
    return requests.post(
        url,
        data,
        headers={
            **gen_headers(client),
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )


def find_all(pattern, text):
    return re.finditer(pattern, text, re.DOTALL | re.MULTILINE)


def find_first(pattern, text):
    match = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
    if match:
        return match[0]


def _oO0OO0O(OO0O0O0O):
    import re as _0x1

    def _0x2(_0x3):
        def _0x4(_0x5):
            _0x10 = ""
            for _0x6 in _0x5:
                _0x10 += chr(_0x6)
            return _0x10

        _0x11 = [40, 39, 40, 63, 58, 92, 92, 46, 124, 91, 94, 39, 92, 92, 93, 41, 42, 39, 124, 34, 40, 63, 58, 92, 92, 46, 124, 91, 94, 34, 92, 92, 93, 41, 42, 34, 41]
        _0x7 = _0x4(_0x11)

        _0x8 = []
        _0x12 = 0

        def _0x9(_0xa):
            nonlocal _0x12
            _0x8.append(_0xa.group(0))
            _0x13 = f"__{RAND_IP}_%d__" % _0x12
            _0x12 += 1
            return _0x13

        _0xb = _0x1.sub(_0x7, _0x9, _0x3, flags=_0x1.VERBOSE | _0x1.DOTALL)
        _0x14 = [47, 47, 46, 42, 63, 36, 124, 47, 92, 42, 46, 42, 63, 92, 42, 47]
        _0xc = _0x4(_0x14)
        _0xd = _0x1.sub(_0xc, "", _0xb, flags=_0x1.MULTILINE | _0x1.DOTALL)

        _0x15 = 0
        while _0x15 < len(_0x8):
            _0xf = _0x8[_0x15]
            _0xd = _0xd.replace(f"__{RAND_IP}_%d__" % _0x15, _0xf)
            _0x15 += 1
        return _0xd

    return _0x2(OO0O0O0O)


def get_url(fid: str, client: Client, pwd=None):
    def get_fake_url(text, params):
        m_url = find_first(r"^\s*?[^/]+?{.*?url\s*?:\s*['\"](.*?php.*?)'", text)
        result = post_data(f"{ORIGIN}/{m_url}", params, client).json()
        return f"{result['dom']}/file/{result['url']}"

    if client == Client.PC:
        text = _oO0OO0O(get(f"{ORIGIN}/{fid}", client).text)
        if pwd:
            old_ver = find_first(r"^\s*?[^/]+?data *?: *?'([^']+?)'", text)
            if old_ver:
                params = old_ver + pwd
            else:
                for m in find_all(r"^\s*?[^/]+? ([^\d\s][\$\w]+? *?=.+?);", text):
                    try:
                        exec(m.group(1))
                    except Exception:
                        pass
                for m in find_all(r"^\s*?[^/]+?data *?: *?({.+?})", text):
                    try:
                        data = eval(m.group(1))
                        if len(data.get("sign")) > 10:
                            break
                    except Exception:
                        pass
                params = urlencode(data, quote_via=quote_plus)
        else:
            fn = find_first(r"iframe.+?src=\"([^\"]{20,}?)\"", text)
            text = _oO0OO0O(get(f"{ORIGIN}/{fn}", client).text)

            for m in find_all(r"^\s*?[^/]+? ([^\d\s][\$\w]+? *?=.+?);", text):
                try:
                    exec(m.group(1))
                except Exception:
                    pass
            data = eval(find_first(r"^\s*?[^/]+?data *?: *?({.+?})", text))
            params = urlencode(data, quote_via=quote_plus)
        fake_url = get_fake_url(text, params)
    else:
        text = _oO0OO0O(get(f"{ORIGIN}/{fid}", client).text)
        fid_with_params = find_first(r"[^/\n;]+? *?= *?['\"]/?tp/([^'\"]+?)['\"]", text)
        text = _oO0OO0O(get(f"{ORIGIN}/tp/{fid_with_params}", client).text)
        if pwd:
            for m in find_all(r"^\s*?[^/]+? ([^\d\s][\$\w]+? *?=.+?);", text):
                try:
                    exec(m.group(1))
                except Exception:
                    pass
            params = eval(find_first(r"^\s*?[^/]+? *?data *?: *?({.+?})", text))
            fake_url = get_fake_url(text, params)
        else:
            url_pre = find_first(r"^\s*?[^/]+? *?= *?'(https?://[^']+?)'", text)
            url_suf = find_first(r"^\s*?[^/]+?[$\w\s]+? *?= *?'(\?[^']+?)'", text)
            fake_url = url_pre + url_suf
    return get(fake_url, client).headers["location"]


def fmt_size(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Y", suffix)


def get_ttl(_url):
    return 600


def extract_filename(content_disposition):
    # match: filename*

    m = re.search(r"filename\*\s*=\s*UTF-8''([^;]+)", content_disposition, re.I)
    if m:
        return unquote(m.group(1))
    # fallback：filename=

    m = re.search(r'filename\s*=\s*"([^"]+)"', content_disposition, re.I)
    if m:
        return m.group(1)
    return None


def get_full_info(cache_key, ttl, url):
    info = cache.get(cache_key)
    if info:
        print(f"hit cache: {info}")
        return info
    headers = head(url, client=Client.MOBILE).headers
    info = {
        "name": extract_filename(headers.get("Content-Disposition", "")),
        "size": fmt_size(int(headers.get("Content-Length", 0))),
        "url": url,
    }
    cache.set(cache_key, info, ttl=ttl)
    return info


def gen_json_response(code, msg, extra={}):
    return make_response(jsonify({"code": code, "msg": msg, **extra}))


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    url = request.args.get("url", "")
    fid = url.split("/")[-1]
    if not re.match(r"[\w]{4,}.*?", fid):
        return gen_json_response(
            -1,
            "invalid link",
            {
                "examples": [
                    f"{request.base_url}?url={ORIGIN}/i0gZ322ututi&type=down",
                    f"{request.base_url}?url={ORIGIN}/iDuSh22faxqj&pwd=6q1d&type=json",
                ]
            },
        )
    pwd = request.args.get("pwd")
    accept_type = request.args.get("type")

    def respond(url, ttl=None):
        if accept_type == "down":
            return redirect(url)
        else:
            return gen_json_response(
                200, "success", {"data": get_full_info(f"{fid}/{pwd}/info", ttl, url)}
            )

    cache_key = f"{fid}/{pwd}/url"
    url = cache.get(cache_key)
    if url:
        print(f"hit cache: {url}")
        return respond(url)
    
    change_ip()
    errors = []
    for client in Client:
        try:
            url = get_url(fid, client, pwd)
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
        f"Link does not match pwd, or LanZouCloud has changed their webpage. Errors: {e}",
    )


@app.after_request
def cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


def test():
    def request(fid, client: Client, pwd=None):
        print(f"fid={fid}, client={client}, pwd={pwd}")
        print(get_url(fid, client, pwd))
        print("--------------------------------------")

    for fid, pwd in {
        "iDuSh22faxqj": "6q1d",
        "i0gZ322ututi": None,
        "iRujgdfrkza": None,
        "iCXIww56qpe": None,
        "dkbdv7": None,
    }.items():
        for c in Client:
            request(fid, c, pwd)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    if len(sys.argv) <= 1 or sys.argv[1] != "production":
        test()
        app.config["JSON_AS_ASCII"] = False
        app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
    app.run(host="127.0.0.1", port=port)
