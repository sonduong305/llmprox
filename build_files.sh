#!/bin/bash
python3 -m pip install -r requirements-vercel.txt
python3 manage.py collectstatic --noinput --clear
