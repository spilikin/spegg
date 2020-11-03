from spegg.api import __version__
from spegg.db import db
from pprint import pprint
import spegg.dbmodel as dbmodel

def test_all_subjects():
    query_result = list(db.Subject.find({}))

    for subject_dict in query_result:
        subject = dbmodel.Subject(**subject_dict)
        pprint(subject.title)

def test():
    resource_id = 'gemSpec_FM_ePA'
    version = '1.6.0'

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
                'resource': { '$arrayElemAt': [ '$resource', 0 ] },
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
                'as': 'referenced_by_subjects'
            },
        },


        {
            '$project': {
                'referenced_by_subjects.references': 0,
            }
        },


    ]))

    pprint(query_result)

    query_result = list(db.SubjectVersion.aggregate([
        {
            '$match': {'subject_id': 'gemProdT_Kon', 'version': '4.4.0-0'}
        },
        {
            '$project': {
                'references.requirements': 0,
            }
        },
    ]))

    pprint(query_result)