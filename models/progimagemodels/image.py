#!/usr/bin/env python3
import hashlib, boto3, os
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

class Image:

    # properties
    @property   
    def extension(self):
        return os.path.splitext(self.filename)[-1]

    @property   
    def index(self):
        return "/".join([self.clientid, self.uid, self.filename])

    # constructors
    def __init__(self, clientid, uid, filename=None):

        self.clientid = clientid
        self.uid = uid

        if(filename): # image doesn't exist and needs to be registered
            self.filename = filename
            create_image_entry(self)
        else: # image exists and needs to be retrieved
            filename = get_image_entry(clientid,uid)['filename']
    
    # model methods
    def save(self):
        pass

    def delete(self):
        delete_image_entry(self)

    # comparison methods
    def hash(self):
        pass
        # hashlib.sha256(open(location, 'rb').read()).hexdigest()

    def __eq__(self,other):
        return (self.clientid == other.clientid) && (self.uid == other.uid) && (self.extension == other.extension)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   Dynamodb functions                                                                    #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# connect to database resource
db = boto3.resource('dynamodb', region_name='eu-west-1', endpoint_url='http://dynamodb.eu-west-1.amazonaws.com')
dbimages = db.Table('Images')

def create_image_entry(image):

    item = {
        'clientid' : image.clientid,
        'uid' : image.uid,
        'filename' : image.filename,
        'extension' : image.extension
    }

    response = dbimages.put_item(Item = item)

def get_image_entry(clientid, uid):
    
    response = dbimages.query(
          KeyConditionExpression=Key('clientid').eq(clientid) && Key('uid').eq(uid)
    )

    return response['Items'][0]

def delete_image_entry(image):
    
    response = dbimages.delete_item(
        Key={
            'clientid': image.clientid,
            'uid': image.uid
        }
    )