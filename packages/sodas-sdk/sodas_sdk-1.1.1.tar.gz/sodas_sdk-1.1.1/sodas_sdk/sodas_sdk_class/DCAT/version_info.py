from typing import List, Optional

from pydantic import BaseModel

from sodas_sdk.core.error import RequirementsNotSetError
from sodas_sdk.core.type import (
    IDType,
    IRIType,
    MultiLanguageField,
    MultiLanguageKeywords,
    as_id,
    as_iri,
)


class VersionInfoDTO(BaseModel):
    ID: Optional[str] = None
    TitleML: Optional[MultiLanguageField] = None
    DescriptionML: Optional[MultiLanguageField] = None
    IRI: Optional[str] = None
    KeywordML: Optional[MultiLanguageKeywords] = None
    ResourceType: Optional[str] = None
    VersionNotes: Optional[str] = None
    Version: Optional[str] = None
    IsVersionOf: Optional[str] = None
    NextVersionID: Optional[str] = None
    PreviousVersionID: Optional[str] = None


class VersionInfo(BaseModel):
    _ID: Optional[IDType] = None
    _TitleML: Optional[MultiLanguageField] = {}
    _DescriptionML: Optional[MultiLanguageField] = {}
    _IRI: Optional[IRIType] = None
    _KeywordML: Optional[MultiLanguageKeywords] = {}
    _ResourceType: Optional[str] = None
    _VersionNotes: Optional[str] = None
    _Version: Optional[str] = None
    _IsVersionOf: Optional[str] = None
    _NextVersionID: Optional[str] = None
    _PreviousVersionID: Optional[str] = None

    async def populate_from_dto(self, dto: VersionInfoDTO) -> None:
        if dto.ID:
            self._ID = as_id(dto.ID)
        if dto.TitleML:
            self._TitleML = dto.TitleML
        if dto.DescriptionML:
            self._DescriptionML = dto.DescriptionML
        if dto.IRI:
            self._IRI = as_iri(dto.IRI)
        if dto.KeywordML:
            self._KeywordML = dto.KeywordML
        if dto.ResourceType:
            self._ResourceType = dto.ResourceType
        if dto.VersionNotes:
            self._VersionNotes = dto.VersionNotes
        if dto.Version:
            self._Version = dto.Version
        if dto.IsVersionOf:
            self._IsVersionOf = dto.IsVersionOf
        if dto.NextVersionID:
            self._NextVersionID = dto.NextVersionID
        if dto.PreviousVersionID:
            self._PreviousVersionID = dto.PreviousVersionID

    @property
    def id(self) -> Optional[str]:
        return self._ID

    def get_title(self, language_code: str = "ko") -> Optional[str]:
        if not self._TitleML:
            raise RequirementsNotSetError()
        return self._TitleML.get(language_code)

    def get_description(self, language_code: str = "ko") -> Optional[str]:
        if not self._DescriptionML:
            raise RequirementsNotSetError()
        return self._DescriptionML.get(language_code)

    @property
    def iri(self) -> Optional[str]:
        return self._IRI

    def get_keywords(self, language_code: str = "ko") -> List[str]:
        if self._KeywordML is None:
            raise RequirementsNotSetError()
        return self._KeywordML.get(language_code, [])

    @property
    def resource_type(self) -> Optional[str]:
        return self._ResourceType

    @property
    def version_notes(self) -> Optional[str]:
        return self._VersionNotes

    @property
    def version(self) -> Optional[str]:
        return self._Version

    @property
    def is_version_of(self) -> Optional[str]:
        return self._IsVersionOf

    @property
    def next_version_id(self) -> Optional[str]:
        return self._NextVersionID

    @property
    def previous_version_id(self) -> Optional[str]:
        return self._PreviousVersionID
