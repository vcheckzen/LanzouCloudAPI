#!/usr/bin/env bash

curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
poetry install
cp lanzous.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now lanzous
