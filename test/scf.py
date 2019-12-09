#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
from ..index import main_handler
from ..main.util import split_url
from ..main.api import ciba, proxy, dnspod, wxstep, lanzous, cloudmusic, aes, qr, fodi


def request(url, body=None):
    """模拟 SCF 调用 main_handler
    """
    url_splited = split_url(url)
    event = {
        'headers': {
            'host': 'www.api.com'
        },
        'requestContext': {
            'path': '/pyscf',
            'stage': 'release'
        },
        'path': url_splited['path'],
        'queryString': url_splited['params'],
        'body': body
    }
    print('https://' + event['headers']['host'] +
          '/' + event['requestContext']['stage'] + url)
    print('body:', body)
    print(main_handler(event, None))
    print('--------------------------------')
