from pymongo import MongoClient
import logging
import datetime
import os
from pprint import pprint

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
    'SubjectVersionDescriptor'
]

def clean():
    for c in COLLECTIONS:
       db[c].delete_many({})

def test():
    resource_id = 'gemSpec_CM_KOMLE'
    version = '1.8.0'

    query_result = list(db.ResourceVersion.aggregate([
        {
            '$match': {'resource_id': resource_id, 'version': version}
        },
        {
            '$lookup': {
                'from': "ResourceVersion",
                'localField': 'resource_id',
                'foreignField': 'resource_id',
                'as': 'versions'
            }
        },
        {
            '$lookup': {
                'from': "Resource",
                'localField': 'resource_id',
                'foreignField': 'id',
                'as': 'resource'
            }
        },
        {
            '$addFields': {
                'id': { '$arrayElemAt': [ '$resource.id', 0 ] },
                'title': { '$arrayElemAt': [ '$resource.title', 0 ] },
            }
        },

        {
            '$lookup': {
                'from': "SubjectVersion",
                'localField': 'resource_id',
                'foreignField': 'references.resource_id',
                'as': 'subject_versions'
            }
        },

        {
            '$lookup': {
                'from': "SubjectVersion",
                'let': {'resource_id': '$resource_id', 'version': '$version'},
                'pipeline': [
                    { "$unwind": "$references" },
                    { 
                        '$match': { 
                            '$and': [
                                { 'references.resource_id': resource_id },
                                { 'references.resource_version': version },
                            ]
                        } 
                    },

                ],
                'as': 'subject_versions'
            },
        },


        {
            '$project': {
                'resource_id': 0,
                'resource': 0,
                'subject_versions.references': 0,
            }
        },


    ]))

    pprint(query_result)
