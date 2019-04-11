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
    def __init__(self, uid, extension=None, filename=None, clientid=None):

        self.uid = uid
        if(clientid):
            self.clientid = clientid
        if(filename): # image doesn't exist and needs to be registered
            self.filename = filename
            create_image_entry(self)
        else: # image exists and needs to be retrieved
            if(extension):
                entry = get_image_entry_with_extension(clientid,extension)
                self.filename = entry['filename']
                self.clientid = entry['clientid']
            else:
                entry = get_image_entry(uid)
                self.filename = entry['filename']
                self.clientid = entry['clientid']
    
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
        pass

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   Dynamodb functions                                                                    #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# connect to database resource
db = boto3.resource('dynamodb', region_name='eu-west-1', endpoint_url='http://dynamodb.eu-west-1.amazonaws.com')
dbimages = db.Table('Images')

def create_image_entry(image):

    item = {
        'uid' : image.uid,
        'extension' : image.extension,
        'clientid' : image.clientid,
        'filename' : image.filename
    }
    print(item)
    response = dbimages.put_item(Item = item)

def get_image_entry_with_extension(uid, extension):
    
    response = dbimages.query(
          KeyConditionExpression=Key('uid').eq(uid) & Key('extension').eq(extension)
    )

    return response['Items'][0]

def get_image_entry(uid):
    
    response = dbimages.query(
          KeyConditionExpression=Key('uid').eq(uid)
    )

    return response['Items'][0]

def delete_image_entry(image):
    
    response = dbimages.delete_item(
        Key={
            'uid': image.uid,
            'extension': image.extension
        }
    )