import copy
from typing import Any, ClassVar, List, Optional, Type, TypeVar, cast

import requests
from pydantic import Field

from sodas_sdk.core.error import (
    NotInitializedError,
    NotTemplateBasedResourceDescriptor,
    ResourceRoleDescriptorAlreadyExist,
    ResourceRoleDescriptorNotExist,
)
from sodas_sdk.core.type import (
    IRIType,
    MultiLanguageKeywords,
    PaginatedResponse,
    ProfileType,
    ResourceDescriptorRole,
    SortOrder,
    TemplateArtifactValue,
)
from sodas_sdk.core.util import LARGE_ENOUGH_NUMBER, destroy, handle_error
from sodas_sdk.sodas_sdk_class.governance_class import (
    GOVERNANCE_MODEL,
    GOVERNANCE_MODEL_DTO,
)
from sodas_sdk.sodas_sdk_class.PROF.options import ProfileOptions
from sodas_sdk.sodas_sdk_class.PROF.resource_descriptor import ResourceDescriptor

T = TypeVar("T", bound="Profile")


class ProfileDTO(GOVERNANCE_MODEL_DTO):
    type: ProfileType
    isProfileOf: Optional[IRIType] = None
    keywordMl: Optional[MultiLanguageKeywords] = None
    name: str
    description: Optional[str] = None
    hasToken: Optional[str] = None


