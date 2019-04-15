# LanzouCloudAPI

## Introduction

Redirect to download server when given lanzoucloud share link, implemented with Flask, python. This implementation uses both User-Agent of Android and PC, ensuring to get direct link successfully.

## Request Format

If the share link has a password, then

```html
https://api-logi-py.us-south.cf.appdomain.cloud?url=https://www.lanzous.com/i3clqna&pwd=b2ur
```

Or

```html
https://api-logi-py.us-south.cf.appdomain.cloud?url=https://www.lanzous.com/i3qi3kf
```

## How to Use

### Download the Code

Assuming you've installed git, then

```bash
$ git clone https://github.com/vcheckzen/LanzouCloudAPI.git
$ cd LanzouCloudAPI
```

### Install Requirements and Run

```bash
$ pip install -r requirements.txt
$ python app.py
```

# Reference

- [LanzouAPI](https://github.com/MHanL/LanzouAPI)