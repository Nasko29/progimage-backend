#!/usr/bin/env python3
import hashlib, boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

class Client:

    # id property
    @property   
    def id(self):
        return self.apikeydict['id']

    # apikey property
    @property   
    def apikey(self):
        return self.apikeydict['value']

    # constructor
    def __init__(self, keyid=None):
        if(keyid): # client exists and needs to be retrieved
            self.apikeydict = get_api_key(keyid)
            self.images = get_client_images(self)
        else: # client doesn't exist and needs to be registered
            self.apikeydict = create_api_key()
            self.images = []
            create_client_entry(self)

    # save client objec to database
    def save(self):
        update_client_entry(self)

    # delete client object from database
    def delete(self):
        delete_api_key(self.id)
        delete_client_entry(self)

    # comparison operator
    def __eq__(self,other):
        return self.id == other.id

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   Dynamodb functions                                                                    #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# connect to database resource
db = boto3.resource('dynamodb', region_name='eu-west-1', endpoint_url='http://dynamodb.eu-west-1.amazonaws.com')
dbclients = db.Table('Clients')

def create_client_entry(client):

    item = {
        'id' : client.id,
        'apikey' : client.apikey,
        'images' : client.images
    }
    response = dbclients.put_item(Item = item)

def get_client_entry(client):

    response = dbclients.query(
          KeyConditionExpression=Key('id').eq(client.id)
    )

    return response

def get_client_images(client):

    response = dbclients.query(
          KeyConditionExpression=Key('id').eq(client.id)
    )

    return response['Items'][0]['images']

def delete_client_entry(client):

    response = dbclients.delete_item(
         Key = { 'id' : client.id}
      )

    return response

def update_client_entry(client):

    response = dbclients.update_item(
          Key={'id': client.id},
          UpdateExpression="set images=:i",
          ExpressionAttributeValues={':i': client.images},
          ReturnValues="UPDATED_NEW"
      )

    return response

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   APIGateway functions                                                                  #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# connect to gateway resource
gateway = boto3.client('apigateway')

def create_api_key():
    response1 = gateway.create_api_key(
        enabled=True,
        generateDistinctId=True,
    )
    response2 = gateway.create_usage_plan_key(
        usagePlanId='8tesk6',
        keyId=response1['id'],
        keyType='API_KEY'
    )
    return response1

def delete_api_key(keyid):
    response = gateway.delete_api_key(
        apiKey=keyid
    )
    return response

def get_api_key(keyid):
    response = gateway.get_api_key(
        apiKey=keyid,
        includeValue=True
    )
    return response



    
    