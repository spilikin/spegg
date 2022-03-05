from pymongo import MongoClient
import logging
import os

client = MongoClient(
    os.getenv('MONGODB_HOST','localhost'),
    username=os.getenv('MONGODB_USERNAME', 'spegg'),
    password=os.getenv('MONGODB_PASSWORD', 'bad_password'),
    authSource=os.getenv('MONGODB_DATABASE', 'spegg'),
    authMechanism='SCRAM-SHA-256')

db = client.spegg

COLLECTIONS = [
    'Resource',
    'ResourceVersion',
    'Subject',
    'SubjectVersion',
    'SubjectVersionValidity',
    'Release'
]

def clean():
    for c in COLLECTIONS:
        logging.info(f"Deleting collection: {c}")
        db[c].delete_many({})
