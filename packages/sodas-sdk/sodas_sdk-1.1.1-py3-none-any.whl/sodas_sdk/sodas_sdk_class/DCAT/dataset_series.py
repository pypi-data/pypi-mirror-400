from typing import ClassVar, List, Optional, Type

from sodas_sdk.core.error import (
    IndexOutOfBoundsError,
    InvalidTypeError,
    NotInitializedError,
    NotRecordedArgumentError,
    SwitchSameIndexError,
)
from sodas_sdk.core.type import IDType, as_id, as_ids
from sodas_sdk.core.util import destroy
from sodas_sdk.sodas_sdk_class.DCAT.dataset import Dataset
from sodas_sdk.sodas_sdk_class.DCAT.dcat_resource import (
    DCAT_RESOURCE,
    DCAT_RESOURCE_DTO,
)
from sodas_sdk.sodas_sdk_class.dcat_class import DCAT_MODEL_DTO


class DatasetSeriesDTO(DCAT_RESOURCE_DTO):
    DatasetSeriesID: Optional[str] = None
    InSeriesID: Optional[str] = None
    Frequency: Optional[str] = None
    SpatialResolutionInMeters: Optional[float] = None
    TemporalResolution: Optional[str] = None
    Spatial: Optional[str] = None
    Temporal: Optional[str] = None
    WasGeneratedBy: Optional[str] = None
    SeriesMemberIDs: Optional[List[str]] = None


class DatasetSeries(DCAT_RESOURCE):
    _DatasetSeriesID: Optional[IDType] = None
    _InSeriesID: Optional[IDType] = None
    _Frequency: Optional[str] = None
    _SpatialResolutionInMeters: Optional[float] = None
    _TemporalResolution: Optional[str] = None
    _Spatial: Optional[str] = None
    _Temporal: Optional[str] = None
    _WasGeneratedBy: Optional[str] = None

    _SeriesMembers: List[Dataset] = []
    _SeriesMemberIDs: List[IDType] = []

    DTO_CLASS: ClassVar[Type[DatasetSeriesDTO]] = DatasetSeriesDTO

    @classmethod
    def configure_api_url(cls, url: str) -> None:
        cls.API_URL = f"{url}/datasetseries"
        cls.LIST_URL = f"{cls.API_URL}/list"

    def to_dto(self) -> DatasetSeriesDTO:
        base = super().to_dto().model_dump(exclude_none=True)
        return DatasetSeriesDTO(
            **base,
            DatasetSeriesID=self._DatasetSeriesID,
            InSeriesID=self._InSeriesID,
            Frequency=self._Frequency,
            SpatialResolutionInMeters=self._SpatialResolutionInMeters,
            TemporalResolution=self._TemporalResolution,
            Spatial=self._Spatial,
            Temporal=self._Temporal,
            WasGeneratedBy=self._WasGeneratedBy,
            SeriesMemberIDs=self._SeriesMemberIDs if self._SeriesMemberIDs else None,
        )

    async def populate_from_dto(self, dto: DCAT_MODEL_DTO) -> None:
        await super().populate_from_dto(dto)
        dto = (
            dto
            if isinstance(dto, DatasetSeriesDTO)
            else DatasetSeriesDTO(**dto.model_dump(exclude_none=True))
        )

        if dto.DatasetSeriesID:
            self._DatasetSeriesID = as_id(dto.DatasetSeriesID)
        if dto.InSeriesID:
            self._InSeriesID = as_id(dto.InSeriesID)
        self._Frequency = dto.Frequency
        self._SpatialResolutionInMeters = dto.SpatialResolutionInMeters
        self._TemporalResolution = dto.TemporalResolution
        self._Spatial = dto.Spatial
        self._Temporal = dto.Temporal
        self._WasGeneratedBy = dto.WasGeneratedBy
        await self._populate_series_members_from_dto(dto)

    async def _populate_series_members_from_dto(self, dto: DatasetSeriesDTO) -> None:
        if dto.SeriesMemberIDs:
            self._SeriesMemberIDs = as_ids(dto.SeriesMemberIDs)
            self._SeriesMembers = [
                await Dataset.get_db_record(did) for did in dto.SeriesMemberIDs
            ]

    async def delete_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()
        for ds in self._SeriesMembers:
            destroy(ds)
        await super().delete_db_record()

    def append_series_member(self, dataset: Dataset) -> None:
        if not isinstance(dataset, Dataset):
            raise InvalidTypeError(dataset, "Dataset")
        if not dataset.id:
            raise NotRecordedArgumentError(dataset)
        self._SeriesMemberIDs.append(dataset.id)

    def switch_series_members(self, index1: int, index2: int) -> None:
        if not self._SeriesMemberIDs:
            raise NotInitializedError("SeriesMemberIDs")
        if index1 < 0 or index1 >= len(self._SeriesMemberIDs):
            raise IndexOutOfBoundsError(index1)
        if index2 < 0 or index2 >= len(self._SeriesMemberIDs):
            raise IndexOutOfBoundsError(index2)
        if index1 == index2:
            raise SwitchSameIndexError(index1)
        self._SeriesMemberIDs[index1], self._SeriesMemberIDs[index2] = (
            self._SeriesMemberIDs[index2],
            self._SeriesMemberIDs[index1],
        )

    @property
    def dataset_series_id(self) -> Optional[str]:
        return self._DatasetSeriesID

    @property
    def series_member_ids(self) -> List[str]:
        return self._SeriesMemberIDs

    @property
    def series_members(self) -> List[Dataset]:
        return self._SeriesMembers

    @property
    def frequency(self) -> Optional[str]:
        return self._Frequency

    @frequency.setter
    def frequency(self, value: str) -> None:
        self._Frequency = value

    @property
    def spatial_resolution_in_meters(self) -> Optional[float]:
        return self._SpatialResolutionInMeters

    @spatial_resolution_in_meters.setter
    def spatial_resolution_in_meters(self, value: float) -> None:
        self._SpatialResolutionInMeters = value

    @property
    def temporal_resolution(self) -> Optional[str]:
        return self._TemporalResolution

    @temporal_resolution.setter
    def temporal_resolution(self, value: str) -> None:
        self._TemporalResolution = value

    @property
    def spatial(self) -> Optional[str]:
        return self._Spatial

    @spatial.setter
    def spatial(self, value: str) -> None:
        self._Spatial = value

    @property
    def temporal(self) -> Optional[str]:
        return self._Temporal

    @temporal.setter
    def temporal(self, value: str) -> None:
        self._Temporal = value

    @property
    def was_generated_by(self) -> Optional[str]:
        return self._WasGeneratedBy

    @was_generated_by.setter
    def was_generated_by(self, value: str) -> None:
        self._WasGeneratedBy = value
