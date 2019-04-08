#!/usr/bin/env python3
import hashlib, boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
class Image:

    # constructors
    def __init__(self, location, extension):
        self.ext = 'PNG'

    
    # model methods
    def save(self):
        pass


    # comparison methods
    def hash(self):
        pass
        # hashlib.sha256(open(location, 'rb').read()).hexdigest()

    def __eq__(self,other):
        pass


    # debugging
    def __str__(self):
        return "progimage image object with exension : " + self.ext\