echo %cd%
virtualenv env
.\env\Scripts\activate&&pip3 install -r requirements.txt&&set FLASK_ENV=development &&set FLASK_DEBUG =True&&set FLASK_APP=run.py&&pip install scipy&&pip install firebase-admin google-cloud-firestore&&pip install python-dateutil&&pip uninstall werkzeug&&pip install werkzeug~=2.0.1
py run.py