from typing import ClassVar, List, Optional, Type, cast
from urllib.parse import quote

import requests

from sodas_sdk.core.error import (
    IndexOutOfBoundsError,
    InvalidTypeError,
    RecordNotFoundError,
)
from sodas_sdk.core.type import IDType, as_id, as_ids
from sodas_sdk.core.util import destroy, handle_error
from sodas_sdk.sodas_sdk_class.DCAT.dcat_resource import (
    DCAT_RESOURCE,
    DCAT_RESOURCE_DTO,
)
from sodas_sdk.sodas_sdk_class.DCAT.distribution import Distribution
from sodas_sdk.sodas_sdk_class.dcat_class import DCAT_MODEL_DTO


class DatasetDTO(DCAT_RESOURCE_DTO):
    DatasetID: Optional[str] = None
    InSeriesID: Optional[str] = None
    FirstID: Optional[str] = None
    PreviousID: Optional[str] = None
    NextID: Optional[str] = None
    LastID: Optional[str] = None
    Frequency: Optional[str] = None
    SpatialResolutionInMeters: Optional[float] = None
    TemporalResolution: Optional[str] = None
    Spatial: Optional[str] = None
    Temporal: Optional[str] = None
    WasGeneratedBy: Optional[str] = None
    DistributionIDs: Optional[List[str]] = None


