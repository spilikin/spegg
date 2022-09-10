from datetime import datetime
from typing import Optional
from pydantic import Field

from .common import CommonFieldInfo, MongoBaseModel, Origin, PyObjectId

class ApprovalObjectVersionFieldInfo:
    cn = Field(
        description="Kanonischer Name der Produkttypversion, bestehend aus kanonischem Namen des Produkttyps und der Versionsnummer",
        example="gemProdT_eRp_FD_PTV_1.3.0-0"
    )
    version = Field(
        description="Versionsnummer",
        example="1.3.0-0"
    )
    typeId = Field(
        description="Referenz zum Zulassungstyp, wessen Version dieser Objekt beschreibt",
    )
    validityId = Field(
        description="Aktuelle Gültigkeit dieser Version",
    )
    approvableFrom = Field(
        description="Früheste Zeitpunkt ab wann die Zulassung möglich ist",
        default=None
    )
    approvableTo = Field(
        description="Zeitpunkt bis wann die Zulassung möglich ist",
        default=None
    )

class ApprovalObjectVersionCreate(MongoBaseModel):
    cn: str = ApprovalObjectVersionFieldInfo.cn
    version: str = ApprovalObjectVersionFieldInfo.version
    typeId: PyObjectId = ApprovalObjectVersionFieldInfo.typeId
    validityId: PyObjectId = ApprovalObjectVersionFieldInfo.validityId
    origin: Optional[Origin] = CommonFieldInfo.origin
    created: datetime = CommonFieldInfo.created
    updated: datetime = CommonFieldInfo.updated
    approvableFrom: Optional[datetime] = ApprovalObjectVersionFieldInfo.approvableFrom
    approvableTo: Optional[datetime] = ApprovalObjectVersionFieldInfo.approvableTo