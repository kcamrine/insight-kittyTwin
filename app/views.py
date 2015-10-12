from flask import render_template, request, redirect, url_for, send_from_directory, jsonify
from app import app
import pymysql as mdb
import sqlalchemy
import pandas as pd
import psycopg2
from werkzeug import secure_filename
from flask import send_from_directory
import os
import subprocess
import match_petfinder
import pull_human
import pickle
import random
import string
import re
import cv2 
import sys
import numpy as np

sys_args = pickle.load( open("api_config.p", "rb") ) #load in private settings
savedata = pickle.load( open( "dirpaths_config.p", "rb" ) )

db = psycopg2.connect(user=sys_args['user'], database=sys_args['database'])

UPLOAD_FOLDER_RAW = 'app/raw/'
UPLOAD_FOLDER_EDIT = 'app/edit/'
ALLOWED_EXTENSIONS = set(['jpg','jpeg','JPEG','JPG'])

app.config['UPLOAD_RAW_DEST'] = UPLOAD_FOLDER_RAW
app.config['UPLOAD_EDIT_DEST'] = UPLOAD_FOLDER_EDIT
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_RAW

global model_SF, model_LA, model_S

model_SF = cv2.createEigenFaceRecognizer(threshold=100000) ## NEW
model_LA = cv2.createEigenFaceRecognizer(threshold=100000) ## NEW 
model_S = cv2.createEigenFaceRecognizer(threshold=100000) ## NEW

model_SF.load("app/eigenModel_SF.xml") ## NEW
model_LA.load("app/eigenModel_LA.xml") ## NEW
model_S.load("app/eigenModel_S.xml") ## NEW

# check file is ok
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# create random filename
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# accept uploaded file
@app.route('/',methods=['GET','POST'])
def upload_file():
    return render_template('input.html')

# create new filename
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route('/output',methods=['POST'])
def report_match():
    file = request.files['file']
    city = request.form.getlist('City')[0] #which model to use ##NEW
    
    if file and allowed_file(file.filename):
        file.filename = str(id_generator(size = 12)) + '.jpg'
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_RAW_DEST'],filename))
        print filename
        #        return redirect(url_for('report_match',filename=filename))
    #get location of saved file
    print 'filename: ' + filename
    filepath = os.path.join(app.config['UPLOAD_RAW_DEST'],filename)
    print filepath
    print app.config['UPLOAD_RAW_DEST']
    #process saved file (meat 1)
    human = pull_human.pull_human(filepath,app.config['UPLOAD_EDIT_DEST'])
    if human == -1:
        return redirect(url_for('no_face_detected'))
    else:
    #match to database (meat 2)
    # Read the image we're looking for                                                                                 
        sampleImage = cv2.imread(human, cv2.IMREAD_GRAYSCALE)
        sampleImage = cv2.resize(sampleImage, (256,256))
    # Look through the model and find the face it matches                                                              
        if city == "SF":
            [p_label, p_confidence] = model_SF.predict(sampleImage)
            matched_cat = savedata['filelist_SF'][p_label]
        elif city == "LA":
            [p_label, p_confidence] = model_LA.epredict(sampleImage)
            matched_cat = savedata['filelist_LA'][p_label]
        elif city == "S":
            [p_label, p_confidence] = model_S.predict(sampleImage)
            matched_cat = savedata['filelist_S'][p_label]
# replace with above
#        matched_cat = match_petfinder.match_faces(image=human, 
#                                              threshold=100000, 
#                                              model_name="eigenModel.xml")
        #extract metadata
        print "matched cat: " + matched_cat
        with db:
            cur = db.cursor()
            sql_query = "SELECT a.id, a.name, a.picture, b.city FROM name_data_table a join contact_info_data_table b on a.id=b.id where b.id='" + matched_cat + "';"
            query_results = pd.read_sql_query(sql_query,db)
            name=query_results.loc[0][1]
            image=query_results.loc[0][2]
            city=query_results.loc[0][3]
            website='https://www.petfinder.com/petdetail/' + str(query_results.loc[0][0])
            to_image = "/static/images/" + filename
            print image
            image = re.sub(r"-(t|pn|pnt|fpm)\.jpg","-x.jpg",image)
            print image
        return render_template("output.html",
                           filepath='http://localhost:5000/uploads/' + filename , 
                           newpic = image,
                           name=name,
                           city=city,
                           website=website)



@app.route('/uploads/<id>')
def show(id):
    return send_from_directory('/Users/kamrine/Documents/projects/Insight/insight-kittyTwin/app/raw/', id)

@app.route('/gif/<id>')
def show_loading(id):
    return send_from_directory('/static/images', "loading.gif")



@app.route('/retry',methods=['GET','POST'])
def no_face_detected():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            file.filename = str(id_generator(size = 12)) + '.jpg'
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_RAW_DEST'],filename))
            print filename
            return redirect(url_for('report_match',filename=filename))
    return render_template("re_enter.html")

