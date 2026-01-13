from typing import Any, ClassVar, Optional, Type, TypeVar, cast

import requests

from sodas_sdk.core.type import (
    IDType,
    PaginatedResponse,
    SortOrder,
    TemplateDetailFunctionality,
)
from sodas_sdk.core.util import handle_error
from sodas_sdk.sodas_sdk_class.governance_class import (
    GOVERNANCE_MODEL,
    GOVERNANCE_MODEL_DTO,
)

T = TypeVar("T", bound="TemplateDetail")


class TemplateDetailDTO(GOVERNANCE_MODEL_DTO):
    templateId: Optional[str]
    ordering: Optional[int]
    functionality: Optional[TemplateDetailFunctionality]
    columnName: Optional[str]
    relativeWidth: Optional[int]
    placeholder: Optional[str]


class TemplateDetail(GOVERNANCE_MODEL):
    _TemplateID: Optional[IDType] = None
    _Ordering: Optional[int] = None
    _Functionality: Optional[TemplateDetailFunctionality] = None
    _ColumnName: Optional[str] = None
    _RelativeWidth: Optional[int] = 1
    _Placeholder: Optional[str] = None

    DTO_CLASS: ClassVar[Type[TemplateDetailDTO]] = TemplateDetailDTO

    @classmethod
    def configure_api_url(cls, base_url: str) -> None:
        PREFIX = "api/v1/governance/open-reference-model"
        cls.API_URL = f"{base_url}/{PREFIX}/template/detail"
        cls.LIST_URL = f"{cls.API_URL}/list"
        cls.GET_URL = f"{cls.API_URL}/get"
        cls.CREATE_URL = f"{cls.API_URL}/create"
        cls.UPDATE_URL = f"{cls.API_URL}/update"
        cls.DELETE_URL = f"{cls.API_URL}/remove"

    async def populate_from_dto(self, dto: GOVERNANCE_MODEL_DTO) -> None:
        await super().populate_from_dto(dto)
        dto = (
            dto
            if isinstance(dto, TemplateDetailDTO)
            else TemplateDetailDTO(**dto.model_dump(exclude_none=True))
        )
        self._TemplateID = dto.templateId
        self._Ordering = dto.ordering
        self._Functionality = dto.functionality
        self._ColumnName = dto.columnName
        self._RelativeWidth = dto.relativeWidth
        self._Placeholder = dto.placeholder

    def to_dto(self) -> TemplateDetailDTO:
        base = super().to_dto().model_dump(exclude_none=True)
        return TemplateDetailDTO(
            **base,
            templateId=self._TemplateID,
            ordering=self._Ordering,
            functionality=self._Functionality,
            columnName=self._ColumnName,
            relativeWidth=self._RelativeWidth,
            placeholder=self._Placeholder,
        )

    @classmethod
    async def list_db_records(
        cls: Type[T],
        page_number: int = 1,
        page_size: int = 10,
        sort_order: SortOrder = SortOrder.DESC,
        template_id: Optional[str] = None,
        *args: Any,
    ) -> PaginatedResponse[T]:
        cls.throw_error_if_api_url_not_set()
        url: str = cast(str, cls.LIST_URL)
        try:
            response = requests.get(
                url,
                params={
                    "offset": (page_number - 1) * page_size,
                    "limit": page_size,
                    "ordered": sort_order.value,
                    "templateId": template_id,
                },
            )
            return await cls.list_response_to_paginated_response(response)
        except Exception as e:
            handle_error(e)

    @property
    def template_id(self) -> Optional[IDType]:
        return self._TemplateID

    @template_id.setter
    def template_id(self, value: str) -> None:
        self._TemplateID = value

    @property
    def ordering(self) -> Optional[int]:
        return self._Ordering

    @ordering.setter
    def ordering(self, value: int) -> None:
        self._Ordering = value

    @property
    def functionality(self) -> Optional[TemplateDetailFunctionality]:
        return self._Functionality

    @functionality.setter
    def functionality(self, value: TemplateDetailFunctionality) -> None:
        self._Functionality = value

    @property
    def column_name(self) -> Optional[str]:
        return self._ColumnName

    @column_name.setter
    def column_name(self, value: str) -> None:
        self._ColumnName = value

    @property
    def relative_width(self) -> Optional[int]:
        return self._RelativeWidth

    @relative_width.setter
    def relative_width(self, value: int) -> None:
        self._RelativeWidth = value

    @property
    def placeholder(self) -> Optional[str]:
        return self._Placeholder

    @placeholder.setter
    def placeholder(self, value: str) -> None:
        self._Placeholder = value
