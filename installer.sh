#!/usr/bin/env bash

python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
mkdir bot/videos
mkdir bot/logs
touch bot/data/blacklist.txt