from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import Field

from .common import CommonFieldInfo, Markup, MongoBaseModel, Origin

class ApprovalObjectKind(str, Enum):
    ProviderType = 'ProviderType'
    ProductType = 'ProductType'
    ClientInterface = 'ClientInterface'
    ThirdParty = 'ThirdParty'

class ApprovalObjectFieldInfo:
    cn = Field(
        description="Kanonischer Name des Zulassungstyps (eine durch gematik vergebene ID)",
        example="gemProdT_FD_eRp"
    )
    title = Field(
        description="Bezeichnung eines Zulassungstyps"
    )
    kind  = Field(
        description="Art des Zulassungstyps",
        example="ProductType"
    )
    description = Field(
        description="Kurzbeschreibung eines Zulassungstyps",
        default=None
    )

class ApprovalObjectCreate(MongoBaseModel):
    cn: str = ApprovalObjectFieldInfo.cn
    title: str = ApprovalObjectFieldInfo.title
    kind: ApprovalObjectKind = ApprovalObjectFieldInfo.kind
    description: Optional[Markup] = ApprovalObjectFieldInfo.description
    origin: Optional[Origin] = CommonFieldInfo.origin
    created: datetime = CommonFieldInfo.created
    updated: datetime = CommonFieldInfo.updated