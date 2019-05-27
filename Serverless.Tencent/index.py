#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import json
import requests


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
        if not fakeurl:
            response = requests.post(url=host + '/ajaxm.php', headers=headers, data=data)
            result = json.loads(response.text)
            fakeurl = result['dom'] + '/file/' + result['url']

        headers['Accept-Language'] = 'zh-CN,zh;q=0.9'
        response = requests.get(url=fakeurl, headers=headers, data=data, allow_redirects=False)
        headers['User-Agent'] = ua[0]
        filename = get_filename(fid, host, headers)
        return {'filename': filename, 'downUrl': response.headers['Location']}
    except:
        return {'filename': '', 'downUrl': ''}


def main_handler(event, context):
    data = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*'},
        "body": json.dumps({'code': 404, 'msg': 'not found'})
    }
    try:
        url = event['queryString']['url']
        if not re.match('https://www.lanzous.com/[0-9a-z]{7,}', url):
            return data
        fid = url.split('/')[3]
    except:
        return data
    try:
        pwd = event['queryString']['pwd']
    except:
        pass
    try:
        type = event['queryString']['type']
    except:
        type = ''

    download_info = get_download_info(fid, pwd, 0)
    if download_info['downUrl'].find('development') < 0:
        download_info = get_download_info(fid, pwd, 1)
    if download_info['downUrl'].find('development') >= 0:
        if type == 'down':
            data['statusCode'] = 302
            data['headers'] = {'Location': download_info['downUrl']}
        else:
            data['body'] = json.dumps({'code': 200, 'msg': 'success',
                                       'data': {'filename': download_info['filename'],
                                                'downUrl': download_info['downUrl']}})
    return data
