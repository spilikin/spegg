from fastapi import HTTPException, APIRouter
from spegg.db import db
import spegg.dbmodel as dbmodel
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from pprint import pprint
from . import __version__

api = APIRouter()

@api.get("/info")
async def root():
    return {"version": __version__}

class ResourceVersionReferenceResource(BaseModel):
    resource: dbmodel.Resource
    version: str
    url: str

class SubjectVersionResource(BaseModel):
    subject_id: str
    version: str
    type: dbmodel.SubjectType
    references: List[ResourceVersionReferenceResource] = []


class SubjectResource(BaseModel):
    id: str
    versions: List[str] = []
    type: dbmodel.SubjectType
    latest_version: str


@api.get("/Subject", response_model=List[SubjectResource])
async def get_all_subjects():
    result = db.SubjectVersion.aggregate([
        {
            '$group': {
                '_id': { '$toLower': '$subject_id'},
                'id': { '$first': '$subject_id'},
                'type': { '$first': '$type'},
                'latest_version': { '$max': '$version' },
                'versions': { '$addToSet': '$version'}
            }
        },
        {
            '$sort': { '_id': 1}
        }
    ])
    response = []
    for subj_dict in result:
        response.append(SubjectResource(**subj_dict))
    return response

@api.get("/Subject/{subject_id}", response_model=List[SubjectVersionResource])
async def get_all_subject_versions(subject_id:str):
    result = db.SubjectVersion.aggregate([
        {
            '$match': {'subject_id': subject_id }
        },
        {
        '$lookup': {
            'from': "ResourceVersion",
            'localField': "resources",
            'foreignField': "_id",
            'as': "resources"
        }
    }])
    response = []
    for subj_dict in result:
        response.append(SubjectVersionResource(**subj_dict))
    return response

@api.get("/Subject/{subject_id}/{version}", response_model=SubjectVersionResource)
async def get_subject_version(subject_id:str, version:str):
    result = list(db.SubjectVersion.aggregate([
        {
            '$match': {'subject_id': subject_id, 'version': version}
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

    ]))

    if len(result) == 0:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    return SubjectVersionResource(**result[0])
    
