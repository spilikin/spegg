#from spegg.api import __version__
from datetime import datetime
from spegg.api.db import collections
from pprint import pprint
from spegg.api.model import CollectionNames, ApprovalValidityCreate, ApprovalObjectCreate, ApprovalObjectVersionCreate
from spegg.api.model.approval_object import ApprovalObjectKind

def test_relationships():
    val1 = ApprovalValidityCreate(cn="valid", title="Gültig")
    val1_id = collections.ApprovalValidity.insert_one(val1.dict()).inserted_id
    pt1 = ApprovalObjectCreate(
        cn="gemProdT_FederationRoot", 
        title="Federation Trust Root", 
        kind=ApprovalObjectKind.ProductType,
        created=datetime.today(),
        updated=datetime.today(),
    )
    pt1_id = collections.ApprovalObject.insert_one(pt1.dict()).inserted_id

    ptv1 = ApprovalObjectVersionCreate(
        cn="gemProdT_FederationRoot_v1.0.0-alpha1",
        version="1.0.0-alpha1",
        typeId=pt1_id,
        validityId=val1_id,
        created=datetime.today(),
        updated=datetime.today(),
    )
    pprint (ptv1)
    ptv1_json = ptv1.json(indent=4)
    print (ptv1_json)
    ptv1_parsed = ApprovalObjectVersionCreate.parse_raw(ptv1_json)
    assert(ptv1.validityId == ptv1_parsed.validityId)
    pprint(ptv1_parsed)
    ptv1_id = collections.ApprovalObjectVersion.insert_one(ptv1.dict()).inserted_id

    pass
"""
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

"""