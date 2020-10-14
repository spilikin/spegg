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

class ReferenceResourceShort(BaseModel):
    resource: dbmodel.Resource
    version: str
    url: str
    requirements_count: int

class ReferenceResource(BaseModel):
    resource: dbmodel.Resource
    version: str
    url: str
    requirements: List[dbmodel.RequirementReference] = []

class SubjectVersionResource(BaseModel):
    subject_id: str
    version: str
    title: str
    type: dbmodel.SubjectType
    references: Optional[List[ReferenceResourceShort]] = None
    all_versions: Optional[List[str]] = None

class SubjectResource(BaseModel):
    id: str
    title: str
    type: dbmodel.SubjectType
    versions: List[str] = []
    latest_version: str


@api.get("/Subject", response_model=List[SubjectResource])
async def get_all_subjects():
    result = db.SubjectVersion.aggregate([
        {
            '$group': {
                '_id': { '$toLower': '$subject_id'},
                'id': { '$first': '$subject_id'},
                'type': { '$first': '$type'},
                'title': { '$first': '$title'},
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
            '$project': {
                'references': 0,
            }
        }
    ])
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
                'title': 1,
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
                'title': {'$first': '$title' },
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

    if len(result) == 0:
        raise HTTPException(status_code=404, detail="Subject not found")

    return SubjectVersionResource(**result[0])

@api.get("/Resource")
async def get_all_resources():
    result = db.Resource.aggregate([
        {
            '$lookup': {
                'from': "ResourceVersion",
                'localField': 'id',
                'foreignField': 'resource_id',
                'as': 'versions'
            }
        },
        {
            '$project': {
                '_id': 0,
                'versions._id': 0,
                'versions.resource_id': 0,
            }
        },
    ])
    response = []
    for res_dict in result:
        response.append(res_dict)
    return response

@api.get("/Reference/{subject_id}/{version}/{resource_id}")
async def get_resoirce_reference(subject_id: str, version: str, resource_id: str):
    result = list(db.SubjectVersion.aggregate([
        {
            '$match': {'subject_id': subject_id, 'version': version}
        },
        { "$unwind": "$references" },
        { '$match': { 'references.resource_id': resource_id } },
        { "$group": {
            "_id": "$_id",
            "resource_id": { "$first": "$references.resource_id" },
            "version": { "$first": "$references.resource_version" },
            "subject_id": { "$first": "$subject_id" },
            "subject_version": { "$first": "$version" },
            "url": { "$first": "$references.url" },
            "requirements": { "$first": "$references.requirements" },
        }},
        {
            '$lookup': {
                'from': "Resource",
                'localField': 'resource_id',
                'foreignField': 'id',
                'as': 'resource'
            }
        },
        {
            '$lookup': {
                'from': "ResourceVersion",
                'let': {'resource_id': '$resource_id', 'version': '$version'},
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
            '$addFields': {
                'title': { '$arrayElemAt': [ "$resource.title", 0 ] },
                'url': { '$arrayElemAt': [ '$resource_version.url', 0 ] },
                'referred_by.subject_id': '$subject_id',
                'referred_by.subject_version': '$subject_version',
            }
        },
        { 
            '$project': {
                '_id': 0,
                'title': 1,
                'version': 1,
                'resource_id': 1,
                'url': 1,
                'referred_by': 1,
                'requirements': 1,
            } 
        }, 
    ]))
    if len(result) == 0:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    pprint(result)

    return result[0]
