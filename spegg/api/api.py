from fastapi import HTTPException, APIRouter
from spegg.db import db
import spegg.dbmodel as dbmodel
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Dict
from pprint import pprint
from . import __version__

api = APIRouter()

class InfoSubjectTypeResource(BaseModel):
    type: dbmodel.SubjectType
    count: int = 0
    versions: int = 0

class InfoResource(BaseModel):
    version: str
    subjects: List[InfoSubjectTypeResource] = []

@api.get(
    "/info",
    response_model=InfoResource,
)
async def info():
    response = InfoResource(version=__version__)

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

    for subj_dict in query_result:
        response.subjects.append(InfoSubjectTypeResource(**subj_dict))

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
     
    for subj_ver_dict in query_result:
        subject_info = next(filter(lambda s: s.type == subj_ver_dict['type'], response.subjects), None)
        pprint(subj_ver_dict)
        pprint(subject_info)
        if subject_info != None:
            subject_info.versions = subj_ver_dict['versions']

    return response

class DiffType(str, Enum):
    Added = 'Added'
    Removed = 'Removed'
    Changed = 'Changed'

class Diff(BaseModel):
    type: DiffType
    changes: Dict[str, str] = {}

class ReferenceShortResource(BaseModel):
    resource: dbmodel.Resource
    version: str
    url: Optional[str]
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
    url: Optional[str]
    subject_id: str
    subject_version: str
    requirements: List[RequirementReferenceResource] = []

class SubjectVersionShortResource(BaseModel):
    subject_id: str
    version: str
    validity: dbmodel.SubjectVersionValidity

class SubjectShortResource(BaseModel):
    id: str
    title: str
    type: dbmodel.SubjectType

class SubjectVersionListItemResource(BaseModel):
    subject: SubjectShortResource
    version: str
    validity: dbmodel.SubjectVersionValidity

class SubjectVersionResource(BaseModel):
    subject: SubjectShortResource
    version: str
    validity: dbmodel.SubjectVersionValidity
    references: Optional[List[ReferenceShortResource]] = None
    versions: List[SubjectVersionShortResource]

class SubjectResource(BaseModel):
    id: str
    title: str
    type: dbmodel.SubjectType
    versions: List[SubjectVersionShortResource] = []
    latest_version: Optional[str]

class ResourceListItemResource(BaseModel):
    id: str
    title: str
    type: dbmodel.ResourceType
    versions: List[dbmodel.ResourceVersion] = [] 
    latest_version: str

class SubjectVersionReferenceResource(BaseModel):
    subject: SubjectShortResource
    version: str
    validity: dbmodel.SubjectVersionValidity

class ResourceVersionResource(BaseModel):
    resource_id: str
    version: str
    resource: dbmodel.Resource
    url: Optional[str]
    versions: List[dbmodel.ResourceVersion] = [] 
    referenced_by_subjects: List[SubjectVersionReferenceResource] = []

@api.get(
    "/Subject", 
    response_model=List[SubjectResource],
    response_model_exclude_unset=True
)
async def get_all_subjects():
    result = db.Subject.aggregate([
        {
            '$lookup': {
                'from': "SubjectVersion",
                'localField': 'id',
                'foreignField': 'subject_id',
                'as': 'versions'
            },            
        },
        {
            '$project': { 
                'id': 1,
                'type': 1,
                'title': 1,
                'versions.subject_id': 1,
                'versions.version': 1,
                'versions.validity': 1,
                'latest_version': { '$max': '$versions.version'}
            }
        },
        {
            '$sort': { 'id': 1}
        },
    ])
    response = []
    for subj_dict in result:
        response.append(SubjectResource(**subj_dict))
    return response

