#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import requests
from flask import Flask, request, redirect, send_from_directory, jsonify, abort, make_response

app = Flask(__name__)
port = int(os.getenv('PORT', '3000'))


def get_fileinfo(fid, host, headers):
    try:
        response = requests.get(url=host + '/' + fid, headers=headers)
        filename = str(re.findall(r"<title>(.+) -", response.text)[0])
        filesize = str(re.findall(r"<span class=\".+\">\( (.+) \)</span>", response.text)[0])
        return {'filename': filename, 'filesize': filesize}
    except:
        return {'filename': '', 'filesize': ''}


def get_para_simulate_pc(fid, pwd, host, headers):
    try:
        response = requests.get(url=host + '/' + fid, headers=headers)
        frame = str(re.findall(r"src=\"(.*)\" frameborder", response.text)[0])
        response = requests.get(url=host + frame, headers=headers)
        return eval(str(re.findall(r"data : ({.+}),", response.text)[0]))
    except:
        return None


def get_link_simulate_phone(fid, host, headers):
    try:
        response = requests.get(url=host + '/tp/' + fid, headers=headers)
        urlp = str(re.findall(r"var url.+ = \'(.+)\'", response.text)[0])
        para = str(re.findall(r"= url.+ \+ \"(.+)\"", response.text)[0])
        return urlp + para
    except:
        return None


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
        return None


def get_download_info(fid, pwd, type):
    host = 'https://www.lanzous.com'
    ua = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Mobile Safari/537.36'
    ]
    headers = {
        'User-Agent': ua[type],
        'Referer': host,
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    if type == 0:
        data = get_para_simulate_pc(fid, pwd, host, headers)
    elif pwd:
        data = get_para_simulate_phone(fid, pwd, host, headers)
    else:
        fakeurl = get_link_simulate_phone(fid, host, headers)

    try:
        headers['User-Agent'] = ua[1]
        if 'data' in dir():
            response = requests.post(url=host + '/ajaxm.php', headers=headers, data=data)
            result = json.loads(response.text)
            fakeurl = result['dom'] + '/file/' + result['url']
            response = requests.get(url=fakeurl, headers=headers, data=data, allow_redirects=False)
        elif fakeurl is not None:
            response = requests.get(url=fakeurl, headers=headers, allow_redirects=False)
        if response.headers['Location']:
            fileinfo = get_fileinfo(fid, host, headers)
        return {**fileinfo, 'downUrl': response.headers['Location']}
    except:
        return {'filename': '', 'filesize': '', 'downUrl': ''}


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/')
def redirect_to_download_server():
    if not re.match('.+/\?url=https:%2F%2Fwww\.lanzous\.com%2F[0-9a-z]{7,}.*', request.url):
        abort(404)

    url = request.args.get('url')
    try:
        pwd = request.args.get('pwd')
    except:
        pwd = ''
    try:
        type = request.args.get('type')
    except:
        type = ''

    fid = url.split('/')[3]
    download_info = get_download_info(fid, pwd, 1)
    if download_info['downUrl'].find('development') < 0:
        download_info = get_download_info(fid, pwd, 0)

    if download_info['downUrl'].find('development') >= 0:
        if type == 'down':
            return redirect(download_info['downUrl'])
        else:
            response = make_response(jsonify({'code': 200, 'msg': 'success',
                                              'data': download_info}))
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response

    abort(404)


@app.errorhandler(404)
@app.errorhandler(500)
def handle_invalid_usage(error):
    response = make_response(jsonify({'code': 404, 'msg': 'not found'}))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
