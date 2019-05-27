# LanzouCloudAPI

Redirect to download server when given lanzoucloud sharing link, implemented with Flask, python. This implementation uses User-Agent of both Android and PC, ensuring to get download link successfully.

## Request Format

Method: GET

| Params | Option | Remark   | Meaning                     |
| ------ | ------ | -------- | --------------------------- |
| url    |        | required | sharing link                |
| pwd    |        |          | password                    |
| type   |        |          | return download info        |
| type   | down   |          | redirect to download server |

## Response Format

### Headers

| Params       | Option           |
| ------------ | ---------------- |
| Content-Type | application/json |

### Body

| Params         | Option | Remark       | Msg       |
| -------------- | ------ | ------------ | --------- |
| code           | 200    | status code  | success   |
| code           | 400    | status code  | not found |
| data[filename] |        | filename     |           |
| data[filesize] |        | filesize     |           |
| data[downUrl]  |        | download url |           |

### Example:

#### Request:

```http
GET /?url=https://www.lanzous.com/i44mvof&pwd=btrs HTTP/1.1
Host: localhost:3000
```

#### Response:

##### Success

```json
{
  "code": 200,
  "data": {
    "downUrl": "https://development56.baidupan.com/052601bb/2019/05/12/5b85e328ab5c326e411893721c56d811.apk?st=YEmyz-0ZzZckZIbKWauizA&e=1558805839&q=org.telegram.messenger_5.6.1-15900_minAPI16.apk&fi=8662345&up=",
    "filename": "org.telegram.messenger_5.6.1-15900_minAPI16.apk"
  },
  "msg": "success"
}
```

##### Failure

```json
{
  "code": 404,
  "msg": "not found"
}
```
