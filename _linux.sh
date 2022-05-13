#!/bin/sh
echo "----start----"
cd /home/ray/CloudCRM
echo "------------"
source env/bin/activate
export FLASK_ENV=development
export FLASK_DEBUG=True
export FLASK_APP=run.py
flask run --host="0.0.0.0" --port=80
echo "-------------gogo-----------------"