class Profile(GOVERNANCE_MODEL):
    MAPPING_API_URL: ClassVar[Optional[str]] = None

    _Type: Optional[ProfileType] = None
    _IsProfileOf: Optional[IRIType] = None
    _KeywordML: Optional[MultiLanguageKeywords] = None
    _Name: Optional[str] = None
    _Description: Optional[str] = None
    _HasToken: Optional[str] = None

    _FetchedResourceDescriptorIRIs: List[IRIType] = []
    _ResourceDescriptors: List[ResourceDescriptor] = []

    Options: ProfileOptions = Field(default_factory=ProfileOptions)

    DTO_CLASS: ClassVar[Type[ProfileDTO]] = ProfileDTO

    @classmethod
    def configure_api_url(cls, base_url: str) -> None:
        prefix = "api/v1/governance/open-reference-model"
        cls.API_URL = f"{base_url}/{prefix}/profile"
        cls.LIST_URL = f"{cls.API_URL}/list"
        cls.GET_URL = f"{cls.API_URL}/get"
        cls.CREATE_URL = f"{cls.API_URL}/create"
        cls.UPDATE_URL = f"{cls.API_URL}/update"
        cls.DELETE_URL = f"{cls.API_URL}/remove"

    @classmethod
    def configure_mapping_api_url(cls, url: str) -> None:
        cls.MAPPING_API_URL = url

    def to_dto(self) -> ProfileDTO:
        assert self._Type is not None
        assert self._Name is not None
        return ProfileDTO(
            **super().to_dto().model_dump(),
            type=self._Type,
            isProfileOf=self._IsProfileOf,
            keywordMl=self._KeywordML,
            name=self._Name,
            description=self._Description,
            hasToken=self._HasToken,
        )

    async def populate_from_dto(self, dto: GOVERNANCE_MODEL_DTO) -> None:
        await super().populate_from_dto(dto)
        dto = (
            dto
            if isinstance(dto, ProfileDTO)
            else ProfileDTO(**dto.model_dump(exclude_none=True))
        )
        self._Type = dto.type
        self._IsProfileOf = dto.isProfileOf
        self._KeywordML = dto.keywordMl or {}
        self._Name = dto.name
        self._Description = dto.description
        self._HasToken = dto.hasToken
        await self.__populate_resource_descriptors_from_dto(dto)

    async def __populate_resource_descriptors_from_dto(self, dto: ProfileDTO) -> None:
        if dto.id:
            paginated: PaginatedResponse[ResourceDescriptor] = (
                await ResourceDescriptor.list_db_records(
                    1, LARGE_ENOUGH_NUMBER, SortOrder.ASC, None, dto.id
                )
            )
            self._ResourceDescriptors = paginated.list
            for rd in self._ResourceDescriptors:
                rd._set_profile(self)
                if rd.use_template:
                    self.Options.update(rd)
                self._FetchedResourceDescriptorIRIs = [
                    iri
                    for iri in (rd.iri for rd in self._ResourceDescriptors)
                    if iri is not None
                ]

    async def create_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_recorded()
        self.validate_template_resource_descriptors()
        descriptors = self._ResourceDescriptors
        await super().create_db_record()
        self._ResourceDescriptors = descriptors
        for descriptor in self._ResourceDescriptors:
            descriptor.profile_id = self.id
            await descriptor.create_db_record()
            self._FetchedResourceDescriptorIRIs.append(cast(str, descriptor.iri))

    def validate_template_resource_descriptors(self) -> None:
        for descriptor in self._ResourceDescriptors:
            if descriptor.use_template:
                descriptor.validate_artifact_value()

    async def delete_not_maintained_resource_descriptors(self) -> None:
        if self._FetchedResourceDescriptorIRIs:
            existing = set(self._FetchedResourceDescriptorIRIs)
            maintained = {d.iri for d in self._ResourceDescriptors if d.iri is not None}
            to_delete = existing - maintained
            for iri in to_delete:
                descriptor = await ResourceDescriptor.get_db_record(iri)
                await descriptor.delete_db_record()
            self._FetchedResourceDescriptorIRIs = list(maintained)

    async def update_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()
        try:
            descriptors = self._ResourceDescriptors
            await super().update_db_record()
            self._ResourceDescriptors = descriptors
            for descriptor in self._ResourceDescriptors:
                descriptor.profile_id = self.id
                if descriptor.has_db_record():
                    await descriptor.update_db_record()
                else:
                    await descriptor.create_db_record()
                    self._FetchedResourceDescriptorIRIs.append(
                        cast(str, descriptor.iri)
                    )
            await self.delete_not_maintained_resource_descriptors()
        except Exception as e:
            raise e

    async def delete_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()
        await self.delete_not_maintained_resource_descriptors()
        for descriptor in self._ResourceDescriptors:
            destroy(descriptor)
        await super().delete_db_record()

    @classmethod
    async def list_db_records(
        cls: Type[T],
        page_number: int = 1,
        page_size: int = 10,
        sort_order: SortOrder = SortOrder.DESC,
        type: Optional[ProfileType] = None,
        name: Optional[str] = None,
        *args: Any,
    ) -> PaginatedResponse[T]:
        cls.throw_error_if_api_url_not_set()
        url = cast(str, cls.LIST_URL)
        try:
            response = requests.get(
                url,
                params={
                    "offset": (page_number - 1) * page_size,
                    "limit": page_size,
                    "ordered": sort_order.value,
                    "type": type,
                    "name": name,
                },
            )
            return await cls.list_response_to_paginated_response(response)
        except Exception as e:
            handle_error(e)

    @classmethod
    async def get_all_profiles(cls: Type[T], type: ProfileType) -> List[T]:
        result = await cls.list_db_records(
            page_number=1,
            page_size=LARGE_ENOUGH_NUMBER,
            sort_order=SortOrder.DESC,
            type=type,
        )
        return result.list

    def get_extended(self) -> "Profile":
        self.throw_error_if_not_recorded()
        result = Profile()
        # Ensure _Type is not None before assignment
        if self._Type is None:
            raise ValueError("Type must not be None when calling get_extended")
        result.type = self._Type

        # Copying multi-language keywords deeply
        result._KeywordML = copy.deepcopy(self._KeywordML)

        # Ensure _Name is not None before assignment
        if self._Name is None:
            raise ValueError("Name must not be None when calling get_extended")
        result.name = self._Name

        # If optional fields are None, set defaults or skip assignment
        result.description = self._Description if self._Description is not None else ""
        result.has_token = self._HasToken if self._HasToken is not None else ""

        extended_descriptors = []
        for descriptor in self._ResourceDescriptors:
            extended_descriptors.append(descriptor.get_extended())

        result._ResourceDescriptors = extended_descriptors
        result._IsProfileOf = self.iri
        return result

    def create_resource_descriptor(
        self, role: ResourceDescriptorRole
    ) -> ResourceDescriptor:
        if any(rd.has_role == role for rd in self._ResourceDescriptors):
            raise ResourceRoleDescriptorAlreadyExist(role)
        rd = ResourceDescriptor()
        rd._set_profile(self)
        rd._HasRole = role
        rd.set_to_use_template()
        self._ResourceDescriptors.append(rd)
        return rd

    def get_resource_descriptor_of_role(
        self, role: ResourceDescriptorRole
    ) -> Optional[ResourceDescriptor]:
        return next(
            (rd for rd in self._ResourceDescriptors if rd.has_role == role), None
        )

    def get_template_descriptor_value_of_role(
        self, role: ResourceDescriptorRole
    ) -> TemplateArtifactValue:
        rd = self.get_resource_descriptor_of_role(role)
        if not rd:
            raise ResourceRoleDescriptorNotExist(role)
        if not rd.use_template:
            raise NotTemplateBasedResourceDescriptor(rd)
        return rd.get_artifact_value()

    def remove_resource_descriptor_using_role(
        self, role: ResourceDescriptorRole
    ) -> None:
        if self._ResourceDescriptors is None:
            raise NotInitializedError("ResourceDescriptors")
        index = next(
            (
                i
                for i, rd in enumerate(self._ResourceDescriptors)
                if rd.has_role == role
            ),
            -1,
        )
        if index == -1:
            raise ResourceRoleDescriptorNotExist(role)
        del self._ResourceDescriptors[index]

    def set_keywords(self, keywords: List[str], language_code: str = "ko") -> None:
        if self._KeywordML is None:
            self._KeywordML = {}
        self._KeywordML[language_code] = keywords

    def get_keywords(self, language_code: str = "ko") -> List[str]:
        if self._KeywordML is None:
            self._KeywordML = {}
        return self._KeywordML.get(language_code, [])

    def add_keyword(self, keyword: str, language_code: str = "ko") -> None:
        if self._KeywordML is None:
            self._KeywordML = {}

        if language_code not in self._KeywordML:
            self._KeywordML[language_code] = []

        if keyword not in self._KeywordML[language_code]:
            self._KeywordML[language_code].append(keyword)

    def remove_keyword(self, keyword: str, language_code: str = "ko") -> None:
        if self._KeywordML is not None and language_code in self._KeywordML:
            self._KeywordML[language_code] = [
                k for k in self._KeywordML[language_code] if k != keyword
            ]
            if not self._KeywordML[language_code]:
                del self._KeywordML[language_code]

    # Properties
    @property
    def type(self) -> Optional[ProfileType]:
        return self._Type

    @type.setter
    def type(self, value: ProfileType) -> None:
        self._Type = value

    @property
    def name(self) -> Optional[str]:
        return self._Name

    @name.setter
    def name(self, value: str) -> None:
        self._Name = value

    @property
    def description(self) -> Optional[str]:
        return self._Description

    @description.setter
    def description(self, value: str) -> None:
        self._Description = value

    @property
    def has_token(self) -> Optional[str]:
        return self._HasToken

    @has_token.setter
    def has_token(self, value: str) -> None:
        self._HasToken = value

    @property
    def resource_descriptors(self) -> List[ResourceDescriptor]:
        return self._ResourceDescriptors
