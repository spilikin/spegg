from datetime import datetime
from typing import Optional
from pydantic import Field
from .common import CommonFieldInfo, Markup, MongoBaseModel, Origin

class ApprovalValidityFieldInfo:
    cn = Field(
        description="Kanonischer Name de Gültigkeit (eine durch gematik vergebene ID)",
        example="notApprovable"
    )
    title = Field(
        description="Texttitel der Gültigkeit",
        example="nicht zulassungsfähig"
    )
    description = Field(
        description="Beschreibung der Gültigkeit",
        default=None
    )

class ApprovalValidityCreate(MongoBaseModel):
    cn: str = ApprovalValidityFieldInfo.cn
    title: str = ApprovalValidityFieldInfo.title
    description: Optional[Markup] = ApprovalValidityFieldInfo.description
    origin: Optional[Origin] = CommonFieldInfo.origin

