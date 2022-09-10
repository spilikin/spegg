from enum import Enum, auto
from .approval_object import *
from .approval_object_version import *
from .approval_validity import *
from .common import *

class CollectionNames(str, Enum):
  ApprovalObject = "ApprovalObject"
  ApprovalObjectVersion = "ApprovalObjectVersion"
  ApprovalValidity = "ApprovalValidity"