@api.get(
    "/Subject/{subject_id}", 
    response_model=List[SubjectVersionListItemResource], 
    response_model_exclude_unset=True
)
async def get_all_subject_versions(subject_id:str):
    result = db.SubjectVersion.aggregate([
        {
            '$match': {'subject_id': subject_id }
        },
        {
            '$lookup': {
                'from': "Subject",
                'localField': 'subject_id',
                'foreignField': 'id',
                'as': 'subject'
            },            
        },
        {
            '$project': {
                'subject_id': 1,
                'version': 1,
                'validity': 1,
                'subject': { "$arrayElemAt": [ "$subject", 0 ] },
            }
        }
    ])
    response = []
    for subj_dict in result:
        response.append(SubjectVersionListItemResource(**subj_dict))
    return response

@api.get(
    "/Subject/{subject_id}/{version}", 
    response_model=SubjectVersionResource,
    response_model_exclude_unset=True
)
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
                'version': {'$first': '$version' },
                'validity': {'$first': '$validity' },
                'references': {'$push': '$references'},
            }
        },
        {
            '$lookup': {
                'from': "SubjectVersion",
                'let': {'resource_id': '$resource_id', 'version': '$version'},
                'pipeline': [
                    { 
                        '$match': {'subject_id': subject_id },  
                    },
                    {
                        '$project': { 
                            'subject_id': 1,
                            'version': 1,
                            'validity': 1,
                        }
                    },

                ],
                'as': 'versions'
            },
        },
        {
            '$lookup': {
                'from': "Subject",
                'localField': 'subject_id',
                'foreignField': 'id',
                'as': 'subject'
            },            
        },
        {
            '$addFields': {
                'subject': { "$arrayElemAt": [ "$subject", 0 ] },
            }
        }

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

@api.get(
    "/Reference/{subject_id}/{version}/{resource_id}", 
    response_model=ReferenceResource,
    response_model_exclude_unset=True
)
async def get_resource_reference(subject_id: str, version: str, resource_id: str, compare_version: Optional[str] = None, compare_resource_id: Optional[str] = None, compare_subject_id: Optional[str] = None):
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

    if compare_version:
        if not compare_subject_id:
            compare_subject_id = subject_id
        if not compare_resource_id:
            compare_resource_id = resource_id
        try:
            other = await get_resource_reference(compare_subject_id, compare_version, compare_resource_id)
            other_requirements = other.requirements
        except:
            other_requirements = []

        for other_req in other_requirements:
            this_req = next((req for req in reference.requirements if req.id == other_req.id), None)
            if this_req != None:
                if this_req.text.strip() != other_req.text.strip():
                    this_req.diff = Diff(type=DiffType.Changed, changes={'html': other_req.html})
            else:
                other_req.diff = Diff(type=DiffType.Removed)
                reference.requirements.append(other_req)
        for this_req in reference.requirements:
            other_req = next((req for req in other_requirements if req.id == this_req.id), None)
            if other_req == None:
                this_req.diff = Diff(type=DiffType.Added)

        reference.requirements.sort(key=lambda req: req.diff.type if req.diff != None else '', reverse=True)


    return reference

@api.get(
    "/Resource", 
    response_model=List[ResourceListItemResource],
    response_model_exclude_unset=True
)
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
        item = ResourceListItemResource(**res_dict, latest_version='None')
        item.latest_version = max(item.versions, key=lambda version: version.version).version
        response.append(item)

    return response

@api.get(
    "/Resource/{resource_id}/{version}", 
    response_model=ResourceVersionResource,
    response_model_exclude_unset=True
)
async def get_resource_version(resource_id: str, version: str, compare: Optional[str] = None):
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
                    {
                        '$lookup': {
                            'from': "Subject",
                            'localField': 'subject_id',
                            'foreignField': 'id',
                            'as': 'subject'
                        },            
                    },
                    {
                        '$addFields': {
                            'subject': { "$arrayElemAt": [ "$subject", 0 ] },
                        }
                    }
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

    if len(query_result) == 0:
        raise HTTPException(status_code=404, detail="ResourceVersion not found")

    return ResourceVersionResource(**query_result[0])
