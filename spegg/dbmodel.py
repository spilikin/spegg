from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Origin(BaseModel):
    originName: str
    originId: str
    originUrl: str

class SubjectType(str, Enum):
    Product = "Product"
    Provider = "Provider"
    ThirdParty = "ThirdParty"
    Interface = "Interface"

class Subject(BaseModel):
    cn: str
    type: SubjectType    
    title: str
    created: datetime
    updated: datetime
    aliases: List[str] = []
    description = ""
    origin: Optional[Origin]

class SubjectVersionValidity(BaseModel):
    id: str
    title: str
    origin: Origin

class SubjectVersion(BaseModel):
    subjectCn: str
    validityId: str
    version: str
    origin: Origin
    created: datetime
    updated: datetime
    documentVersion: str
    approvableFrom: Optional[datetime]
    approvableTo: Optional[datetime]
    description = ""
#    references: List[ResourceReference] = []

#
# ===============================================
#

class TextFormat(str, Enum):
    html = 'html'
    asciidoc = 'asciidoc'
    plain = 'plain'

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

class SubjectVersionReference(BaseModel):
    subject_id: str
    version: str

class Release(BaseModel):
    id: str
    title: str
    release_date: datetime
    description: str
    description_format: TextFormat = TextFormat.asciidoc
    subject_versions: List[SubjectVersionReference] = []
