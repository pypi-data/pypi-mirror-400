from typing import ClassVar, Optional, Type

from sodas_sdk.core.type import IDType, as_id
from sodas_sdk.sodas_sdk_class.DCAT.dcat_resource import (
    DCAT_RESOURCE,
    DCAT_RESOURCE_DTO,
)
from sodas_sdk.sodas_sdk_class.dcat_class import DCAT_MODEL_DTO


class DataServiceDTO(DCAT_RESOURCE_DTO):
    DataServiceID: Optional[str] = None
    EndpointURL: Optional[str] = None
    EndpointDescription: Optional[str] = None


class DataService(DCAT_RESOURCE):
    _DataServiceID: Optional[IDType] = None
    _EndpointURL: Optional[str] = None
    _EndpointDescription: Optional[str] = None

    DTO_CLASS: ClassVar[Type[DataServiceDTO]] = DataServiceDTO

    @classmethod
    def configure_api_url(cls, url: str) -> None:
        cls.API_URL = f"{url}/dataservice"
        cls.LIST_URL = f"{cls.API_URL}/list"

    def to_dto(self) -> DataServiceDTO:
        base = super().to_dto().model_dump(exclude_none=True)
        return DataServiceDTO(
            **base,
            DataServiceID=self._DataServiceID,
            EndpointURL=self._EndpointURL,
            EndpointDescription=self._EndpointDescription,
        )

    async def populate_from_dto(self, dto: DCAT_MODEL_DTO) -> None:
        await super().populate_from_dto(dto)
        dto = (
            dto
            if isinstance(dto, DataServiceDTO)
            else DataServiceDTO(**dto.model_dump(exclude_none=True))
        )
        if dto.DataServiceID:
            self._DataServiceID = as_id(dto.DataServiceID)
        if dto.EndpointURL:
            self._EndpointURL = dto.EndpointURL
        if dto.EndpointDescription:
            self._EndpointDescription = dto.EndpointDescription

    @property
    def data_service_id(self) -> Optional[str]:
        return self._DataServiceID

    @property
    def endpoint_url(self) -> Optional[str]:
        return self._EndpointURL

    @endpoint_url.setter
    def endpoint_url(self, value: str) -> None:
        self._EndpointURL = value

    @property
    def endpoint_description(self) -> Optional[str]:
        return self._EndpointDescription

    @endpoint_description.setter
    def endpoint_description(self, value: str) -> None:
        self._EndpointDescription = value
