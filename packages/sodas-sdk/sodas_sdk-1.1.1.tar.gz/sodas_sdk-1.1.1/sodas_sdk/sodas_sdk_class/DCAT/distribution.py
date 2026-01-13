from typing import Any, ClassVar, List, Optional, Type

from sodas_sdk.core.error import RequirementsNotSetError
from sodas_sdk.core.type import IDType, MultiLanguageField, as_id
from sodas_sdk.sodas_sdk_class.dcat_class import DCAT_MODEL, DCAT_MODEL_DTO
from sodas_sdk.sodas_sdk_file.data_file import DataFile


class DistributionDTO(DCAT_MODEL_DTO):
    AccessServiceID: Optional[str] = None
    AccessURL: Optional[str] = None
    ByteSize: Optional[int] = None
    CompressFormat: Optional[str] = None
    DownloadURL: Optional[str] = None
    MediaType: Optional[str] = None
    PackageFormat: Optional[str] = None
    SpatialResolutionInMeters: Optional[float] = None
    TemporalResolution: Optional[str] = None
    AccessRights: Optional[str] = None
    ConformsTo: Optional[str] = None
    DescriptionML: Optional[MultiLanguageField] = None
    Format: Optional[str] = None
    License: Optional[str] = None
    Rights: Optional[List[Any]] = None
    TitleML: Optional[MultiLanguageField] = None
    HasPolicy: Optional[List[Any]] = None
    Checksum: Optional[str] = None
    IsDistributionOf: Optional[str] = None


