from abc import ABC
from datetime import datetime
from typing import Any, ClassVar, List, Optional, Type, TypeVar, cast

import requests
from pydantic import BaseModel

from sodas_sdk.core.error import (
    DeleteRecordFailError,
    RecordNotFoundError,
    UnexpectedResponseFormatError,
)
from sodas_sdk.core.type import (
    IDType,
    IRIType,
    PaginatedResponse,
    SortOrder,
    to_date,
    to_date_string,
)
from sodas_sdk.core.util import LARGE_ENOUGH_NUMBER, destroy, handle_error
from sodas_sdk.sodas_sdk_class.sodas_sdk_class import SODAS_SDK_CLASS

T = TypeVar("T", bound="DCAT_MODEL")


class DCAT_MODEL_DTO(BaseModel):
    ID: Optional[str] = None
    IRI: Optional[str] = None
    Issued: Optional[str] = None
    Modified: Optional[str] = None
    CreatedAt: Optional[str] = None
    UpdatedAt: Optional[str] = None


class DCAT_MODEL(SODAS_SDK_CLASS, ABC):
    _CreatedAt: Optional[datetime] = None
    _UpdatedAt: Optional[datetime] = None

    DTO_CLASS: ClassVar[Type[DCAT_MODEL_DTO]] = DCAT_MODEL_DTO

    def to_dto(self) -> DCAT_MODEL_DTO:
        return DCAT_MODEL_DTO(
            ID=self.id,
            IRI=self.iri,
            Issued=to_date_string(self.issued) if self.issued else None,
            Modified=to_date_string(self.modified) if self.modified else None,
            CreatedAt=to_date_string(self.created_at) if self.created_at else None,
            UpdatedAt=to_date_string(self.updated_at) if self.updated_at else None,
        )

    def has_db_record(self) -> bool:
        return bool(self._ID and self._IRI)

    async def populate_from_dto(self, dto: DCAT_MODEL_DTO) -> None:
        if dto.ID:
            self._ID = dto.ID
        if dto.IRI:
            self._IRI = dto.IRI
        if dto.Issued:
            self._Issued = to_date(dto.Issued)
        if dto.Modified:
            self._Modified = to_date(dto.Modified)
        if dto.CreatedAt:
            self._CreatedAt = to_date(dto.CreatedAt)
        if dto.UpdatedAt:
            self._UpdatedAt = to_date(dto.UpdatedAt)

    @classmethod
    async def list_db_records(
        cls: Type[T],
        page_number: int = 1,
        page_size: int = 10,
        sort_order: SortOrder = SortOrder.DESC,
        *additional_args: Any,
    ) -> PaginatedResponse[T]:
        cls.throw_error_if_api_url_not_set()

        url: str = cast(str, cls.LIST_URL)
        try:
            response = requests.get(
                url,
                params={
                    "pageNumber": page_number,
                    "pageSize": page_size,
                    "sortOrder": sort_order.value,
                },
            )
        except Exception as e:
            handle_error(e)

        data = response.json()
        if "total" in data and isinstance(data["list"], list):
            result_list: List[T] = []
            for item in data["list"]:
                instance = cls()
                dto_class = getattr(cls, "DTO_CLASS", DCAT_MODEL_DTO)
                dto_instance = dto_class(**item)
                await instance.populate_from_dto(dto_instance)
                result_list.append(instance)

            return cast(
                PaginatedResponse[T],
                PaginatedResponse(total=data["total"], list=result_list),
            )
        else:
            raise UnexpectedResponseFormatError(response)

    @classmethod
    async def get_all_db_records(cls: Type[T]) -> List[T]:
        cls.throw_error_if_api_url_not_set()
        result = await cls.list_db_records(1, LARGE_ENOUGH_NUMBER)
        return result.list

    @classmethod
    async def get_db_record(cls: Type[T], id_: str) -> T:
        cls.throw_error_if_api_url_not_set()
        url: str = f"{cls.API_URL}/{id_}"
        try:
            response = requests.get(url)
        except Exception as e:
            handle_error(e)

        data = response.json()
        if data:
            instance = cls()
            dto_class = getattr(cls, "DTO_CLASS", DCAT_MODEL_DTO)
            dto_instance = dto_class(**data)
            await instance.populate_from_dto(dto_instance)
            return instance
        else:
            raise RecordNotFoundError()

    async def create_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_recorded()
        url = cast(str, self.API_URL)
        payload = self.to_dto().model_dump(exclude_none=True)
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
        except Exception as e:
            handle_error(e)
        dto_class = getattr(self.__class__, "DTO_CLASS", DCAT_MODEL_DTO)
        dto_instance = dto_class(**response.json())
        await self.populate_from_dto(dto_instance)

    async def update_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()
        url: str = cast(str, self.API_URL)
        payload = self.to_dto().model_dump(exclude_none=True)
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
        except Exception as e:
            handle_error(e)
        dto_class = getattr(self.__class__, "DTO_CLASS", DCAT_MODEL_DTO)
        dto_instance = dto_class(**response.json())
        await self.populate_from_dto(dto_instance)

    async def delete_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()

        url = f"{self.API_URL}/{self.id}"
        try:
            response = requests.delete(url)
        except Exception as e:
            handle_error(e)

        if response.status_code == 204:
            destroy(self)
        else:
            raise DeleteRecordFailError()

    @property
    def id(self) -> Optional[IDType]:
        return self._ID

    @id.setter
    def id(self, value: str) -> None:
        self._ID = value

    @property
    def iri(self) -> Optional[IRIType]:
        return self._IRI

    @iri.setter
    def iri(self, value: str) -> None:
        self._IRI = value

    @property
    def created_at(self) -> Optional[datetime]:
        return self._CreatedAt

    @property
    def updated_at(self) -> Optional[datetime]:
        return self._UpdatedAt
