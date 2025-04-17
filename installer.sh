#!/usr/bin/env bash

python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
mkdir videos
mkdir logs
touch data/blacklist.txt