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

# initialize xray tracing
xray_recorder.configure(service='auth')
XRayMiddleware(app, xray_recorder)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Routes                                                                                  #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@app.route('/', methods=['GET'])
@xray_recorder.capture('index')
def index():
    '''
    Redirect the index of the website to the documentation
    '''
    print("redirecting!")
    return redirect("https://docs.readthedocs.io",code=301)


@app.route('/apikey', methods=['GET'])
@xray_recorder.capture('apikey')
def apikey():
    '''
    Create a new client and return a unique user id
    '''
    # create a new api key and db entry
    newcomer = Client()

    # generate response data
    data = {
        'apikey' : newcomer.apikey
    }

    return jsonify(data), 200


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