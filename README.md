# LanzouCloudAPI

## Introduction

Redirect to download server when given lanzoucloud share link, implemented with Flask, python

## Request Format

If the share link has a password, then

```html
https://www.example.com?url=https://www.lanzous.com/i3clqna&type=down&pwd=b2ur
```

Or

```html
https://www.example.com?url=https://www.lanzous.com/i3qi3kf
```

## How to Use

### Download the Code

Assuming you've installed git, then

```bash
git clone https://github.com/vcheckzen/LanzouCloudAPI.git
cd LanzouCloudAPI
```

### Install Requirements

```bash
pip install -r requirements.txt
```

### Run and Test

```bash
python app.py
```
