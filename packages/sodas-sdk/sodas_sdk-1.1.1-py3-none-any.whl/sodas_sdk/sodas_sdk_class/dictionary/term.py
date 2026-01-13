from typing import Any, ClassVar, Optional, Type, TypeVar, cast

import requests

from sodas_sdk.core.error import (
    DeleteRecordFailError,
    NeedToSetFieldError,
    NotRecordedYetError,
)
from sodas_sdk.core.type import (
    IDType,
    IRIType,
    PaginatedResponse,
    SortOrder,
    as_id,
    as_iri,
)
from sodas_sdk.core.util import handle_error
from sodas_sdk.sodas_sdk_class.governance_class import (
    GOVERNANCE_MODEL,
    GOVERNANCE_MODEL_DTO,
)

T = TypeVar("T", bound="Term")


class TermDTO(GOVERNANCE_MODEL_DTO):
    termIri: Optional[str] = None
    vocabularyId: str
    name: str
    description: Optional[str] = None


class Term(GOVERNANCE_MODEL):
    _TermIRI: Optional[IRIType] = None
    _VocabularyID: Optional[IDType] = None
    _Name: Optional[str] = None
    _Description: Optional[str] = None
    _VocabularyIRI: Optional[IRIType] = None

    DTO_CLASS: ClassVar[Type[TermDTO]] = TermDTO

    @classmethod
    def configure_api_url(cls, base_url: str) -> None:
        PREFIX = "api/v1/governance/dictionary"
        cls.API_URL = f"{base_url}/{PREFIX}/term"
        cls.LIST_URL = f"{cls.API_URL}/list"
        cls.GET_URL = f"{cls.API_URL}/get"
        cls.CREATE_URL = f"{cls.API_URL}/create"
        cls.UPDATE_URL = f"{cls.API_URL}/update"
        cls.DELETE_URL = f"{cls.API_URL}/remove"

    async def populate_from_dto(self, dto: GOVERNANCE_MODEL_DTO) -> None:
        await super().populate_from_dto(dto)
        dto = (
            dto
            if isinstance(dto, TermDTO)
            else TermDTO(**dto.model_dump(exclude_none=True))
        )
        if dto.termIri:
            self._TermIRI = as_iri(dto.termIri)
        self._VocabularyID = as_id(dto.vocabularyId)
        self._Name = dto.name
        self._Description = dto.description

    def to_dto(self) -> TermDTO:
        base = super().to_dto().model_dump(exclude_none=True)
        return TermDTO(
            **base,
            termIri=self._TermIRI,
            vocabularyId=cast(str, self._VocabularyID),
            name=cast(str, self._Name),
            description=self._Description,
        )

    @classmethod
    async def list_db_records(
        cls: Type[T],
        page_number: int = 1,
        page_size: int = 10,
        sort_order: SortOrder = SortOrder.DESC,
        vocabulary_id: Optional[str] = None,
        *args: Any,
    ) -> PaginatedResponse[T]:
        cls.throw_error_if_api_url_not_set()
        try:
            response = requests.get(
                cast(str, cls.LIST_URL),
                params={
                    "offset": (page_number - 1) * page_size,
                    "limit": page_size,
                    "ordered": sort_order.value,
                    "vocabularyId": vocabulary_id,
                },
            )
            return await cls.list_response_to_paginated_response(response)
        except Exception as e:
            handle_error(e)

    async def create_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_recorded()
        try:
            response = requests.post(
                cast(str, self.__class__.CREATE_URL),
                json=self.to_dto().model_dump(exclude_none=True),
                headers={"Content-Type": "application/json"},
            )
            await self.populate_from_dto(TermDTO(**response.json()))
        except Exception as e:
            handle_error(e)

    async def update_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()
        dto_dict = self.to_dto().model_dump(
            exclude={"iri", "issued", "modified"}, exclude_none=True
        )

        try:
            response = requests.post(
                cast(str, self.__class__.UPDATE_URL),
                json=dto_dict,
                headers={"Content-Type": "application/json"},
            )
            await self.populate_from_dto(TermDTO(**response.json()))
        except Exception as e:
            handle_error(e)

    async def delete_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()
        try:
            response = requests.post(
                cast(str, self.__class__.DELETE_URL),
                json={"iri": self.iri},
                headers={"Content-Type": "application/json"},
            )
            if response.status_code != 201:
                raise DeleteRecordFailError()
        except Exception as e:
            handle_error(e)

    def set_vocabulary(self, vocabulary: Any) -> None:
        if not vocabulary.has_db_record():
            raise NotRecordedYetError(vocabulary)
        self._VocabularyID = vocabulary.id
        self._VocabularyIRI = vocabulary.iri

    def set_external_term_iri_using_name(self) -> None:
        if not self._Name:
            raise NeedToSetFieldError(self, "name")
        self._TermIRI = f"{self._VocabularyIRI}#{self._Name}"

    @property
    def term_iri(self) -> Optional[IRIType]:
        return self._TermIRI

    @term_iri.setter
    def term_iri(self, value: str) -> None:
        self._TermIRI = as_iri(value)

    @property
    def vocabulary_iri(self) -> Optional[IRIType]:
        return self._VocabularyIRI

    @property
    def vocabulary_id(self) -> Optional[IDType]:
        return self._VocabularyID

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
