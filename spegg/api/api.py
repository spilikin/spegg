from fastapi import HTTPException, APIRouter
from spegg.db import db
import spegg.dbmodel as dbmodel
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Dict
from pprint import pprint
from . import __version__

api = APIRouter()

@api.get("/info")
async def root():
    return {"version": __version__}

class DiffType(str, Enum):
    Added = 'Added'
    Removed = 'Removed'
    Changed = 'Changed'

class Diff(BaseModel):
    type: DiffType
    changes: Dict[str, str] = {}

class ReferenceResourceShort(BaseModel):
    resource: dbmodel.Resource
    version: str
    url: str
    requirements_count: int
    diff: Optional[Diff]

class RequirementReferenceResource(BaseModel):
    id: str
    title: str
    text: str
    html: str
    level: str
    test_procedure: str
    diff: Optional[Diff]

class ReferenceResource(BaseModel):
    resource: dbmodel.Resource
    version: str
    url: str
    subject_id: str
    subject_version: str
    requirements: List[RequirementReferenceResource] = []

class SubjectVersionResource(BaseModel):
    subject_id: str
    version: str
    title: str
    type: dbmodel.SubjectType
    validity: dbmodel.SubjectValidity
    references: Optional[List[ReferenceResourceShort]] = None
    all_versions: Optional[List[str]] = None

class SubjectResource(BaseModel):
    id: str
    title: str
    type: dbmodel.SubjectType
    versions: List[str] = []
    latest_version: str

class ResourceResource(BaseModel):
    id: str
    title: str
    versions: List[dbmodel.ResourceVersion] = []

 

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

@api.get("/Subject/{subject_id}", 
    response_model=List[SubjectVersionResource], 
    response_model_exclude_unset=True)
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
async def get_subject_version(subject_id:str, version:str, compare: Optional[str] = None) -> SubjectVersionResource:
    query_result = list(db.SubjectVersion.aggregate([
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
                'validity': 1,
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
                'validity': {'$first': '$validity' },
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

    if len(query_result) == 0:
        raise HTTPException(status_code=404, detail="Subject not found")

    subject = SubjectVersionResource(**query_result[0])

    if compare != None:
        other = await get_subject_version(subject_id, compare)
        for other_reference in other.references:
            this_reference = next((obj for obj in subject.references if obj.resource.id == other_reference.resource.id), None)
            if this_reference != None:
                if this_reference.version != other_reference.version:
                    this_reference.diff = Diff(type=DiffType.Changed, changes={'version': other_reference.version})
            else:
                other_reference.diff = Diff(type=DiffType.Removed)
                subject.references.append(other_reference)
        for this_reference in subject.references:
            other_reference = next((obj for obj in other.references if obj.resource.id == this_reference.resource.id), None)
            if other_reference == None:
                this_reference.diff = Diff(type=DiffType.Added)
        
        subject.references.sort(key=lambda ref: ref.diff.type if ref.diff != None else '', reverse=True)


    return subject

@api.get("/Resource", response_model=List[ResourceResource])
async def get_all_resources():
    query_result = db.Resource.aggregate([
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
            }
        },
    ])
    response = []
    for res_dict in query_result:
        response.append(ResourceResource(**res_dict))
    return response

@api.get("/Reference/{subject_id}/{version}/{resource_id}", response_model=ReferenceResource)
async def get_resource_reference(subject_id: str, version: str, resource_id: str, compare: Optional[str] = None):
    query_result = list(db.SubjectVersion.aggregate([
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
                'resource': { '$arrayElemAt': [ "$resource", 0 ] },
                'url': { '$arrayElemAt': [ '$resource_version.url', 0 ] },
            }
        },
        { 
            '$project': {
                '_id': 0,
                'resource': 1,
                'version': 1,
                'url': 1,
                'subject_id': 1,
                'subject_version': 1,
                'requirements': 1,
            }             
        }, 
    ]))
    if len(query_result) == 0:
        raise HTTPException(status_code=404, detail="Subject not found")

    reference = ReferenceResource(**query_result[0])

    if compare:
        other = await get_resource_reference(subject_id, compare, resource_id)
        for other_req in other.requirements:
            this_req = next((req for req in reference.requirements if req.id == other_req.id), None)
            if this_req != None:
                if this_req.text.strip() != other_req.text.strip():
                    print (this_req.text)
                    print (other_req.text)
                    this_req.diff = Diff(type=DiffType.Changed, changes={'html': other_req.html})
            else:
                other_req.diff = Diff(type=DiffType.Removed)
                reference.requirements.append(other_req)
        for this_req in reference.requirements:
            other_req = next((req for req in other.requirements if req.id == this_req.id), None)
            if other_req == None:
                this_req.diff = Diff(type=DiffType.Added)

        reference.requirements.sort(key=lambda req: req.diff.type if req.diff != None else '', reverse=True)


    return reference

'''
    if compare != None:
        other = await get_subject_version(subject_id, compare)
        for other_reference in other.references:
            this_reference = next((obj for obj in subject.references if obj.resource.id == other_reference.resource.id), None)
            if this_reference != None:
                if this_reference.version != other_reference.version:
                    this_reference.diff = Diff(type=DiffType.Changed, changes={'version': other_reference.version})
            else:
                other_reference.diff = Diff(type=DiffType.Removed)
                subject.references.append(other_reference)
        for this_reference in subject.references:
            other_reference = next((obj for obj in other.references if obj.resource.id == this_reference.resource.id), None)
            if other_reference == None:
                this_reference.diff = Diff(type=DiffType.Added)
        
        subject.references.sort(key=lambda ref: ref.diff.type if ref.diff != None else '', reverse=True)
'''
