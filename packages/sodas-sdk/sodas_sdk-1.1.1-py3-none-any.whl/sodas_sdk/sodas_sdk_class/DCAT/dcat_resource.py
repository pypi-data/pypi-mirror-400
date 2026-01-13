from typing import Any, ClassVar, List, Optional, Type, Union

from sodas_sdk.core.error import (
    InvalidProfileTypeError,
    InvalidTypeError,
    NotRecordedYetError,
    RequirementsNotSetError,
)
from sodas_sdk.core.type import (
    IDType,
    InstanceValueType,
    IRIType,
    MultiLanguageField,
    MultiLanguageKeywords,
    ProfileType,
    as_id,
    as_iri,
)
from sodas_sdk.sodas_sdk_class.DCAT.version_info import VersionInfo, VersionInfoDTO
from sodas_sdk.sodas_sdk_class.dcat_class import DCAT_MODEL, DCAT_MODEL_DTO
from sodas_sdk.sodas_sdk_class.PROF.profile import Profile
from sodas_sdk.sodas_sdk_file.thumbnail_file import ThumbnailFile


class DCAT_RESOURCE_DTO(DCAT_MODEL_DTO):
    ResourceType: Optional[str] = None
    AssetID: Optional[str] = None
    DatahubID: Optional[str] = None
    ThumbnailURL: Optional[str] = None
    AccessRights: Optional[str] = None
    Status: Optional[str] = None
    VersionNotes: Optional[str] = None
    Version: Optional[str] = None
    IsVersionOf: Optional[str] = None
    PreviousVersionID: Optional[str] = None
    NextVersionID: Optional[str] = None
    ContactPoint: Optional[str] = None
    KeywordML: Optional[MultiLanguageKeywords] = None
    LandingPage: Optional[str] = None
    Theme: Optional[str] = None
    ConformsTo: Optional[str] = None
    Creator: Optional[str] = None
    DescriptionML: Optional[MultiLanguageField] = None
    Identifier: Optional[str] = None
    IsReferencedBy: Optional[List[Any]] = None
    Language: Optional[List[Any]] = None
    License: Optional[str] = None
    Publisher: Optional[str] = None
    Rights: Optional[List[Any]] = None
    TitleML: Optional[MultiLanguageField] = None
    Type: Optional[str] = None
    HasPolicy: Optional[List[Any]] = None
    IssuerID: Optional[str] = None
    ProfileIRI: Optional[str] = None
    InstanceValue: Optional[dict] = None
    VersionInfo: Optional[List["VersionInfoDTO"]] = None  # Forward reference


