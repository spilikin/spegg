from spegg.api import __version__
from spegg.db import db
from pprint import pprint
import spegg.dbmodel as dbmodel

def test_all_subjects():
    query_result = list(db.Subject.find({}))

    for subject_dict in query_result:
        subject = dbmodel.Subject(**subject_dict)
        #pprint(subject.title)


def test():
    query_result = list(db.Subject.aggregate([
        {
            '$group' : {
                '_id':'$type', 
                'count': { '$sum': 1},
                'type': {'$first': '$type' },
            }
        },
        {
            '$project': {
                '_id': 0,
            }
        },
     ]))
    pprint(query_result)

    query_result = list(db.SubjectVersion.aggregate([
        {
            '$lookup': {
                'from': "Subject",
                'localField': 'subject_id',
                'foreignField': 'id',
                'as': 'subject'
            },        
        },
        {"$unwind":"$subject"},
        {
            '$group' : {
                '_id':'$subject.type', 
                'type': {'$first': '$subject.type' },
                'versions': { '$sum': 1}
            }
        },
        {
            '$project': {
                '_id': 0,
            }
        },
     ]))
    pprint(query_result)

