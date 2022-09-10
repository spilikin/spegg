from typing import Optional
from bson.objectid import ObjectId
from pydantic import BaseModel, Field

class MongoBaseModel(BaseModel):
  class Config:
    json_encoders = {
      ObjectId: lambda v: str(v),
    }

class PyObjectId(ObjectId):
  @classmethod
  def __get_validators__(cls):
    yield cls.validate
    
  @classmethod
  def validate(cls, v):
    if not ObjectId.is_valid(v):
      raise ValueError("Invalid objectid")
    return ObjectId(v)

  @classmethod
  def __modify_schema__(cls, field_schema):
    field_schema.update(type="string")

class Markup(MongoBaseModel):
  source = ""
  format = "html"

class Origin(MongoBaseModel):
  originName: str
  originId: str
  originUrl: Optional[str] = None

class CommonFieldInfo:
  origin = Field(
    description="Primäre Quelle für die Daten dieses Objekts",
  )
  created = Field(
    description="Datum und Uhrzeit der ursprünglichen Erstellung des Objekts",
  )
  updated = Field(
    description="Datum und Uhrzeit der der letzten Aktualisierung",
  )
