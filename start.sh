#!/bin/bash

set -eu

export PYTHONUNBUFFERED=true

VIRTUALENV=./venv

if [ ! -d $VIRTUALENV ]; then
  python3 -m venv $VIRTUALENV
fi

if [ ! -f $VIRTUALENV/bin/pip ]; then
  curl --silent --show-error --retry 5 https://bootstrap.pypa.io/pip/3.11/get-pip.py | $VIRTUALENV/bin/python
fi


$VIRTUALENV/bin/python3 site/main.py
