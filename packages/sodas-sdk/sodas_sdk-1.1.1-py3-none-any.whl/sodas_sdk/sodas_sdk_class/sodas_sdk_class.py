from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, ClassVar, Optional, Type, TypeVar

from pydantic import BaseModel, ConfigDict

from sodas_sdk.core.error import (
    AlreadyRecordedError,
    APIURLNotSetError,
    NeedToImplementError,
    NotRecordedYetError,
)
from sodas_sdk.core.type import IDType, IRIType, PaginatedResponse, SortOrder

T = TypeVar("T", bound="SODAS_SDK_CLASS")


class SODAS_SDK_CLASS_DTO:
    pass


class SODAS_SDK_CLASS(BaseModel, ABC):
    BEARER_TOKEN: ClassVar[Optional[str]] = None
    API_URL: ClassVar[Optional[str]] = None
    LIST_URL: ClassVar[Optional[str]] = None

    _ID: Optional[IDType] = None
    _IRI: Optional[IRIType] = None
    _Issued: Optional[datetime] = None
    _Modified: Optional[datetime] = None

    DTO_CLASS: ClassVar[Type[Any]] = SODAS_SDK_CLASS_DTO

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    def __eq__(self, other: object) -> bool:
        return self is other

    def __hash__(self) -> int:
        return id(self)

    @classmethod
    def configure_api_url(cls, url: str) -> None:
        raise NeedToImplementError()

    @classmethod
    async def list_db_records(
        cls: Type[T],
        page_number: int = 1,
        page_size: int = 10,
        sort_order: SortOrder = SortOrder.DESC,
        *additional_args: Any,
    ) -> PaginatedResponse[T]:
        raise NeedToImplementError()

    @abstractmethod
    def to_dto(self) -> Any:
        pass

    @abstractmethod
    async def populate_from_dto(self, dto: Any) -> None:
        pass

    @abstractmethod
    async def create_db_record(self) -> None:
        pass

    @abstractmethod
    async def update_db_record(self) -> None:
        pass

    @abstractmethod
    async def delete_db_record(self) -> None:
        pass

    @abstractmethod
    def has_db_record(self) -> bool:
        pass

    def throw_error_if_recorded(self) -> None:
        if self.has_db_record():
            raise AlreadyRecordedError(self)

    def throw_error_if_not_recorded(self) -> None:
        if not self.has_db_record():
            raise NotRecordedYetError(self)

    @classmethod
    def throw_error_if_api_url_not_set(cls) -> None:
        if not cls.API_URL:
            raise APIURLNotSetError(cls)

    def debug(self) -> None:
        print(self)

    @property
    def id(self) -> Optional[IDType]:
        return self._ID

    @property
    def iri(self) -> Optional[IRIType]:
        return self._IRI

    @property
    def issued(self) -> Optional[datetime]:
        return self._Issued

    @property
    def modified(self) -> Optional[datetime]:
        return self._Modified
