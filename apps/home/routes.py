# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from apps import db
from apps.home import blueprint
from flask import render_template, request,send_file
from flask_login import login_required
from jinja2 import TemplateNotFound
import os

@blueprint.route('/alter_db')
def alter_db():
    result=db.engine.execute("ALTER TABLE TProject ADD startTime DATETIME ")
    result=db.engine.execute("ALTER TABLE TProject ADD endTime DATETIME ")
    return "updated"

@blueprint.route('/webgl')
def webgl():
    return render_template('home/webglIndex.html', segment='index')
@blueprint.route('/webgl_test')
def webgl_test():
    return render_template('home/webglIndex_test.html', segment='index')
@blueprint.route('/webglex')
def webglex():
    return render_template('home/deploayWebGL/index.html', segment='index')

image_directory = 'D://Dropbox//tmpp20230407//outputimage//20230415_155522_1_thread//'

@blueprint.route('/getimage/<filename>')
def get_image(filename):
    image_path = os.path.join(image_directory, filename)
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/jpeg')
    else:
        return "Image not found", 404
@blueprint.route('/getcsv/<filename>')
def get_csv(filename):
    image_path = os.path.join(image_directory, filename)
    print("ImagePath:",image_path)
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='text/csv')
    else:
        return "CSV not found", 404
#-----------------處理webgl的呼叫-------------------------------
image_directory = 'D://Dropbox//tmpp20230407//outputimage//'

@blueprint.route('/textfile',methods=['GET'])
def send_textfile():
    global image_directory
    # Logic to retrieve the text file
    userid=request.args.get('userid')
    if userid == "001walk":
        folder = image_directory+userid
    else:
        folder = image_directory+"000walk"
    filename = folder+"//outputfile.csv"
    print("send_textfile",filename)
    return send_file(filename, mimetype="text/plain")
    

#http://localhost:5000/imagenamelist?userid=001walk
@blueprint.route('/imagenamelist',methods=['GET'])
def image_filename():
    global image_directory
    # Logic to retrieve the text file
    userid=request.args.get('userid')
    
    print("USERID:",userid)
    if userid == "001walk":
            folder = 'D://Dropbox//tmpp20230407//outputimage//'+userid
            result="001walk@"
            print("image_filename:",result)
    else:
            folder = 'D://Dropbox//tmpp20230407//outputimage//'+"000walk"
            result="000walk@"    
            print("image_filename",result)
    namelist=[_ for _ in os.listdir(folder) if _.endswith(".jpg")]
    for name in namelist:
        result=result+name.split(".")[0]+";"
    return result
#http://localhost:5000/getimages?userid=000walk&filename=0000000
@blueprint.route('/getimages',methods=['GET'])
def get_images():
    userid=request.args.get('userid')
    filename=request.args.get('filename')
    file_path = os.path.join("D://Dropbox//tmpp20230407//outputimage//"+userid, filename+".jpg")
    print("filepath",file_path,",exist:",os.path.exists(file_path))
    return send_file(file_path, mimetype="image/jpeg")
    
    









@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')
@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:
        if not template.endswith('.html'):
            template += '.html'
        # Detect the current page
        segment = get_segment(request)
        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None







@blueprint.route('/video_feed')
def video_feed():
    global video
    global hands
    return Response(gen(video,hands),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@blueprint.route('/video')
def video():
    return render_template('home/webstring.html', segment='index')