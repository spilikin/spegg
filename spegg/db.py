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
    result = list(db.SubjectVersion.aggregate([
        {
            '$match': {'subject_id': 'gemAnbT_CVC_Root', 'version': '1.0.2'}
        },
        {"$unwind":"$references"},
        {
            '$lookup': {
                'from': "ResourceVersion",
                'let': {'resource_id': '$references.resource_id', 'version': '$references.resource_version'},
                'pipeline': [
                    { 
                        '$match': {
                            '$expr': { 
                                '$and': [
                                    { '$eq': [ "$resource_id",  "$$resource_id" ] },
                                    { '$eq': [ "$version",  "$$version" ] },
                                ]
                            }
                        },
                    },
                ],
                'as': 'resource_version'
            },
        },
        {
            '$lookup': {
                'from': "Resource",
                'localField': 'resource_version.resource_id',
                'foreignField': 'id',
                'as': 'resource'
            }
        },
        {"$unwind":"$resource_version"},
        {
            '$addFields': {
                'references.version': '$resource_version.version',
                'references.url': '$resource_version.url'
            }
        },
        {
            '$project': { 
                'subject_id': 1,
                'type': 1,
                'version': 1,
                'references.version': 1,
                'references.url': 1,
                'references.requirements_count': {'$size': "$references.requirements"},
                'references.resource': { "$arrayElemAt": [ "$resource", 0 ] },
            }
        },
        {
            '$group': {
                '_id': '$_id',
                'subject_id': {'$first': '$subject_id' },
                'type': {'$first': '$type' },
                'version': {'$first': '$version' },
                'references': {'$push': '$references'},
            }
        },
        {
            '$lookup': {
                'from': "SubjectVersion",
                'localField': 'subject_id',
                'foreignField': 'subject_id',
                'as': '_versions'
            }
        },
        {
            '$addFields': {
                'all_versions': '$_versions.version'
            }
        },
        {
            '$project': { 
                "_versions": 0,
            }
        },

    ]))
    pprint(result)

'''
                'let': {'subject_id': '$subject_id'},
                'pipeline': [
                    {'$match': {'subject_id':'$subject_id'}},
                ],



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
            '$lookup': {
                'from': "SubjectVersion",
                'localField': 'subject_id',
                'foreignField': 'subject_id',
                'as': 'versions'
            }
        },
        {
            '$group': {
                '_id': '$_id',
                'subject_id': {'$first': '$subject_id' },
                'type': {'$first': '$type' },
                'version': {'$first': '$version' },
                'all_versions': { '$first': '$versions.version'},
                'references': {'$push': '$reference'},
            }
        },

'''