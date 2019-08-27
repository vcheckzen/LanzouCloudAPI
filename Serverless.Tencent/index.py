#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import json
import requests


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


def main_handler(event, context):
    data = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json; charset=utf-8",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "code": 404,
            "msg": "not found"
        })
    }
    try:
        url = event['queryString']['url']
        if not re.match('https://www.lanzous.com/[0-9a-z]{7,}', url):
            return data
        fid = url.split('/')[3]
    except:
        return data

    try:
        type = event['queryString']['type']
    except:
        type = ''

    try:
        pwd = event['queryString']['pwd']
    except:
        pwd = ''

    try:
        download_info = get_download_info(fid, pwd, 'mobile')
    except:
        download_info = get_download_info(fid, pwd, 'pc')

    if download_info['downloadUrl'].find('dev') >= 0:
        if type == 'down':
            data['statusCode'] = 302
            data['headers'] = {'Location': download_info['downloadUrl']}
        else:
            data['body'] = json.dumps({
                'code': 200,
                'msg': 'success',
                'data': download_info
            })
    return data


# event = {'queryString': {'url': 'https://www.lanzous.com/i5tb0vg'}}
# print(main_handler(event, None))

# event = {
#     'queryString': {
#         'url': 'https://www.lanzous.com/i44mvof',
#         'pwd': 'btrs'
#     }
# }
# print(main_handler(event, None))

# downloadinfo = get_download_info('i44mvof', 'btrs', 'mobile')
# print(downloadinfo)

# downloadinfo = get_download_info('i44mvof', 'btrs', 'pc')
# print(downloadinfo)

# downloadinfo = get_download_info('i5tb0vg', '', 'mobile')
# print(downloadinfo)

# downloadinfo = get_download_info('i5tb0vg', '', 'pc')
# print(json.dumps(downloadinfo))