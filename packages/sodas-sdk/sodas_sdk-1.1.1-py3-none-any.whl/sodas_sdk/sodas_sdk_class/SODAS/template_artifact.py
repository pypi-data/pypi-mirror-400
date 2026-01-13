import copy
from typing import Any, ClassVar, Optional, Type, TypeVar, cast

import requests

from sodas_sdk.core.error import (
    IndexOutOfBoundsError,
    InvalidTemplateArtifactRow,
    InvalidValueError,
    NeedToSetTemplateError,
)
from sodas_sdk.core.type import (
    IRIType,
    PaginatedResponse,
    SortOrder,
    TemplateArtifactRow,
    TemplateArtifactValue,
    TemplateDetailFunctionality,
)
from sodas_sdk.core.util import handle_error
from sodas_sdk.sodas_sdk_class.governance_class import (
    GOVERNANCE_MODEL,
    GOVERNANCE_MODEL_DTO,
)
from sodas_sdk.sodas_sdk_class.SODAS.template import Template

T = TypeVar("T", bound="TemplateArtifact")


class TemplateArtifactDTO(GOVERNANCE_MODEL_DTO):
    resourceDescriptorIri: Optional[str]
    templateIri: str
    value: TemplateArtifactValue


class TemplateArtifact(GOVERNANCE_MODEL):
    _ResourceDescriptorIRI: Optional[IRIType] = None
    _TemplateIRI: Optional[IRIType] = None
    _Value: TemplateArtifactValue = []
    _Template: Optional[Template] = None

    DTO_CLASS: ClassVar[Type[TemplateArtifactDTO]] = TemplateArtifactDTO

    @classmethod
    def configure_api_url(cls, base_url: str) -> None:
        PREFIX = "api/v1/governance/open-reference-model"
        cls.API_URL = f"{base_url}/{PREFIX}/template-artifact"
        cls.LIST_URL = f"{cls.API_URL}/list"
        cls.GET_URL = f"{cls.API_URL}/get"
        cls.CREATE_URL = f"{cls.API_URL}/create"
        cls.UPDATE_URL = f"{cls.API_URL}/update"
        cls.DELETE_URL = f"{cls.API_URL}/remove"

    async def populate_from_dto(self, dto: GOVERNANCE_MODEL_DTO) -> None:
        await super().populate_from_dto(dto)
        dto_typed = (
            dto
            if isinstance(dto, TemplateArtifactDTO)
            else TemplateArtifactDTO(**dto.model_dump(exclude_none=True))
        )

        if dto_typed.resourceDescriptorIri:
            self._ResourceDescriptorIRI = dto_typed.resourceDescriptorIri
        self._TemplateIRI = dto_typed.templateIri
        self._Value = dto_typed.value

        try:
            self._Template = await Template.get_db_record(dto_typed.templateIri)
        except Exception as e:
            handle_error(e)

    def to_dto(self) -> TemplateArtifactDTO:
        base = super().to_dto().model_dump(exclude_none=True)
        return TemplateArtifactDTO(
            **base,
            resourceDescriptorIri=self._ResourceDescriptorIRI,
            templateIri=cast(str, self._TemplateIRI),  #
            value=self._Value,
        )

    @classmethod
    async def list_db_records(
        cls: Type[T],
        page_number: int = 1,
        page_size: int = 10,
        sort_order: SortOrder = SortOrder.DESC,
        template_iri: Optional[str] = None,
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
                    "templateIri": template_iri,
                },
            )
            return await cls.list_response_to_paginated_response(response)
        except Exception as e:
            handle_error(e)

    def _set_resource_descriptor_iri(self, iri: IRIType):
        self._ResourceDescriptorIRI = iri

    def get_value(self) -> TemplateArtifactValue:
        return copy.deepcopy(self._Value)

    def get_row(self, index: int) -> TemplateArtifactRow:
        if index < 0 or index >= len(self._Value):
            raise IndexOutOfBoundsError(index)
        return copy.deepcopy(self._Value[index])

    def append_empty_row(self) -> None:
        if not self._Template:
            raise NeedToSetTemplateError()
        row: TemplateArtifactRow = {}
        for detail in self._Template.details:
            if detail.functionality is not None:
                row[detail.functionality] = None
        self._Value.append(row)

    def set_value(self, value: TemplateArtifactValue) -> None:
        if not self._Template:
            raise NeedToSetTemplateError()

        for i, row in enumerate(value):
            self._validate_row_keys(i, row)

        self._Value = copy.deepcopy(value)

    def set_field(
        self, index: int, functionality: TemplateDetailFunctionality, val: Any
    ) -> None:
        if index < 0 or index >= len(self._Value):
            raise IndexOutOfBoundsError(index)
        if functionality not in self._Value[index]:
            raise InvalidValueError(functionality)
        self._Value[index][functionality] = val

    def remove_row(self, index: int) -> None:
        if index < 0 or index >= len(self._Value):
            raise IndexOutOfBoundsError(index)
        self._Value.pop(index)

    def set_template(self, template: Template) -> None:
        self._Template = template
        self._TemplateIRI = template.iri
        self._Value = []

    def _validate_row_keys(self, index: int, row: TemplateArtifactRow) -> None:
        if not self._Template:
            raise NeedToSetTemplateError()
        expected = [d.functionality for d in self._Template.details]
        actual = list(row.keys())

        missing = [k for k in expected if k not in actual]
        extra = [k for k in actual if k not in expected]

        if missing or extra:
            raise InvalidTemplateArtifactRow(index, missing, extra)

    @property
    def template(self) -> Template:
        if not self._Template:
            raise NeedToSetTemplateError()
        return self._Template

    @property
    def template_iri(self) -> Optional[IRIType]:
        return self._TemplateIRI

    @property
    def resource_descriptor_iri(self) -> Optional[IRIType]:
        return self._ResourceDescriptorIRI
