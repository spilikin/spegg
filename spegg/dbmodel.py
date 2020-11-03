from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class ResourceType(str, Enum):
    DescriptorDocument = 'DescriptorDocument'
    InternalDocument = 'InternalDocument'
    ExternalDocument = 'ExternalDocument'
    InternalAPI = 'InternalAPI'
    ExternalAPI = 'ExternalAPI'

class Resource(BaseModel):
    id: str
    title: str
    type: ResourceType

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

class SubjectVersionValidity(str, Enum):
    Unspecified = 'Unspecified'
    Invalid = 'Invalid'
    ValidFrozen = 'ValidFrozen'
    ValidActive = 'ValidActive'
    Pending = 'Pending'

class SubjectVersion(BaseModel):
    subject_id: str
    version: str
    description = ""
    references: List[ResourceReference] = []
    validity = SubjectVersionValidity.Unspecified

class SubjectVersionDescriptor(BaseModel):
    subject_id: str
    version: str
