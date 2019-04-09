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
xray_recorder.configure(service='api')
XRayMiddleware(app, xray_recorder)

# connect to s3 resource
BUCKETNAME = "progimage-eu-west-1"
s3 = boto3.client('s3')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Tools                                                                                   #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def is_allowed_file_extension(filename):
    '''
    Verify if the file extension is in by the ALLOWED_EXTENSION dictionary

    :param str filename: The filename
    :return: bool 
    '''

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def file_extension(filename):
    '''
    Obtain the extension of a filename

    :param str filename: The filename
    :return: the file extension as a string
    '''
    return os.path.splitext(filename)[-1]

def upload_file_to_s3(file, index, bucket, acl='public-read'):

    '''
    Upload file directly from memory to S3

    :param file file: the file object
    :param str index: the index to be used in s3
    :param str bucket: the name of the s3 bucket

    '''
    response = s3.upload_fileobj(
        Fileobj = file,
        Bucket = BUCKETNAME,
        Key = index)

    return response

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Routes                                                                                  #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@app.route('/api/client', methods=['DELETE'])
@xray_recorder.capture('api delete client')
def delete_client():
    '''
    Delete a client's database entry, api key and files on s3
    '''

    # get the client id
    clientid = request.headers['Apikeyid']

    # fetch the client
    target = Client(clientid)

    # delete the api key and the db entry
    target.delete()

    # delete all the files in s3 for this client
    bucket = s3.Bucket(BUCKETNAME)
    bucket.objects.filter(Prefix=clientid+"/").delete()
    
    return "", 200


@app.route('/api/upload', methods=['POST'])
@xray_recorder.capture('api upload file')
def upload():
    '''
    Receive a file and upload it to the s3 bucket, document its existence in the
    client's database entry and return a unique id that can be used to retrieve
    the image.

    :param file file: the file object
    :return: the unique id of the file
    '''

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
    if file and is_allowed_file_extension(file.filename):

        # ensure that the filename is safe
        filename = secure_filename(file.filename)

        # generate file index [clientid] / [uuid] . [extension]
        fileid = uuid4().hex
        ext = file_extension(filename)
        uid = uuid4().hex
        index = "/".join([clientid, uid, filename])

        # upload to s3
        upload_file_to_s3(file, index, BUCKETNAME)

        # generate response data
        data = {
            'uid' : uid
        }

        return jsonify(data), 200

    return "", 403 

@app.route('/api/', methods=['GET'])
@xray_recorder.capture('api download file')
def download():
    '''
    Receive a file and upload it to the s3 bucket, document its existence in the
    client's database entry and return a unique id that can be used to retrieve
    the image.

    :param file file: the file object
    :return: the unique id of the file
    '''

    # get the client id
    clientid = request.headers['Apikeyid']

    # obtain file identifer
    uid = request.args.get('uid', type=str)
    if uid is None :
        return "",403

    # get the associated filename
    # filename = 

    # generate file index
    # fileid = uuid4().hex
    # ext = file_extension(filename)
    # uid = uuid4().hex
    # index = "/".join([clientid, uid, filename])

    # obtain a presigned url for the file
    # url = s3.generate_presigned_url('get_object', Params = {'Bucket': BUCKETNAME, 'Key': index}, ExpiresIn = 100)

    # redirect to the file
    # return redirect(url, code=302)   
    return "", 200  

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   Errors                                                                                #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.errorhandler(404)
@xray_recorder.capture('error404')
def not_found(error):

    # generate a message
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.errorhandler(500)
@xray_recorder.capture('error500')
def not_found(error):
   return "Error 500 Internal Server Error"

if __name__ == '__main__':
    app.run()