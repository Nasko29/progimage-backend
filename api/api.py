from flask import Flask, request, redirect, abort, render_template, url_for, jsonify
import requests, datetime, math, boto3, os, json, sys
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from werkzeug.utils import secure_filename
from uuid import uuid4
from progimagemodels import Client, Image

# initialize flask application
app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# initialize xray tracing
xray_recorder.configure(service='app')
XRayMiddleware(app, xray_recorder)

# connect to s3 resource
bucket = "progimage-eu-west-1"
s3 = boto3.client('s3')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Tools                                                                                   #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def allowed_file_extension(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def file_extension(filename):
    return os.path.splitext(filename)[-1]

def upload_to_s3(file, index, bucket, acl='public-read'):
    """ Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
     labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco 
     laboris nisi ut aliquip ex ea commodo consequat.
    """

    # pipe file to s3
    response = s3.put_object(
        ACL = acl,
        Body = file.data.read(),
        Bucket = bucket,
        Key = index)

    return response

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Routes                                                                                  #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
@app.route('/', methods=['GET'])
@xray_recorder.capture('index')
def index():
    """ Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
     labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco 
     laboris nisi ut aliquip ex ea commodo consequat.
    """
    
    return "", 200

@app.route('/apikey', methods=['GET','DELETE'])
@xray_recorder.capture('apikey')
def apikey():
    """ Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
     labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco 
     laboris nisi ut aliquip ex ea commodo consequat.
    """

    if(request.method == 'GET'):
        
        # create a new api key and db entry
        newcomer = Client()

        return jsonify(apikey=newcomer.apikey), 200

    elif(request.method == 'DELETE'):

        # get the client id
        clientid = request.headers['Apikeyid']

        # fetch the client
        target = Client(clientid)

        # delete the api key and the db entry
        target.delete()
        
        return "", 200

    return "",400

@app.route('/upload', methods=['POST'])
@xray_recorder.capture('upload')
def upload():
    """ Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
     labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco 
     laboris nisi ut aliquip ex ea commodo consequat.
    """

    # get the client id
    clientid = request.headers['Apikeyid']

    # obtain file from form
    if 'file' not in request.files:
        return "",403
    file = request.files['file']

    # verify that there is a filename
    if file.filename == '':
        return "",403

    # store file in the bucket
    if file and allowed_file_extension(file.filename):
        filename = secure_filename(file.filename)

        # generate file index [clientid] / [uuid] . [extension]
        index = "/".join([clientid, uuid4().hex]) + file_extension(filename)

        # upload to s3

        return index, 200

    return "", 403 

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   Errors                                                                                #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.errorhandler(404)
@xray_recorder.capture('error404')
def not_found(error):
   return "Error 404 Not Found"

@app.errorhandler(500)
@xray_recorder.capture('error500')
def not_found(error):
   return "Error 500 Internal Server Error"

if __name__ == '__main__':
    app.run()