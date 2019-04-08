from flask import Flask, request, redirect, abort, render_template, url_for
import requests, datetime, math, boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

# initialize flask application
app = Flask(__name__)
xray_recorder.configure(service='app')
XRayMiddleware(app, xray_recorder)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ##
#   Hello World                                                                            #
# Handle user onboarding, where their database entry is created and their information stored
@app.route('/', methods=['GET'])
def helloworld():
    return "hello world!\n", 200

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   Errors                                                                                #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.errorhandler(404)
def not_found(error):
   return "Error 404 Not Found"

@app.errorhandler(500)
def not_found(error):
   return "Error 500 Internal Server Error"

if __name__ == '__main__':
    app.run()