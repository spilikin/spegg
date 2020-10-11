from pymongo import MongoClient
import logging
import datetime
from pprint import pprint

client = MongoClient(
    'localhost',
    username='spegg',
    password='bad_password',
    authSource='spegg',
    authMechanism='SCRAM-SHA-256')

db = client.spegg

COLLECTIONS = [
    'Resource',
    'ResourceVersion',
    'Subject',
    'SubjectVersion',
    'SubjectVersionDescriptor'
]

def clean():
    for c in COLLECTIONS:
       db[c].delete_many({})

def test():
    result = list(db.SubjectVersion.aggregate([
        {
            '$match': {'subject_id': 'gemAnbT_CVC_Root', 'version': '1.0.2'}
        },        
        {
            '$lookup': {
                'from': "ResourceVersion",
                'localField': 'resources',
                'foreignField': '_id',
                'as': "reference"
            },
        },
        {"$unwind":"$reference"},
        {
            '$lookup': {
                'from': "Resource",
                'localField': 'reference.resource_id',
                'foreignField': 'id',
                'as': 'resource'
            }
        },
        {
            '$addFields': {
                'reference.resource': '$resource'
            }
        },
        {
            '$project': { 
                'subject_id': 1,
                'type': 1,
                'version': 1,
                'reference.version': 1,
                'reference.url': 1,
                "reference.resource": { "$arrayElemAt": [ "$reference.resource", 0 ] },
            }
        },
        {
            '$group': {
                '_id': '$_id',
                'subject_id': {'$first': '$subject_id' },
                'type': {'$first': '$type' },
                'version': {'$first': '$version' },
                'references': {'$push': '$reference'}
            }
        }


#        {'$limit':1}
    ]))
    pprint(result)
'''
                    'localField': "resources",
                'foreignField': "_id",
                'pipeline': [
                    {
                        '$lookup': {
                            'from': "Resource",
                            'localField': "resource_id",
                            'foreignField': "id",
                            'as': "_res"
                        },
                    },
                ],
'''