class DCAT_RESOURCE(DCAT_MODEL):
    _Thumbnail: Optional[ThumbnailFile] = None
    _ResourceType: Optional[str] = None
    _AssetID: Optional[IDType] = None
    _DatahubID: Optional[IDType] = None
    _ThumbnailURL: Optional[str] = None
    _AccessRights: Optional[str] = None
    _Status: Optional[str] = None
    _VersionNotes: Optional[str] = None
    _Version: Optional[str] = None
    _IsVersionOf: Optional[IDType] = None
    _PreviousVersionID: Optional[IDType] = None
    _NextVersionID: Optional[IDType] = None
    _ContactPoint: Optional[str] = None
    _KeywordML: Optional[MultiLanguageKeywords] = {}
    _LandingPage: Optional[str] = None
    _Theme: Optional[str] = None
    _ConformsTo: Optional[str] = None
    _Creator: Optional[str] = None
    _DescriptionML: Optional[MultiLanguageField] = {}
    _Identifier: Optional[str] = None
    _IsReferencedBy: Optional[List[Any]] = []
    _Language: Optional[List[Any]] = []
    _License: Optional[str] = None
    _Publisher: Optional[str] = None
    _Rights: Optional[List[Any]] = []
    _TitleML: Optional[MultiLanguageField] = {}
    _Type: Optional[str] = None
    _HasPolicy: Optional[List[Any]] = []
    _IssuerID: Optional[str] = None
    _ProfileIRI: Optional[IRIType] = None
    _InstanceValue: Optional[InstanceValueType] = {}
    _VersionInfos: List[VersionInfo] = []

    DTO_CLASS: ClassVar[Type[DCAT_RESOURCE_DTO]] = DCAT_RESOURCE_DTO

    def to_dto(self) -> DCAT_RESOURCE_DTO:
        base = super().to_dto().model_dump(exclude_none=True)
        return DCAT_RESOURCE_DTO(
            **base,
            ResourceType=self._ResourceType,
            AssetID=self._AssetID,
            DatahubID=self._DatahubID,
            ThumbnailURL=self._ThumbnailURL,
            AccessRights=self._AccessRights,
            Status=self._Status,
            VersionNotes=self._VersionNotes,
            Version=self._Version,
            IsVersionOf=self._IsVersionOf,
            PreviousVersionID=self._PreviousVersionID,
            NextVersionID=self._NextVersionID,
            ContactPoint=self._ContactPoint,
            KeywordML=self._KeywordML,
            LandingPage=self._LandingPage,
            Theme=self._Theme,
            ConformsTo=self._ConformsTo,
            Creator=self._Creator,
            DescriptionML=self._DescriptionML,
            Identifier=self._Identifier,
            IsReferencedBy=self._IsReferencedBy if self._IsReferencedBy else None,
            Language=self._Language if self._Language else None,
            License=self._License,
            Publisher=self._Publisher,
            Rights=self._Rights if self._Rights else None,
            TitleML=self._TitleML,
            Type=self._Type,
            HasPolicy=self._HasPolicy if self._HasPolicy else None,
            IssuerID=self._IssuerID,
            ProfileIRI=self._ProfileIRI,
            InstanceValue=self._InstanceValue,
        )

    async def populate_from_dto(self, dto: DCAT_MODEL_DTO):
        await super().populate_from_dto(dto)
        dto = (
            dto
            if isinstance(dto, DCAT_RESOURCE_DTO)
            else DCAT_RESOURCE_DTO(**dto.model_dump(exclude_none=True))
        )
        self._ResourceType = dto.ResourceType
        self._AssetID = as_id(dto.AssetID) if dto.AssetID else None
        self._DatahubID = as_id(dto.DatahubID) if dto.DatahubID else None
        self._ThumbnailURL = dto.ThumbnailURL
        self._AccessRights = dto.AccessRights
        self._Status = dto.Status
        self._VersionNotes = dto.VersionNotes
        self._Version = dto.Version
        self._IsVersionOf = as_id(dto.IsVersionOf) if dto.IsVersionOf else None
        self._PreviousVersionID = (
            as_id(dto.PreviousVersionID) if dto.PreviousVersionID else None
        )
        self._NextVersionID = as_id(dto.NextVersionID) if dto.NextVersionID else None
        self._ContactPoint = dto.ContactPoint
        self._KeywordML = dto.KeywordML or {}
        self._LandingPage = dto.LandingPage
        self._Theme = dto.Theme
        self._ConformsTo = dto.ConformsTo
        self._Creator = dto.Creator
        self._DescriptionML = dto.DescriptionML or {}
        self._Identifier = dto.Identifier
        self._IsReferencedBy = dto.IsReferencedBy or []
        self._Language = dto.Language or []
        self._License = dto.License
        self._Publisher = dto.Publisher
        self._Rights = dto.Rights or []
        self._TitleML = dto.TitleML or {}
        self._Type = dto.Type
        self._HasPolicy = dto.HasPolicy or []
        self._IssuerID = dto.IssuerID
        self._ProfileIRI = as_iri(dto.ProfileIRI) if dto.ProfileIRI else None
        self._InstanceValue = dto.InstanceValue or {}

        await self.populate_version_info_from_dto(dto)

    async def populate_version_info_from_dto(self, dto: DCAT_RESOURCE_DTO):
        if dto.VersionInfo:
            self._VersionInfos = []
            for vi in dto.VersionInfo:
                vi_obj = VersionInfo()
                await vi_obj.populate_from_dto(vi)
                self._VersionInfos.append(vi_obj)

    def set_thumbnail(self, file_path: str):
        self._Thumbnail = self._Thumbnail or ThumbnailFile()
        self._Thumbnail.set_file(file_path)

    async def create_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_recorded()
        if not self.has_db_record() and self._Thumbnail:
            self._Thumbnail.upload()
            self._ThumbnailURL = self._Thumbnail.get_download_url()
        await super().create_db_record()
        self._Thumbnail = None

    async def update_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()
        if self.has_db_record() and self._Thumbnail:
            self._Thumbnail.upload()
            self._ThumbnailURL = self._Thumbnail.get_download_url()
        await super().update_db_record()
        self._Thumbnail = None

    def set_previous_version(self, prev: "DCAT_RESOURCE"):
        if not isinstance(prev, DCAT_RESOURCE):
            raise InvalidTypeError(prev, "DCAT_RESOURCE")
        if not prev.has_db_record():
            raise NotRecordedYetError(prev)
        self._PreviousVersionID = prev.id

    # Getters/Setters below — you already saw them in earlier Python versions
    # Example:

    def get_title(self, language_code: str = "ko") -> Optional[str]:
        if self._TitleML is None:
            self._TitleML = {}
        return self._TitleML.get(language_code)

    def set_title(self, title: str, language_code: str = "ko") -> None:
        if self._TitleML is None:
            self._TitleML = {}
        self._TitleML[language_code] = title

    def remove_title(self, language_code: str = "ko") -> None:
        if self._TitleML is None:
            raise RequirementsNotSetError()
        if language_code in self._TitleML:
            del self._TitleML[language_code]
        else:
            print(f'Warning: Title for language code "{language_code}" does not exist.')

    def get_description(self, language_code: str = "ko") -> Optional[str]:
        if self._DescriptionML is None:
            self._DescriptionML = {}
        return self._DescriptionML.get(language_code)

    def set_description(self, value: str, language_code: str = "ko") -> None:
        if self._DescriptionML is None:
            self._DescriptionML = {}
        self._DescriptionML[language_code] = value

    def remove_description(self, language_code: str = "ko") -> None:
        if self._DescriptionML is None:
            raise RequirementsNotSetError()
        if language_code in self._DescriptionML:
            del self._DescriptionML[language_code]
        else:
            print(
                f'Warning: Description for language code "{language_code}" does not exist.'
            )

    def get_keywords(self, language_code: str = "ko") -> List[str]:
        if self._KeywordML is None:
            self._KeywordML = {}
        return self._KeywordML.get(language_code, [])

    def set_keywords(self, keywords: List[str], language_code: str = "ko") -> None:
        if self._KeywordML is None:
            self._KeywordML = {}
        self._KeywordML[language_code] = keywords

    def add_keyword(self, keyword: str, language_code: str = "ko") -> None:
        if self._KeywordML is None:
            self._KeywordML = {}

        if language_code not in self._KeywordML:
            self._KeywordML[language_code] = []

        if keyword not in self._KeywordML[language_code]:
            self._KeywordML[language_code].append(keyword)

    def remove_keyword(self, keyword: str, language_code: str = "ko") -> None:
        if self._KeywordML is None:
            self._KeywordML = {}
        if language_code in self._KeywordML:
            self._KeywordML[language_code] = [
                k for k in self._KeywordML[language_code] if k != keyword
            ]
            if not self._KeywordML[language_code]:
                del self._KeywordML[language_code]

    async def get_dcat_profile(self) -> Union[Profile, None]:
        try:
            assert self.profile_iri
            result = await Profile.get_db_record(as_iri(self.profile_iri))
            return result
        except Exception as error:
            print("Error in get_dcat_profile:", error)
            return None

    def set_dcat_profile(self, profile: Profile) -> None:
        if profile.type != ProfileType.DCAT:
            raise InvalidProfileTypeError(profile, ProfileType.DCAT)
        if not profile.has_db_record():
            raise NotRecordedYetError(profile)
        self.profile_iri = profile.iri

    async def get_data_profile(self) -> Union[Profile, None]:
        try:
            assert self.conforms_to
            result = await Profile.get_db_record(as_iri(self.conforms_to))
            return result
        except Exception as error:
            print("Error in get_data_profile:", error)
            return None

    def set_data_profile(self, profile: Profile) -> None:
        if profile.type != ProfileType.DATA:
            raise InvalidProfileTypeError(profile, ProfileType.DATA)
        if not profile.has_db_record():
            raise NotRecordedYetError(profile)
        self.conforms_to = profile.iri

    # (continuation from existing DCAT_RESOURCE class definition)

    @property
    def version_infos(self) -> List[VersionInfo]:
        return self._VersionInfos

    @property
    def is_version_of(self) -> Optional[str]:
        return self._IsVersionOf

    @property
    def previous_version_id(self) -> Optional[str]:
        return self._PreviousVersionID

    @property
    def next_version_id(self) -> Optional[str]:
        return self._NextVersionID

    @property
    def resource_type(self) -> Optional[str]:
        return self._ResourceType

    @property
    def asset_id(self) -> Optional[str]:
        return self._AssetID

    @property
    def datahub_id(self) -> Optional[str]:
        return self._DatahubID

    @property
    def thumbnail_url(self) -> Optional[str]:
        return self._ThumbnailURL

    @property
    def access_rights(self) -> Optional[str]:
        return self._AccessRights

    @access_rights.setter
    def access_rights(self, value: str):
        self._AccessRights = value

    @property
    def status(self) -> Optional[str]:
        return self._Status

    @status.setter
    def status(self, value: str):
        self._Status = value

    @property
    def version_notes(self) -> Optional[str]:
        return self._VersionNotes

    @version_notes.setter
    def version_notes(self, value: str):
        self._VersionNotes = value

    @property
    def version(self) -> Optional[str]:
        return self._Version

    @version.setter
    def version(self, value: str):
        self._Version = value

    @property
    def contact_point(self) -> Optional[str]:
        return self._ContactPoint

    @contact_point.setter
    def contact_point(self, value: str):
        self._ContactPoint = value

    @property
    def landing_page(self) -> Optional[str]:
        return self._LandingPage

    @landing_page.setter
    def landing_page(self, value: str):
        self._LandingPage = value

    @property
    def theme(self) -> Optional[str]:
        return self._Theme

    @theme.setter
    def theme(self, value: str):
        self._Theme = value

    @property
    def conforms_to(self) -> Optional[str]:
        return self._ConformsTo

    @conforms_to.setter
    def conforms_to(self, value: str):
        self._ConformsTo = value

    @property
    def creator(self) -> Optional[str]:
        return self._Creator

    @creator.setter
    def creator(self, value: str):
        self._Creator = value

    @property
    def identifier(self) -> Optional[str]:
        return self._Identifier

    @property
    def language(self) -> Optional[List[Any]]:
        return self._Language

    @language.setter
    def language(self, value: List[Any]):
        self._Language = value

    @property
    def license(self) -> Optional[str]:
        return self._License

    @license.setter
    def license(self, value: str):
        self._License = value

    @property
    def publisher(self) -> Optional[str]:
        return self._Publisher

    @publisher.setter
    def publisher(self, value: str):
        self._Publisher = value

    @property
    def rights(self) -> Optional[List[Any]]:
        return self._Rights

    @rights.setter
    def rights(self, value: List[Any]):
        self._Rights = value

    @property
    def type(self) -> Optional[str]:
        return self._Type

    @type.setter
    def type(self, value: str):
        self._Type = value

    @property
    def has_policy(self) -> Optional[List[Any]]:
        return self._HasPolicy

    @has_policy.setter
    def has_policy(self, value: List[Any]):
        self._HasPolicy = value

    @property
    def issuer_id(self) -> Optional[str]:
        return self._IssuerID

    @issuer_id.setter
    def issuer_id(self, value: str):
        self._IssuerID = value

    @property
    def profile_iri(self) -> Optional[IRIType]:
        return self._ProfileIRI

    @profile_iri.setter
    def profile_iri(self, value: str):
        self._ProfileIRI = as_iri(value)

    @property
    def instance_value(self) -> Optional[InstanceValueType]:
        return self._InstanceValue

    @instance_value.setter
    def instance_value(self, value: InstanceValueType):
        self._InstanceValue = value

    def set_instance_value(self, name: str, value: str):
        if self._InstanceValue is None:
            self._InstanceValue = {}
        self._InstanceValue[name] = value

    def get_instance_value(self, name: str) -> Optional[str]:
        if not self._InstanceValue:
            raise RequirementsNotSetError()
        return self._InstanceValue.get(name)
