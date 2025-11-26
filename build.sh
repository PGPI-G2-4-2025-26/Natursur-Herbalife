#!/usr/bin/env bash 
set -o errexit 
pip install -r requirements.txt 
python manage.py migrate 
python manage.py shell -c "from main.import_csv import cargar; print(cargar())" 
python manage.py seed
python manage.py collectstatic --noinput
