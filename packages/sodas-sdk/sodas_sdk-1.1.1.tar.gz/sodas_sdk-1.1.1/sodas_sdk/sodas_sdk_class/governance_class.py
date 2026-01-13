from abc import ABC
from typing import Any, ClassVar, List, Optional, Type, TypeVar, cast

from pydantic import BaseModel

from sodas_sdk.core.error import (
    DeleteRecordFailError,
    NeedToImplementError,
    RecordNotFoundError,
    UnexpectedResponseFormatError,
)
from sodas_sdk.core.type import (
    IRIType,
    PaginatedResponse,
    SortOrder,
    to_date,
    to_date_string,
)
from sodas_sdk.core.util import LARGE_ENOUGH_NUMBER, destroy, handle_error
from sodas_sdk.sodas_sdk_class.sodas_sdk_class import SODAS_SDK_CLASS

T = TypeVar("T", bound="GOVERNANCE_MODEL")


class GOVERNANCE_MODEL_DTO(BaseModel):
    id: Optional[str] = None
    iri: Optional[str] = None
    issued: Optional[str] = None
    modified: Optional[str] = None


class GOVERNANCE_MODEL(SODAS_SDK_CLASS, ABC):
    GET_URL: ClassVar[Optional[str]] = None
    CREATE_URL: ClassVar[Optional[str]] = None
    UPDATE_URL: ClassVar[Optional[str]] = None
    DELETE_URL: ClassVar[Optional[str]] = None

    DTO_CLASS: ClassVar[Type[GOVERNANCE_MODEL_DTO]] = GOVERNANCE_MODEL_DTO

    def to_dto(self) -> GOVERNANCE_MODEL_DTO:
        return GOVERNANCE_MODEL_DTO(
            id=self._ID,
            iri=self._IRI,
            issued=to_date_string(self._Issued) if self._Issued else None,
            modified=to_date_string(self._Modified) if self._Modified else None,
        )

    async def populate_from_dto(self, dto: GOVERNANCE_MODEL_DTO) -> None:
        if dto.id:
            self._ID = dto.id
        if dto.iri:
            self._IRI = dto.iri
        if dto.issued:
            self._Issued = to_date(dto.issued)
        if dto.modified:
            self._Modified = to_date(dto.modified)

    def has_db_record(self) -> bool:
        return bool(self._ID and self._IRI)

    @classmethod
    async def list_db_records(
        cls: Type[T],
        page_number: int = 1,
        page_size: int = 10,
        sort_order: SortOrder = SortOrder.DESC,
        *additional_args: Any,
    ) -> PaginatedResponse[T]:
        raise NeedToImplementError()

    @classmethod
    async def list_response_to_paginated_response(
        cls: Type[T], response: Any
    ) -> PaginatedResponse[T]:
        response.raise_for_status()
        data = response.json()
        if "total" in data and "results" in data:
            result_list = []
            for item in data["results"]:
                instance = cls()
                dto_class = getattr(cls, "DTO_CLASS", GOVERNANCE_MODEL_DTO)
                dto_instance = dto_class(**item)
                await instance.populate_from_dto(dto_instance)
                result_list.append(instance)
            return cast(
                PaginatedResponse[T],
                PaginatedResponse(total=data["total"], list=result_list),
            )
        else:
            raise UnexpectedResponseFormatError(data)

    @classmethod
    async def get_all_db_records(cls: Type[T]) -> List[T]:
        response = await cls.list_db_records(1, LARGE_ENOUGH_NUMBER)
        return response.list

    @classmethod
    async def get_db_record(cls: Type[T], iri: IRIType) -> T:
        cls.throw_error_if_api_url_not_set()
        import requests

        try:
            response = requests.get(
                f"{cls.GET_URL}/?iri={iri}",
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
        except Exception as e:
            handle_error(e)

        data = response.json()
        if data:
            instance = cls()
            dto_class = getattr(cls, "DTO_CLASS", GOVERNANCE_MODEL_DTO)
            dto_instance = dto_class(**data)
            await instance.populate_from_dto(dto_instance)
            return instance
        else:
            raise RecordNotFoundError()

    async def create_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_recorded()

        import requests

        url = cast(str, self.__class__.CREATE_URL)
        try:
            response = requests.post(
                url,
                json=self.to_dto().model_dump(exclude_none=True),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
        except Exception as e:
            handle_error(e)

        dto_class = getattr(self.__class__, "DTO_CLASS", GOVERNANCE_MODEL_DTO)
        dto_instance = dto_class(**response.json())
        await self.populate_from_dto(dto_instance)

    async def update_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()

        import requests

        url = cast(str, self.__class__.UPDATE_URL)
        # Exclude 'iri', 'issued', 'modified' fields from DTO before sending
        dto_dict = self.to_dto().model_dump(
            exclude={"iri", "issued", "modified"}, exclude_none=True
        )

        try:
            response = requests.post(
                url,
                json=dto_dict,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
        except Exception as e:
            handle_error(e)
        dto_class = getattr(self.__class__, "DTO_CLASS", GOVERNANCE_MODEL_DTO)
        dto_instance = dto_class(**response.json())
        await self.populate_from_dto(dto_instance)

    async def delete_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()

        import requests

        url = cast(str, self.__class__.DELETE_URL)
        try:
            response = requests.post(
                url,
                json={"iri": self._IRI},
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
        except Exception as e:
            handle_error(e)

        if response.status_code != 201:
            raise DeleteRecordFailError()
        else:
            destroy(self)
