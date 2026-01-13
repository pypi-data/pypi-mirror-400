from typing import Any, ClassVar, List, Optional, Type, TypeVar, cast

import requests

from sodas_sdk.core.error import NamedTermNotExistError
from sodas_sdk.core.type import IRIType, PaginatedResponse, SortOrder, as_id, as_iri
from sodas_sdk.core.util import LARGE_ENOUGH_NUMBER, destroy, handle_error
from sodas_sdk.sodas_sdk_class.dictionary.term import Term
from sodas_sdk.sodas_sdk_class.governance_class import (
    GOVERNANCE_MODEL,
    GOVERNANCE_MODEL_DTO,
)

T = TypeVar("T", bound="Vocabulary")


class VocabularyDTO(GOVERNANCE_MODEL_DTO):
    namespaceIri: Optional[str] = None
    original: bool
    prefix: str
    name: str
    description: str


class Vocabulary(GOVERNANCE_MODEL):
    _NamespaceIRI: Optional[IRIType] = None
    _Original: Optional[bool] = None
    _Prefix: Optional[str] = None
    _Name: Optional[str] = None
    _Description: Optional[str] = None

    _FetchedTermIRIs: List[str] = []
    _Terms: List[Term] = []

    DTO_CLASS: ClassVar[Type[VocabularyDTO]] = VocabularyDTO

    @classmethod
    def configure_api_url(cls, base_url: str) -> None:
        PREFIX = "api/v1/governance/dictionary"
        cls.API_URL = f"{base_url}/{PREFIX}/vocabulary"
        cls.LIST_URL = f"{cls.API_URL}/list"
        cls.GET_URL = f"{cls.API_URL}/get"
        cls.CREATE_URL = f"{cls.API_URL}/create"
        cls.UPDATE_URL = f"{cls.API_URL}/update"
        cls.DELETE_URL = f"{cls.API_URL}/remove"

    async def populate_from_dto(self, dto: GOVERNANCE_MODEL_DTO) -> None:
        await super().populate_from_dto(dto)
        dto = (
            dto
            if isinstance(dto, VocabularyDTO)
            else VocabularyDTO(**dto.model_dump(exclude_none=True))
        )
        if dto.namespaceIri:
            self._NamespaceIRI = as_iri(dto.namespaceIri)
        self._Original = dto.original
        self._Prefix = dto.prefix
        self._Name = dto.name
        self._Description = dto.description
        await self._populate_terms_from_dto(dto)

    async def _populate_terms_from_dto(self, dto: VocabularyDTO) -> None:
        if dto.id:
            response = await Term.list_db_records(
                page_number=1,
                page_size=LARGE_ENOUGH_NUMBER,
                sort_order=SortOrder.ASC,
                vocabulary_id=as_id(dto.id),
            )
            self._Terms = response.list
            self._FetchedTermIRIs = [t.iri for t in self._Terms if t.iri is not None]

    def to_dto(self) -> VocabularyDTO:
        base = super().to_dto().model_dump(exclude_none=True)
        return VocabularyDTO(
            **base,
            namespaceIri=self._NamespaceIRI,
            original=cast(bool, self._Original),
            prefix=cast(str, self._Prefix),
            name=cast(str, self._Name),
            description=cast(str, self._Description),
        )

    @classmethod
    async def list_db_records(
        cls: Type[T],
        page_number: int = 1,
        page_size: int = 10,
        sort_order: SortOrder = SortOrder.DESC,
        original: Optional[bool] = None,
        name: Optional[str] = None,
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
                    "original": original,
                    "name": name,
                },
            )
            return await cls.list_response_to_paginated_response(response)
        except Exception as e:
            handle_error(e)

    async def create_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_recorded()
        terms = self._Terms
        await super().create_db_record()
        self._Terms = terms
        for term in self._Terms:
            await term.create_db_record()
            self._FetchedTermIRIs.append(cast(str, term.iri))

    async def update_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()
        terms = self._Terms
        await super().update_db_record()
        self._Terms = terms
        for term in self._Terms:
            term.set_vocabulary(self)
            if term.has_db_record():
                await term.update_db_record()
            else:
                await term.create_db_record()
                self._FetchedTermIRIs.append(cast(str, term.iri))
        await self._delete_not_maintained_terms()

    async def delete_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()
        await self._delete_not_maintained_terms()
        for term in self._Terms:
            destroy(term)
        await super().delete_db_record()

    async def _delete_not_maintained_terms(self) -> None:
        if self._FetchedTermIRIs:
            existing = self._FetchedTermIRIs
            maintained = [t.iri for t in self._Terms if t.iri is not None]
            scheduled = [iri for iri in existing if iri not in maintained]
            scheduled_terms = await Term.get_all_db_records()
            for term in scheduled_terms:
                if term.iri in scheduled:
                    await term.delete_db_record()
            self._FetchedTermIRIs = maintained

    def create_term(self) -> Term:
        new_term = Term()
        new_term.set_vocabulary(self)
        self._Terms.append(new_term)
        return new_term

    def get_term_using_name(self, name: str) -> Term:
        for term in self._Terms:
            if term.name == name:
                return term
        raise NamedTermNotExistError(name)

    def remove_term_using_name(self, name: str) -> None:
        for i, term in enumerate(self._Terms):
            if term.name == name:
                self._Terms.pop(i)
                return
        raise NamedTermNotExistError(name)

    @property
    def namespace_iri(self) -> Optional[IRIType]:
        return self._NamespaceIRI

    @namespace_iri.setter
    def namespace_iri(self, value: str) -> None:
        self._NamespaceIRI = as_iri(value)

    @property
    def original(self) -> Optional[bool]:
        return self._Original

    @original.setter
    def original(self, value: bool) -> None:
        self._Original = value

    @property
    def prefix(self) -> Optional[str]:
        return self._Prefix

    @prefix.setter
    def prefix(self, value: str) -> None:
        self._Prefix = value

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
    def terms(self) -> List[Term]:
        return self._Terms
