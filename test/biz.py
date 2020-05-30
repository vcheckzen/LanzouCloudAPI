#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from .scf import request


def aes():
    request('/aes/')
    request('/aes/?method=encrypta&key=1234567890123456&data=1379628076')
    request('/aes/?method=encrypt&key=12345678&data=1379628076')
    request('/aes/?method=encrypt&key=1234567890123456&data=1379628076')
    request('/aes/?method=decrypt&key=1234567890123456&data=roLzT3GBhVQw22WrUPAdsw==')


def cb():
    request('/ciba/')


def cm():
    request('/cloudmusic/')
    request('/cloudmusic/?id=514761281')
    request('/cloudmusic/?ids=1379628076,38592976,409654891,1345848098,514761281,326738')
    request('/cloudmusic/?playlist=552606452')
    request('/cloudmusic/?playlist=3645157')


def dp():
    request('/dnspod/')
    request('/dnspod/?subDomain=@')
    request('/dnspod/?domain=logi.ml')
    request('/dnspod/?domain=logi.ml&subDomain=@')


def lz():
    request('/lanzous/')
    request('/lanzous/?url=https://www.lanzous.com/i871yaf')
    request('/lanzous/?url=https://www.lanzous.com/i5tb0vg')
    request('/lanzous/?url=https://www.lanzous.com/i19pnjc&pwd=1pud&type=down')


def px():
    request('/proxy/')
    request('/proxy/?url=http://baidu.com')
    request('/proxy/?url=http://google.com')


def qr():
    request('/qr/')
    request('/qr/?method=encode&text=https://logi.ml')
    request('/qr/?method=encode&text=https://logi.ml&size=12&border=2')


def wx():
    request('/wxstep/')
    request('/wxstep/?id=e')
    request('/wxstep/?step=a')
    request('/wxstep/?id=pknhtfxsw&step=2341')


def fodi():
    request('/fodi/?accessToken')
    request('/fodi/?file=/Android/Devices/Firmware-Flash-Tool/QPST_2.7.474.7z')
    NEW_ACCESS_TOKEN = {"code": 0, "msg": "success", "encrypted": "x7hV8WISj2SOg%2BVQpdzV4wTrxPmgAv%2FeN4IQk25R23Y%3D", "plain": "LCJub25jZSI6IkVDUll1NG9RdnViSVplR0MzQ1ROZ0hWM0N5bkI4S2pqdzkydlpHSHBTNWsiLCJhbGciOiJSUzI1NiIsIng1dCI6IkN0VHVoTUptRDVNN0RMZHpEMnYyeDNRS1NSWSIsImtpZCI6IkN0VHVoTUptRDVNN0RMZHpEMnYyeDNRS1NSWSJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8xNDY3ZDZhOS1hZjc0LTRmNDUtOGE2NC1jYzg3NzU2Nzg1MWUvIiwiaWF0IjoxNTkwODQ3NDA5LCJuYmYiOjE1OTA4NDc0MDksImV4cCI6MTU5MDg1MTMwOSwiYWNjdCI6MCwiYWNyIjoiMSIsImFpbyI6IjQyZGdZTWdNWGgzbi84NjFXeUkrYS9YM0Q2ME5UWnF5RlVrLy9oeFl3Rzc2MWtuaHpYSUEiLCJhbXIiOlsicHdkIl0sImFwcF9kaXNwbGF5bmFtZSI6Im9uZV9zY2YiLCJhcHBpZCI6IjRkYTNlN2YyLWJmNmQtNDY3Yy1hYWYwLTU3ODA3OGYwYmY3YyIsImFwcGlkYWNyIjoiMSIsImlwYWRkciI6IjEyMC4yMjkuMjQuMTEzIiwibmFtZSI6IjEwMjQxOSIsIm9pZCI6ImViNGFmYWQzLTRmNjAtNGZjOS1iNDU5LTdhMDEyZDYzOTI1ZSIsInBsYXRmIjoiMyIsInB1aWQiOiIxMDAzM0ZGRjk0RjY3NjczIiwic2NwIjoiRmlsZXMuUmVhZFdyaXRlLkFsbCBwcm9maWxlIG9wZW5pZCBlbWFpbCIsInNpZ25pbl9zdGF0ZSI6WyJrbXNpIl0sInN1YiI6IlZPNjhiWV9GY1FzTVlYTndWcXlIX3ZjYTUtejhpTjVpU3pRbUFXSFBndW8iLCJ0ZW5hbnRfcmVnaW9uX3Njb3BlIjoiT0MiLCJ0aWQiOiIxNDY3ZDZhOS1hZjc0LTRmNDUtOGE2NC1jYzg3NzU2Nzg1MWUiLCJ1bmlxdWVfbmFtZSI6IjEwMjQxOUBvbm1pY3Jvc29mdC5uZXQiLCJ1cG4iOiIxMDI0MTlAb25taWNyb3NvZnQubmV0IiwidXRpIjoiS0JCbHY3SnJMMENCWXVfM3dMdFZBQSIsInZlciI6IjEuMCIsInhtc19zdCI6eyJzdWIiOiJ3THlFczZhVEZSVFpHek9aLVR6a1R6WlJJY2ZhazNtZzlORkJQYTZLalZvIn0sInhtc190Y2R0IjoxNDM2NzA1MDU0fQ.ip3r_qdu2msSUC2-1Pc6-GpDbnEraWitbnNCh5_hxp3bdSoyykNS7_GSFByU5QCJOvLs2Khamcjsl95BMfukiECJ6Dra9yx4SlCCLB42Nfc0QvjpsCSY459MTu2mxrio1OnfuqNHIXokalW9I0yKOxDvBYp5a2gbSCwT2O5PoGnxvKHMax_73_ia_-OSvN1QJVB3ujqnuqU47x51TYgZrRY9SUGkjEm4BIGO6J25HneaQXIy8EXsysOE8eCJ5Kpbcekd3TGK93fCnxd1CB5sbnL0EaZAH_vAOwUhv2ouEFVuqZ2g8vum01BBik0LcIR-d_7IkbdcYQhWCOxSOxhO6g"}
    request('/fodi',
            '?path=/&encrypted='
            + NEW_ACCESS_TOKEN['encrypted']
            + '&plain=' + NEW_ACCESS_TOKEN['plain'] + '&passwd=undefined')
