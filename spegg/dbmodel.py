from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from bson.objectid import ObjectId

class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            raise TypeError('ObjectId required')
        return str(v)

class Resource(BaseModel):
    id: str
    description: str

class ResourceVersion(BaseModel):
    resource_id: str 
    version: str
    url: Optional[str]

class SubjectType(str, Enum):
    Provider = 'Provider'
    Product = 'Product'
    ThirdParty = 'ThirdParty'
    Requirements = 'Requirements'

class SubjectVersion(BaseModel):
    subject_id: str
    version: str
    type: SubjectType
    resources: List[PydanticObjectId] = []


class SubjectVersionDescriptor(BaseModel):
    subject_id: str
    version: str

class Requirement(BaseModel):
    id: str
    title: str
    text: str
    html: str
    level: str