class Distribution(DCAT_MODEL):

    UPLOAD_API_URL: ClassVar[Optional[str]] = None
    DOWNLOAD_API_URL: ClassVar[Optional[str]] = None

    _UploadingData: Optional[DataFile] = None
    _AccessServiceID: Optional[IDType] = None
    _AccessURL: Optional[str] = None
    _ByteSize: Optional[int] = None
    _CompressFormat: Optional[str] = None
    _DownloadURL: Optional[str] = None
    _MediaType: Optional[str] = None
    _PackageFormat: Optional[str] = None
    _SpatialResolutionInMeters: Optional[float] = None
    _TemporalResolution: Optional[str] = None
    _AccessRights: Optional[str] = None
    _ConformsTo: Optional[str] = None
    _DescriptionML: Optional[MultiLanguageField] = None
    _Format: Optional[str] = None
    _License: Optional[str] = None
    _Rights: Optional[List[Any]] = None
    _TitleML: Optional[MultiLanguageField] = None
    _HasPolicy: Optional[List[Any]] = None
    _Checksum: Optional[str] = None
    _IsDistributionOf: Optional[IDType] = None

    DTO_CLASS: ClassVar[Type[DistributionDTO]] = DistributionDTO

    @classmethod
    def configure_api_url(cls, url: str) -> None:
        cls.API_URL = f"{url}/distribution"
        cls.LIST_URL = f"{cls.API_URL}/list"
        cls.UPLOAD_API_URL = f"{url}/data/upload"
        cls.DOWNLOAD_API_URL = f"{url}/data/download"

    @classmethod
    def configure_bucket_name(cls, bucket_name: str) -> None:
        DataFile.BUCKET_NAME = bucket_name

    def to_dto(self) -> DistributionDTO:
        base = super().to_dto().model_dump(exclude_none=True)
        return DistributionDTO(
            **base,
            AccessServiceID=self._AccessServiceID,
            AccessURL=self._AccessURL,
            ByteSize=self._ByteSize,
            CompressFormat=self._CompressFormat,
            DownloadURL=self._DownloadURL,
            MediaType=self._MediaType,
            PackageFormat=self._PackageFormat,
            SpatialResolutionInMeters=self._SpatialResolutionInMeters,
            TemporalResolution=self._TemporalResolution,
            AccessRights=self._AccessRights,
            ConformsTo=self._ConformsTo,
            DescriptionML=self._DescriptionML,
            Format=self._Format,
            License=self._License,
            Rights=self._Rights,
            TitleML=self._TitleML,
            HasPolicy=self._HasPolicy,
            Checksum=self._Checksum,
            IsDistributionOf=self._IsDistributionOf,
        )

    async def populate_from_dto(self, dto: DCAT_MODEL_DTO) -> None:
        await super().populate_from_dto(dto)
        dto = (
            dto
            if isinstance(dto, DistributionDTO)
            else DistributionDTO(**dto.model_dump(exclude_none=True))
        )
        if dto.AccessServiceID:
            self._AccessServiceID = as_id(dto.AccessServiceID)
        if dto.AccessURL:
            self._AccessURL = dto.AccessURL
        if dto.ByteSize is not None:
            self._ByteSize = dto.ByteSize
        if dto.CompressFormat:
            self._CompressFormat = dto.CompressFormat
        if dto.DownloadURL:
            self._DownloadURL = dto.DownloadURL
        if dto.MediaType:
            self._MediaType = dto.MediaType
        if dto.PackageFormat:
            self._PackageFormat = dto.PackageFormat
        if dto.SpatialResolutionInMeters is not None:
            self._SpatialResolutionInMeters = dto.SpatialResolutionInMeters
        if dto.TemporalResolution:
            self._TemporalResolution = dto.TemporalResolution
        if dto.AccessRights:
            self._AccessRights = dto.AccessRights
        if dto.ConformsTo:
            self._ConformsTo = dto.ConformsTo
        if dto.Format:
            self._Format = dto.Format
        if dto.License:
            self._License = dto.License
        if dto.Rights is not None:
            self._Rights = dto.Rights
        if dto.HasPolicy is not None:
            self._HasPolicy = dto.HasPolicy
        if dto.Checksum:
            self._Checksum = dto.Checksum
        if dto.IsDistributionOf:
            self._IsDistributionOf = as_id(dto.IsDistributionOf)
        if dto.DescriptionML:
            self._DescriptionML = dto.DescriptionML
        if dto.TitleML:
            self._TitleML = dto.TitleML

    async def create_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_recorded()
        if self._UploadingData:
            self._UploadingData.upload()
            self._DownloadURL = self._UploadingData.get_download_url()
        await super().create_db_record()
        self._UploadingData = None

    async def update_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()
        if self._UploadingData:
            self._UploadingData.upload()
            self._DownloadURL = self._UploadingData.get_download_url()
        await super().update_db_record()
        self._UploadingData = None

    def set_uploading_data(self, file_path: str) -> None:
        if not self._UploadingData:
            self._UploadingData = DataFile()
        self._UploadingData.set_file(file_path)

    def get_title(self, language_code: str = "ko") -> Optional[str]:
        if self._TitleML is None:
            self._TitleML = {}
        return self._TitleML.get(language_code)

    def set_title(self, title: str, language_code: str = "ko") -> None:
        if self._TitleML is None:
            self._TitleML = {}
        self._TitleML[language_code] = title

    def remove_title(self, language_code: str = "ko") -> None:
        if self._TitleML is None:
            raise RequirementsNotSetError()
        if language_code in self._TitleML:
            del self._TitleML[language_code]
        else:
            print(f'Warning: Title for language code "{language_code}" does not exist.')

    def get_description(self, language_code: str = "ko") -> Optional[str]:
        if self._DescriptionML is None:
            self._DescriptionML = {}
        return self._DescriptionML.get(language_code)

    def set_description(self, value: str, language_code: str = "ko") -> None:
        if self._DescriptionML is None:
            self._DescriptionML = {}
        self._DescriptionML[language_code] = value

    def remove_description(self, language_code: str = "ko") -> None:
        if self._DescriptionML is None:
            raise RequirementsNotSetError()
        if language_code in self._DescriptionML:
            del self._DescriptionML[language_code]
        else:
            print(
                f'Warning: Description for language code "{language_code}" does not exist.'
            )

    @property
    def download_url(self) -> Optional[str]:
        return self._DownloadURL

    @download_url.setter
    def download_url(self, value: str) -> None:
        self._DownloadURL = value

    @property
    def access_service_id(self) -> Optional[str]:
        return self._AccessServiceID

    @access_service_id.setter
    def access_service_id(self, value: str) -> None:
        self._AccessServiceID = as_id(value)

    @property
    def byte_size(self) -> Optional[int]:
        return self._ByteSize

    @byte_size.setter
    def byte_size(self, value: int) -> None:
        self._ByteSize = value

    @property
    def compress_format(self) -> Optional[str]:
        return self._CompressFormat

    @compress_format.setter
    def compress_format(self, value: str) -> None:
        self._CompressFormat = value

    @property
    def media_type(self) -> Optional[str]:
        return self._MediaType

    @media_type.setter
    def media_type(self, value: str) -> None:
        self._MediaType = value

    @property
    def package_format(self) -> Optional[str]:
        return self._PackageFormat

    @package_format.setter
    def package_format(self, value: str) -> None:
        self._PackageFormat = value

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
    def access_rights(self) -> Optional[str]:
        return self._AccessRights

    @access_rights.setter
    def access_rights(self, value: str) -> None:
        self._AccessRights = value

    @property
    def conforms_to(self) -> Optional[str]:
        return self._ConformsTo

    @conforms_to.setter
    def conforms_to(self, value: str) -> None:
        self._ConformsTo = value

    @property
    def format(self) -> Optional[str]:
        return self._Format

    @format.setter
    def format(self, value: str) -> None:
        self._Format = value

    @property
    def license(self) -> Optional[str]:
        return self._License

    @license.setter
    def license(self, value: str) -> None:
        self._License = value

    @property
    def rights(self) -> Optional[List[Any]]:
        return self._Rights

    @rights.setter
    def rights(self, value: List[Any]) -> None:
        self._Rights = value

    @property
    def has_policy(self) -> Optional[List[Any]]:
        return self._HasPolicy

    @has_policy.setter
    def has_policy(self, value: List[Any]) -> None:
        self._HasPolicy = value

    @property
    def checksum(self) -> Optional[str]:
        return self._Checksum

    @checksum.setter
    def checksum(self, value: str) -> None:
        self._Checksum = value

    @property
    def is_distribution_of(self) -> Optional[str]:
        return self._IsDistributionOf

    @is_distribution_of.setter
    def is_distribution_of(self, value: str) -> None:
        self._IsDistributionOf = as_id(value)
