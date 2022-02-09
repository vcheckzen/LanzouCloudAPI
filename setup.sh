#!/usr/bin/env bash

for rq in curl tar grep sed systemctl python3; do
    [ "$(command -v $rq)" ] || {
        echo "Lack of $rq, quit installation"
        exit
    }
done

IP=140.249.61.99
DOMAIN=lanzoui.com
OLD_DOMAIN=pan.lanzou.com
REPO=LanzouCloudAPI
SAVE_PATH=/usr/local/share
POETRY_INSTALATION_SCRIPT=https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py

install() {
    curl -sSL "$POETRY_INSTALATION_SCRIPT" | python3 -
    source $HOME/.poetry/env

    cd "$SAVE_PATH"
    rm -f master.tar.gz
    curl -LO "https://github.com/vcheckzen/$REPO/archive/master.tar.gz"

    systemctl stop lanzous 2>/dev/null
    rm -rf "$REPO"
    mkdir "$REPO"
    tar xf master.tar.gz -C "$REPO" --strip-components 1
    rm -f master.tar.gz

    cd "$REPO"
    poetry config virtualenvs.in-project true
    poetry install

    sed -i "/.*$OLD_DOMAIN/d" /etc/hosts
    grep "$DOMAIN" /etc/hosts &>/dev/null && {
        sed -i "s/.*$DOMAIN/$IP $DOMAIN/" /etc/hosts
    } || {
        echo "$IP $DOMAIN" >>/etc/hosts
    }

    cp lanzous.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable --now lanzous
}

uninstall() {
    curl -sSL "$POETRY_INSTALATION_SCRIPT" | python3 - --uninstall

    rm -rf "$SAVE_PATH/$REPO"

    sed -i "/.*$DOMAIN/d" /etc/hosts

    systemctl disable --now lanzous
    rm -f /etc/systemd/system/lanzous.service
}

[ "$1" == 'uninstall' ] && uninstall || install
