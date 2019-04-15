#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import json
import requests
from flask import Flask, request, redirect, send_from_directory, jsonify

app = Flask(__name__)
port = int(os.getenv('PORT', '3000'))


def get_para_simulate_pc(fid, pwd, host, headers):
    response = requests.get(url=host + '/' + fid, headers=headers)
    frame = str(re.findall(r"src=\"(.*)\" frameborder", response.text)[0])

    response = requests.get(url=host + frame, headers=headers)
    file_id = str(re.findall(r"\'(.{7})\'", response.text)[0])
    t = str(re.findall(r"\'(.{10})\'", response.text)[0])
    k = str(re.findall(r"\'(.{32})\'", response.text)[0])

    return {
        'action': 'down_process',
        'file_id': file_id,
        't': t,
        'k': k,
        'p': pwd,
        'c': ''
    }


def get_link_simulate_phone(fid, host, headers):
    response = requests.get(url=host + '/tp/' + fid, headers=headers)
    urlp = str(re.findall(r"urlp = \'(.*)\'", response.text)[0])
    para = str(re.findall(r"urlp \+ \'(.*)\'", response.text)[0])

    return urlp + para


def get_para_simulate_phone(fid, pwd, host, headers):
    response = requests.get(url=host + '/tp/' + fid, headers=headers)
    para = str(re.findall(r"data : \'(.*)\'\+pwd", response.text)[0])
    data = {}
    for item in para.split('&'):
        tmp = item.split('=')
        data[tmp[0]] = tmp[1]
    data['p'] = pwd

    return data


def get_direct_link(fid, pwd, type):
    host = 'https://www.lanzous.com'
    ua = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Mobile Safari/537.36'
    ]
    headers = {
        'User-Agent': ua[type],
        'Referer': host
    }

    if type == 0:
        data = get_para_simulate_pc(fid, pwd, host, headers)
    elif pwd:
        data = get_para_simulate_phone(fid, pwd, host, headers)
    else:
        return get_link_simulate_phone(fid, host, headers)

    response = requests.post(url=host + '/ajaxm.php', headers=headers, data=data)
    result = json.loads(response.text)
    link = result['dom'] + '/file/' + result['url']

    return link


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/')
def redirect_to_download_server():
    url = request.args.get('url')
    pwd = request.args.get('pwd')

    if not re.match('^https://www\.lanzous\.com/[0-9a-z]{7,}$', url):
        return jsonify({'errno': '1', 'msg': 'not found'})

    fid = url.split('/')[3]
    link = get_direct_link(fid, pwd, 1)
    if link.find('baidupan.com') < 0:
        link = get_direct_link(fid, pwd, 0)

    return redirect(link)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
