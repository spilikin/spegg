from pymongo import MongoClient
import os

from spegg.api.model.approval_object import ApprovalObjectCreate

from .model import CollectionNames

client = MongoClient(
    os.getenv('MONGODB_HOST','localhost'),
    username=os.getenv('MONGODB_USERNAME', 'spegg'),
    password=os.getenv('MONGODB_PASSWORD', 'bad_password'),
    authSource=os.getenv('MONGODB_DATABASE', 'spegg'),
    authMechanism='SCRAM-SHA-256')

db = client.get_database(os.getenv('MONGODB_DATABASE', 'spegg'))

class collections:
    ApprovalObject = db.get_collection(CollectionNames.ApprovalObject)
    ApprovalObjectVersion = db.get_collection(CollectionNames.ApprovalObjectVersion)
    ApprovalValidity = db.get_collection(CollectionNames.ApprovalValidity)

def clean():
    for c in CollectionNames:
       db.get_collection(c).delete_many({})
