#!/usr/bin/env bash

curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
poetry config virtualenvs.in-project true
poetry install
cp lanzous.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now lanzous
