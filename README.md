# LanzouCloudAPI

## Develop

### Start a Server

<!-- https://blog.csdn.net/COCO56/article/details/105959190 -->

```bash
git clone --depth 1 https://github.com/vcheckzen/LanzouCloudAPI.git
cd LanzouCloudAPI
pip3.6+ install -r requirements.txt
python3.6+ index.py
```

### Request APIs

```bash
➜  curl localhost:3000
{
  "code": -1,
  "examples": [
    "http://localhost:3000/?url=https://lanzous.com/i4wk2oh&type=down",
    "http://localhost:3000/?url=https://lanzous.com/i7tit9c&pwd=6svq&type=json"
  ],
  "msg": "invalid link"
}

➜  curl 'http://localhost:3000/?url=https://lanzous.com/i4wk2oh&type=json'
{
  "code": 200,
  "data": {
    "name": "nPlayer v1.6.1.5_190626 [Pro].apk",
    "size": "31.5MB",
    "url": "https://developer81.baidupan.com/040305bb/2019/07/09/7cc366020ff1530865f7e0c70d95a56e.apk?st=7xswzKkJd_WdJRAeYoFMiw&e=1617400107&b=BjoJWVQ4VzNWelZlAyEDJwIhWTRXeFdnUi8MMFZ_aVmFSXwo7VG1ZbAVmAmZXMQElUlwNAQJxUTgIBg0uUTcDcQY_a&fi=9965077&pid=120-229-85-16&up="
  },
  "msg": "success"
}

➜  curl -i 'http://localhost:3000/?url=https://lanzous.com/i7tit9c&pwd=6svq&type=down'
HTTP/1.0 302 FOUND
Content-Type: text/html; charset=utf-8
Content-Length: 947
Location: https://developer82.baidupan.com/040305bb/2019/12/03/96a3256ec57b632c34573353faaaea0a.apk?st=mHnA5SXouIMzjISkFVz-Yg&e=1617400245&b=BLFZzQK3Ur8E9gLSUeQOpATnCGdRfgo8U19YZgEoBDUCfgw0U7QDkgLiBLoC9VTWALJbnFDDA_bBUqgGcAOBR2gTeWRsCZ1I2BCQCIFF4DkcEPggwUbUKglO7WLMBtgS_bArQMtVPWA_bACzATmArRUxgDlW_bFQ8gOFVOEBuQCMUX0EN1kpAmk_c&fi=14862322&pid=120-229-85-16&up=
Server: Werkzeug/1.0.1 Python/3.9.2
Date: Fri, 02 Apr 2021 21:17:25 GMT
```

## Deploy

### Initialize the Service

```bash
# install python3.6+ manually before executing the following command
bash <(curl -sL https://github.com/vcheckzen/LanzouCloudAPI/raw/master/setup.sh)

# uninstall
bash <(curl -sL https://github.com/vcheckzen/LanzouCloudAPI/raw/master/setup.sh) uninstall
```

### Set up Reverse Proxy

```nginx
location /lanzous {
    proxy_pass http://localhost:3000;
    proxy_redirect off;
    proxy_set_header Host $http_host;
}
```
