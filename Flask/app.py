#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import requests
from flask import Flask, request, redirect, send_from_directory, jsonify, abort, make_response

app = Flask(__name__)
port = int(os.getenv('PORT', '3000'))


def get_params_from_pc_site(fid, pwd, host, headers):
    response = requests.get(url=host + '/' + fid, headers=headers)
    if pwd:
        file_name = ''
        file_size = str(
            re.findall(
                r"<div class=\"n_filesize\">大小：(.+)</div><div id=\"downajax\"></div>",
                response.text)[0])
        params = str(re.findall(r"data : '(.+)'\+pwd", response.text)[0]) + pwd
    else:
        file_size = str(re.findall(r"文件大小：</span>(.+)<br>", response.text)[0])
        file_name = str(
            re.findall(r"var filename = '(.+)';", response.text)[0])
        frame = str(
            re.findall(r"src=\"(.{10,})\" frameborder", response.text)[0])
        response = requests.get(url=host + frame, headers=headers)
        data = eval(str(re.findall(r"data : ({.+}),", response.text)[0]))
        params = ''
        for key, value in data.items():
            params += key + '=' + str(value) + '&'
        params = params[:-1]
    return {
        'params': params,
        'fileInfo': {
            'fileName': file_name,
            'fileSize': file_size
        }
    }


def get_params_from_mobile_site(fid, pwd, host, headers):
    response = requests.get(url=host + '/tp/' + fid, headers=headers)
    params = str(re.findall(r"data : \'(.*)\'\+pwd", response.text)[0])
    file_name = str(re.findall(r"<title>(.+)</title>", response.text)[0])
    file_size = str(
        re.findall(r"id=\"submit\">下载\( (.+) \)</a>", response.text)[0])
    return {
        'params': params + pwd,
        'fileInfo': {
            'fileName': file_name,
            'fileSize': file_size
        }
    }


def get_fakeurl_from_mobile_site(fid, host, headers):
    response = requests.get(url=host + '/tp/' + fid, headers=headers)
    file_name = str(re.findall(r"<title>(.+)</title>", response.text)[0])
    file_size = str(
        re.findall(r"target=\"_blank\">下载\( (.+) \)</a>", response.text)[0])
    urlp = str(re.findall(r"var url.+ = \'(.+)\'", response.text)[0])
    params = str(
        re.findall(r"submit.href = dpost \+ \"(.+)\"", response.text)[0])
    return {
        'fakeUrl': urlp + params,
        'fileInfo': {
            'fileName': file_name,
            'fileSize': file_size
        }
    }


def get_download_info(fid, pwd, type):
    host = 'https://www.lanzous.com'
    ua = {
        'pc':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
        'mobile':
        'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Mobile Safari/537.36'
    }
    headers = {
        'User-Agent': ua[type],
        'Referer': host,
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    if type == 'pc':
        params = get_params_from_pc_site(fid, pwd, host, headers)
    elif pwd:
        params = get_params_from_mobile_site(fid, pwd, host, headers)
    else:
        params = get_fakeurl_from_mobile_site(fid, host, headers)

    if params.__contains__('params'):
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        response = requests.post(url=host + '/ajaxm.php',
                                 headers=headers,
                                 data=params['params'])
        headers.pop('Content-Type')

        result = json.loads(response.text)
        if not params['fileInfo']['fileName']:
            params['fileInfo']['fileName'] = result['inf']
        fake_url = result['dom'] + '/file/' + result['url']
        response = requests.get(url=fake_url,
                                headers=headers,
                                allow_redirects=False)
    else:
        response = requests.get(url=params['fakeUrl'],
                                headers=headers,
                                allow_redirects=False)
    return {
        'fileInfo': params['fileInfo'],
        'downloadUrl': response.headers['location']
    }


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/')
def redirect_to_download_server():
    if not re.match('.+/\?url=https:%2F%2Fwww\.lanzous\.com%2F[0-9a-z]{7,}.*',
                    request.url):
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

    try:
        download_info = get_download_info(fid, pwd, 'mobile')
    except:
        download_info = get_download_info(fid, pwd, 'pc')

    if download_info['downloadUrl'].find('dev') >= 0:
        if type == 'down':
            return redirect(download_info['downloadUrl'])
        else:
            response = make_response(
                jsonify({
                    'code': 200,
                    'msg': 'success',
                    'data': download_info
                }))
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
