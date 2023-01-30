echo %cd%
echo "------------"
.\env\Scripts\activate
echo "StartSetting"
set FLASK_ENV=development
set FLASK_DEBUG =True
set FLASK_APP=run.py

echo "done setting"
py run.py
echo "start"