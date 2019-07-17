#-*- encoding:utf-8 -*-
from flask import url_for,render_template
from flask import Flask, request, Response,send_from_directory
import json
from werkzeug.utils import secure_filename
from os import path
import os
from picture_deal import Matcher
import traceback
import cv2

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
HOST = "leping.info"
PORT = 5000

app = Flask(__name__)
app.config['Matcher'] = Matcher(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def jsonResponse(errCode, errMsg, data = None):
    return json.dumps({
        'errCode': errCode,
        'errMsg': errMsg,
        'data': data
    })

def downloadUrl(fileName):
    return "http://" + HOST + ":" + str(PORT) + "/download/" + fileName

@app.route("/upload", methods=["POST"])
def uploadFile():
    if 'source' not in request.files or 'target' not in request.files:
        return Response("error params msg!")

    src = request.files['source']
    tar = request.files['target']

    if src.filename == "" or tar.filename == "":
        return Response("Not selected file")
    if not allowed_file(src.filename):
        return "not allow for file name:" + src.filename
    if not allowed_file(tar.filename):
        return "not allow for file name:" + tar.filename

    matcher = app.config['Matcher']

    srcSavePath = matcher.getOriginalSavePath(secure_filename(src.filename))
    tarSavePath = matcher.getComparedSavePath(secure_filename(tar.filename))
    resSavePath = matcher.getResultSavePath(secure_filename(tar.filename))
    src.save(srcSavePath)
    tar.save(tarSavePath)
    resFileName = resSavePath.split(os.sep)[-1]

    errCode = 0
    errMsg = None
    data = None

    try:
        rects = matcher.compareAndSave(srcSavePath, tarSavePath, resSavePath)
        download = downloadUrl("result/" + resFileName)
        data = {
            'result': download,
            'differences': rects
        } 
    except Exception as ex:
        errCode = -1
        errMsg = str(ex)
        traceback.print_exc()

    #return jsonResponse(errCode, errMsg, data)
    originalImg = downloadUrl("original/" + srcSavePath.split(os.sep)[-1])
    return render_template("result.html", original = originalImg, result = download, message = errMsg)

@app.route("/list", methods=["GET"])
def list_im():
    matcher = app.config['Matcher']
    return jsonResponse(0, "", os.listdir(matcher.resultDir))

def get_image(file):
    mdict = {
        'jpeg': 'image/jpeg',
        'jpg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif'
    }
    mime = mdict[(file.split('.')[1])]
    return mime

@app.route('/download/<midpath>/<filename>', methods=['GET'])
def download(midpath, filename):
    if request.method=="GET":
        matcher = app.config['Matcher']
        fileDir = os.path.join(matcher.workingDir, midpath)
        filePath = os.path.join(fileDir, filename)
        if os.path.isfile(filePath):
            return send_from_directory(fileDir, filename, as_attachment=False)
        else:
            return jsonResponse(-1, "Can't not found file '%s'" % (filename))

@app.route('/')
def index():
    return render_template('upload.html', version = cv2.__version__)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = PORT)