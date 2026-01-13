import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar

from dateutil.parser import parse
from pydantic import BaseModel

from sodas_sdk.core.error import InvalidDateObjectError, InvalidDateStringError

# === ID and IRI ===

IDType = str
IRIType = str

uuid_regex = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I
)


def as_id(value: str) -> IDType:
    if not uuid_regex.match(value):
        raise ValueError(f"Invalid UUID format: '{value}'")
    return value


def as_ids(values: List[str]) -> List[IDType]:
    return [as_id(v) for v in values]


def as_iri(value: str) -> IRIType:
    return value


# === Date Handling ===

DateString = str  # alias for clarity

iso_8601_pattern = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


def to_date_string(date: Optional[datetime]) -> DateString:
    if not isinstance(date, datetime):
        raise InvalidDateObjectError(date)
    value = date.isoformat().replace("+00:00", "Z")
    if not iso_8601_pattern.match(value):
        raise InvalidDateStringError(value)
    return value


def to_date(date_string: DateString) -> datetime:
    try:
        return parse(date_string)
    except Exception:
        raise InvalidDateStringError(date_string)


# === Multilingual fields ===

MultiLanguageField = Dict[str, str]
MultiLanguageKeywords = Dict[str, List[str]]
InstanceValueType = Dict[str, str]


# === Enums ===


class SortOrder(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


class ResourceDescriptorRole(str, Enum):
    VOCABULARY = "vocabulary"
    TYPE = "type"
    SCHEMA = "schema"
    CONSTRAINT = "constraint"
    VALIDATION = "validation"
    MAPPING = "mapping"
    EXAMPLE = "example"
    SPECIFICATION = "specification"
    GUIDANCE = "guidance"


class ProfileType(str, Enum):
    DCAT = "dcat"
    DATA = "data"


class ArtifactType(str, Enum):
    TEMPLATE = "template"
    FILE = "file"


class TemplateDetailFunctionality(str, Enum):
    ORIGIN = "origin"
    NAMESPACE = "namespaceIRI"
    TERM = "term"
    DESCRIPTION = "description"
    NAME = "name"
    LABEL = "label"
    VALUE = "value"
    TYPE = "type"
    REQUIRED = "required"
    FIELD_TERM = "fieldTerm"
    FIELD = "field"
    REGEX = "regex"
    MEASURE = "measure"
    TARGET_PROFILE = "targetProfile"
    TARGET_FIELD = "targetField"
    CONVERSION = "conversion"


# === Paginated Response ===

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    list: List[T]


# === TemplateArtifact Related Types ===
TemplateArtifactRow = Dict[TemplateDetailFunctionality, Any]
TemplateArtifactValue = List[TemplateArtifactRow]
