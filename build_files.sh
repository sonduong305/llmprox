#!/bin/bash
set -e

echo "Installing dependencies..."
python3.11 -m pip install -r requirements-vercel.txt

echo "Running migrations..."
python3.11 manage.py migrate --noinput

echo "Collecting static files..."
python3.11 manage.py collectstatic --noinput --clear