class Dataset(DCAT_RESOURCE):
    _DatasetID: Optional[IDType] = None
    _InSeriesID: Optional[IDType] = None
    _FirstID: Optional[IDType] = None
    _PreviousID: Optional[IDType] = None
    _NextID: Optional[IDType] = None
    _LastID: Optional[IDType] = None
    _Frequency: Optional[str] = None
    _SpatialResolutionInMeters: Optional[float] = None
    _TemporalResolution: Optional[str] = None
    _Spatial: Optional[str] = None
    _Temporal: Optional[str] = None
    _WasGeneratedBy: Optional[str] = None

    _DistributionIDs: List[IDType] = []
    _Distributions: List[Distribution] = []

    DTO_CLASS: ClassVar[Type[DatasetDTO]] = DatasetDTO

    @classmethod
    def configure_api_url(cls, url: str) -> None:
        cls.API_URL = f"{url}/dataset"
        cls.LIST_URL = f"{cls.API_URL}/list"

    @classmethod
    async def get_rdf_map(cls, identifier: str, depth: int = 1) -> str:
        """
        /dataset/{identifier}/rdf?depth={depth} 호출해서
        text/turtle 문자열을 그대로 반환하는 헬퍼.
        identifier는 slash, dot 등이 포함될 수 있으므로 반드시 URL-encode.
        """
        cls.throw_error_if_api_url_not_set()

        # depth 클램핑
        depth = max(0, min(depth, 10))

        # identifier URL 인코딩 (모든 unsafe 문자 포함)
        encoded_identifier = quote(identifier, safe="")

        url = f"{cls.API_URL}/rdf"
        params = {"depth": depth, "identifier": encoded_identifier}
        headers = {"Accept": "text/turtle"}

        try:
            response = requests.get(url, params=params, headers=headers)
        except Exception as e:
            handle_error(e)

        if response.status_code == 404:
            raise RecordNotFoundError()

        if response.status_code // 100 != 2:
            handle_error(
                RuntimeError(
                    f"Failed to fetch RDF (status={response.status_code}): {response.text}"
                )
            )

        return response.text

    def to_dto(self) -> DatasetDTO:
        base = super().to_dto().model_dump(exclude_none=True)
        return DatasetDTO(
            **base,
            DatasetID=self._DatasetID,
            InSeriesID=self._InSeriesID,
            FirstID=self._FirstID,
            PreviousID=self._PreviousID,
            NextID=self._NextID,
            LastID=self._LastID,
            Frequency=self._Frequency,
            SpatialResolutionInMeters=self._SpatialResolutionInMeters,
            TemporalResolution=self._TemporalResolution,
            Spatial=self._Spatial,
            Temporal=self._Temporal,
            WasGeneratedBy=self._WasGeneratedBy,
            DistributionIDs=self._DistributionIDs if self._DistributionIDs else None,
        )

    async def populate_from_dto(self, dto: DCAT_MODEL_DTO) -> None:
        await super().populate_from_dto(dto)
        dto = (
            dto
            if isinstance(dto, DatasetDTO)
            else DatasetDTO(**dto.model_dump(exclude_none=True))
        )
        if dto.DatasetID:
            self._DatasetID = as_id(dto.DatasetID)
        if dto.InSeriesID:
            self._InSeriesID = as_id(dto.InSeriesID)
        if dto.FirstID:
            self._FirstID = as_id(dto.FirstID)
        if dto.PreviousID:
            self._PreviousID = as_id(dto.PreviousID)
        if dto.NextID:
            self._NextID = as_id(dto.NextID)
        if dto.LastID:
            self._LastID = as_id(dto.LastID)
        self._Frequency = dto.Frequency
        self._SpatialResolutionInMeters = dto.SpatialResolutionInMeters
        self._TemporalResolution = dto.TemporalResolution
        self._Spatial = dto.Spatial
        self._Temporal = dto.Temporal
        self._WasGeneratedBy = dto.WasGeneratedBy
        await self.populate_distributions_from_dto(dto)

    async def populate_distributions_from_dto(self, dto: DatasetDTO) -> None:
        if dto.DistributionIDs:
            self._DistributionIDs = as_ids(dto.DistributionIDs)
            self._Distributions = [
                await Distribution.get_db_record(did) for did in dto.DistributionIDs
            ]

    async def create_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_recorded()
        dists = self._Distributions
        await super().create_db_record()
        self._Distributions = dists
        for d in self._Distributions:
            d.is_distribution_of = self._DatasetID
            await d.create_db_record()
            self._DistributionIDs.append(as_id(cast(str, d.id)))

    async def update_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()
        dists = self._Distributions
        await super().update_db_record()
        self._Distributions = dists
        for d in self._Distributions:
            d.is_distribution_of = self._DatasetID
            if d.id:
                await d.update_db_record()
            else:
                await d.create_db_record()
                self._DistributionIDs.append(as_id(cast(str, d.id)))
        await self._delete_not_maintained_distributions()

    async def delete_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()
        for d in self._Distributions:
            if d.has_db_record():
                await d.delete_db_record()
            destroy(d)
        await super().delete_db_record()

    async def _delete_not_maintained_distributions(self) -> None:
        current = [d.id for d in self._Distributions if d.id]
        kept = as_ids(current)
        to_delete = [id for id in self._DistributionIDs if id not in kept]
        for id in to_delete:
            dist = await Distribution.get_db_record(id)
            await dist.delete_db_record()
        self._DistributionIDs = kept

    def create_distribution(self) -> Distribution:
        new_dist = Distribution()
        self._Distributions.append(new_dist)
        return new_dist

    def append_distribution(self, dist: Distribution) -> None:
        if not isinstance(dist, Distribution):
            raise InvalidTypeError(dist, "Distribution")
        self._Distributions.append(dist)

    def remove_distribution(self, index: int) -> None:
        if index < 0 or index >= len(self._Distributions):
            raise IndexOutOfBoundsError(index)
        target = self._Distributions[index]
        self._Distributions = [
            dist
            for i, dist in enumerate(self._Distributions)
            if i != index or dist is not target
        ]

    def get_distribution(self, index: int) -> Distribution:
        if index < 0 or index >= len(self._Distributions):
            raise IndexOutOfBoundsError(index)
        return self._Distributions[index]

    @property
    def distributions(self) -> List[Distribution]:
        return self._Distributions

    @property
    def dataset_id(self) -> Optional[str]:
        return self._DatasetID

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

    @property
    def in_series_id(self) -> Optional[str]:
        return self._InSeriesID

    @property
    def first_id(self) -> Optional[str]:
        return self._FirstID

    @property
    def previous_id(self) -> Optional[str]:
        return self._PreviousID

    @property
    def next_id(self) -> Optional[str]:
        return self._NextID

    @property
    def last_id(self) -> Optional[str]:
        return self._LastID
