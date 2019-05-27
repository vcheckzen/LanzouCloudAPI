#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import json
import urlparse
import requests
from flask_cors import CORS
from flask import Flask, request, redirect, send_from_directory, jsonify, abort

app = Flask(__name__)
CORS(app)
port = int(os.getenv('PORT', '3000'))


def get_filename(fid, host, headers):
    try:
        response = requests.get(url=host + '/' + fid, headers=headers)
        filename = str(re.findall(r"filename = '(.+)'", response.text)[0])
        return filename
    except:
        return ''


def get_para_simulate_pc(fid, pwd, host, headers):
    try:
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
    except:
        return


def get_link_simulate_phone(fid, host, headers):
    try:
        response = requests.get(url=host + '/tp/' + fid, headers=headers)
        urlp = str(re.findall(r"urlp = \'(.*)\'", response.text)[0])
        para = str(re.findall(r"urlp \+ \'(.*)\'", response.text)[0])
        return urlp + para
    except:
        return


def get_para_simulate_phone(fid, pwd, host, headers):
    try:
        response = requests.get(url=host + '/tp/' + fid, headers=headers)
        para = str(re.findall(r"data : \'(.*)\'\+pwd", response.text)[0])
        data = {}
        for item in para.split('&'):
            tmp = item.split('=')
            data[tmp[0]] = tmp[1]
        data['p'] = pwd
        return data
    except:
        return


def get_download_info(fid, pwd, type):
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
        fakeurl = get_link_simulate_phone(fid, host, headers)

    try:
        if 'fakeurl' not in dir() or not fakeurl:
            response = requests.post(url=host + '/ajaxm.php', headers=headers, data=data)
            result = json.loads(response.text)
            fakeurl = result['dom'] + '/file/' + result['url']

        headers['Accept-Language'] = 'zh-CN,zh;q=0.9'
        response = requests.get(url=fakeurl, headers=headers, data=data, allow_redirects=False)
        headers['User-Agent'] = ua[0]
        filename = get_filename(fid, host, headers)
        return {'filename': filename, 'downUrl': response.headers['Location']}
    except:
        return ''


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/')
def redirect_to_download_server():
    if not re.match('.+/\?url=https:%2F%2Fwww\.lanzous\.com%2F[0-9a-z]{7,}.*', request.url):
        abort(404)

    url = request.args.get('url')
    pwd = request.args.get('pwd')
    type = request.args.get('type')

    fid = url.split('/')[3]
    download_info = get_download_info(fid, pwd, 0)
    if download_info['downUrl'].find('development') < 0:
        download_info = get_download_info(fid, pwd, 1)

    if download_info['downUrl'].find('development') >= 0:
        if type == 'down':
            return redirect(download_info['downUrl'])
        else:
            return jsonify({'code': '200', 'msg': 'success',
                            'data': {'filename': download_info['filename'], 'downUrl': download_info['downUrl']}})

    abort(404)


@app.errorhandler(404)
@app.errorhandler(500)
def handle_invalid_usage(error):
    return jsonify({'code': '404', 'msg': 'not found'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
