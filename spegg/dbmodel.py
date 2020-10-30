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
    title: str

class ResourceVersion(BaseModel):
    resource_id: str 
    version: str
    url: Optional[str]

class SubjectType(str, Enum):
    Provider = 'Provider'
    Product = 'Product'
    ThirdParty = 'ThirdParty'
    Requirements = 'Requirements'

class Subject(BaseModel):
    id: str
    type: SubjectType    
    title: str
    description = ""

class RequirementReference(BaseModel):
    id: str
    title: str
    text: str
    html: str
    level: str
    test_procedure: str

class ResourceReference(BaseModel):
    resource_id: str
    resource_version: str
    requirements: List[RequirementReference] = []

class SubjectValidity(str, Enum):
    Unspecified = 'Unspecified'
    Invalid = 'Invalid'
    ValidFrozen = 'ValidFrozen'
    ValidActive = 'ValidActive'
    Pending = 'Pending'

class SubjectVersion(BaseModel):
    subject_id: str
    title: str
    version: str
    type: SubjectType
    references: List[ResourceReference] = []
    description = ""
    validity: SubjectValidity = SubjectValidity.Unspecified

class SubjectVersionDescriptor(BaseModel):
    subject_id: str
    version: str
