from typing import Any, ClassVar, List, Optional, Type, TypeVar, cast

import requests

from sodas_sdk.core.error import (
    IndexOutOfBoundsError,
    TemplateDetailFunctionalityAlreadyExist,
)
from sodas_sdk.core.type import (
    IRIType,
    PaginatedResponse,
    ProfileType,
    ResourceDescriptorRole,
    SortOrder,
    TemplateDetailFunctionality,
)
from sodas_sdk.core.util import LARGE_ENOUGH_NUMBER, handle_error
from sodas_sdk.sodas_sdk_class.governance_class import (
    GOVERNANCE_MODEL,
    GOVERNANCE_MODEL_DTO,
)
from sodas_sdk.sodas_sdk_class.SODAS.template_detail import TemplateDetail

T = TypeVar("T", bound="Template")


class TemplateDTO(GOVERNANCE_MODEL_DTO):
    role: ResourceDescriptorRole
    type: ProfileType
    name: str
    description: Optional[str]
    defaultTemplate: bool


class Template(GOVERNANCE_MODEL):
    _Role: Optional[ResourceDescriptorRole] = None
    _Type: Optional[ProfileType] = None
    _Name: Optional[str] = None
    _Description: Optional[str] = None
    _DefaultTemplate: bool = False
    _FetchedTemplateDetailIRIs: List[IRIType] = []
    _TemplateDetails: List[TemplateDetail] = []

    DTO_CLASS: ClassVar[Type[TemplateDTO]] = TemplateDTO

    @classmethod
    def configure_api_url(cls, base_url: str) -> None:
        PREFIX = "api/v1/governance/open-reference-model"
        cls.API_URL = f"{base_url}/{PREFIX}/template"
        cls.LIST_URL = f"{cls.API_URL}/list"
        cls.GET_URL = f"{cls.API_URL}/get"
        cls.CREATE_URL = f"{cls.API_URL}/create"
        cls.UPDATE_URL = f"{cls.API_URL}/update"
        cls.DELETE_URL = f"{cls.API_URL}/remove"

    async def populate_from_dto(self, dto: GOVERNANCE_MODEL_DTO) -> None:
        await super().populate_from_dto(dto)
        dto = (
            dto
            if isinstance(dto, TemplateDTO)
            else TemplateDTO(**dto.model_dump(exclude_none=True))
        )
        self._Role = dto.role
        self._Type = dto.type
        self._Name = dto.name
        self._Description = dto.description
        self._DefaultTemplate = dto.defaultTemplate
        await self._populate_details_from_dto(dto)

    async def _populate_details_from_dto(self, dto: TemplateDTO) -> None:
        if dto.id:
            response = await TemplateDetail.list_db_records(
                page_number=1,
                page_size=LARGE_ENOUGH_NUMBER,
                sort_order=SortOrder.ASC,
                template_id=dto.id,
            )
            self._TemplateDetails = response.list
            self._FetchedTemplateDetailIRIs = [
                d.iri for d in self._TemplateDetails if d.iri is not None
            ]

    def to_dto(self) -> TemplateDTO:
        base = super().to_dto().model_dump(exclude_none=True)
        return TemplateDTO(
            **base,
            role=cast(ResourceDescriptorRole, self._Role),
            type=cast(ProfileType, self._Type),
            name=cast(str, self._Name),
            description=self._Description,
            defaultTemplate=self._DefaultTemplate,
        )

    @classmethod
    async def list_db_records(
        cls,
        page_number: int = 1,
        page_size: int = 10,
        sort_order: SortOrder = SortOrder.DESC,
        role: Optional[ResourceDescriptorRole] = None,
        type_: Optional[ProfileType] = None,
        *additional_args: Any,
    ) -> PaginatedResponse["Template"]:
        cls.throw_error_if_api_url_not_set()
        url = cast(str, cls.LIST_URL)
        try:
            response = requests.get(
                url,
                params={
                    "offset": (page_number - 1) * page_size,
                    "limit": page_size,
                    "ordered": sort_order.value,
                    "role": role,
                    "type": type_,
                },
            )
            return await cls.list_response_to_paginated_response(response)
        except Exception as e:
            handle_error(e)

    async def create_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_recorded()

        details = self._TemplateDetails
        await super().create_db_record()
        self._TemplateDetails = details

        if self._TemplateDetails:
            for detail in self._TemplateDetails:
                detail.template_id = self.id
                await detail.create_db_record()
                self._FetchedTemplateDetailIRIs.append(cast(str, detail.iri))

    async def update_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()

        details = self._TemplateDetails
        await super().update_db_record()
        self._TemplateDetails = details

        if self._TemplateDetails:
            for detail in self._TemplateDetails:
                detail.template_id = self.id
                if detail.has_db_record():
                    await detail.update_db_record()
                else:
                    await detail.create_db_record()
                    self._FetchedTemplateDetailIRIs.append(cast(str, detail.iri))
            await self._delete_not_maintained_details()

    async def delete_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()

        await self._delete_not_maintained_details()
        self._TemplateDetails.clear()
        await super().delete_db_record()

    async def _delete_not_maintained_details(self):
        if self._FetchedTemplateDetailIRIs:
            maintained = [d.iri for d in self._TemplateDetails if d.iri is not None]
            to_delete = [
                iri for iri in self._FetchedTemplateDetailIRIs if iri not in maintained
            ]
            details = [await TemplateDetail.get_db_record(iri) for iri in to_delete]
            for detail in details:
                await detail.delete_db_record()
            self._FetchedTemplateDetailIRIs = maintained

    def get_detail_using_index(self, index: int) -> TemplateDetail:
        if index < 0 or index >= len(self._TemplateDetails):
            raise IndexOutOfBoundsError(index)
        return self._TemplateDetails[index]

    def create_detail(
        self, functionality: TemplateDetailFunctionality
    ) -> TemplateDetail:
        if not self._TemplateDetails:
            self._TemplateDetails = []
        if any(d.functionality == functionality for d in self._TemplateDetails):
            raise TemplateDetailFunctionalityAlreadyExist(functionality)
        detail = TemplateDetail()
        detail.ordering = len(self._TemplateDetails)
        detail.relative_width = 1
        detail.functionality = functionality
        self._TemplateDetails.append(detail)
        return detail

    def remove_detail_using_index(self, index: int) -> None:
        if index < 0 or index >= len(self._TemplateDetails):
            raise IndexOutOfBoundsError(index)
        self._TemplateDetails.pop(index)
        self._sort_details_using_ordering()
        for i, detail in enumerate(self._TemplateDetails):
            detail.ordering = i

    def _sort_details_using_ordering(self) -> None:
        self._TemplateDetails.sort(key=lambda detail: detail.ordering or 0)

    @property
    def role(self) -> Optional[ResourceDescriptorRole]:
        return self._Role

    @role.setter
    def role(self, value: ResourceDescriptorRole) -> None:
        self._Role = value

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
    def description(self, value: Optional[str]) -> None:
        self._Description = value

    @property
    def default_template(self) -> bool:
        return self._DefaultTemplate

    @default_template.setter
    def default_template(self, value: bool) -> None:
        self._DefaultTemplate = value

    @property
    def details(self) -> List[TemplateDetail]:
        return self._TemplateDetails

    @property
    def functionality_list(self) -> List[TemplateDetailFunctionality]:
        return [
            d.functionality
            for d in self._TemplateDetails
            if d.functionality is not None
        ]
