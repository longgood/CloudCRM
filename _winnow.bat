echo %cd%
virtualenv env
.\env\Scripts\activate
set FLASK_ENV=development 
set FLASK_DEBUG =True
set FLASK_APP=run.py
python3 run.py