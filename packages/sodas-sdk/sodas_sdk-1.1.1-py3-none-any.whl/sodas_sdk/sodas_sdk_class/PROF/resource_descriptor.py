from typing import TYPE_CHECKING, Any, ClassVar, Optional, Type, cast

import requests

from sodas_sdk.core.error import (
    NeedToImplementError,
    NeedToSetTemplateError,
    NotRecordedArgumentError,
    NotTemplateBasedResourceDescriptor,
    RequirementsNotSetError,
)
from sodas_sdk.core.type import (
    IDType,
    PaginatedResponse,
    ResourceDescriptorRole,
    SortOrder,
    TemplateArtifactValue,
    as_id,
    as_iri,
)
from sodas_sdk.core.util import destroy, handle_error
from sodas_sdk.sodas_sdk_class.governance_class import (
    GOVERNANCE_MODEL,
    GOVERNANCE_MODEL_DTO,
)
from sodas_sdk.sodas_sdk_class.SODAS.template import Template
from sodas_sdk.sodas_sdk_class.SODAS.template_artifact import TemplateArtifact
from sodas_sdk.sodas_sdk_file.artifact_file import ArtifactFile

if TYPE_CHECKING:
    from sodas_sdk.sodas_sdk_class.PROF.profile import Profile


class ResourceDescriptorDTO(GOVERNANCE_MODEL_DTO):
    profileId: str
    hasRole: ResourceDescriptorRole
    isInheritedFrom: Optional[str] = None
    hasArtifact: Optional[str] = None
    conformsTo: Optional[str] = None
    format: Optional[str] = None
    useTemplate: bool


class ResourceDescriptor(GOVERNANCE_MODEL):
    _ProfileID: Optional[IDType] = None
    _HasRole: Optional[ResourceDescriptorRole] = None
    _IsInheritedFrom: Optional[str] = None
    _HasArtifact: Optional[str] = None
    _ConformsTo: Optional[str] = None
    _Format: Optional[str] = None
    _UseTemplate: bool = False

    _FileArtifact: Optional[ArtifactFile] = None
    _TemplateArtifact: Optional[TemplateArtifact] = None
    _Profile: Optional["Profile"] = None

    DTO_CLASS: ClassVar[Type[ResourceDescriptorDTO]] = ResourceDescriptorDTO

    @classmethod
    def configure_api_url(cls, base_url: str) -> None:
        prefix = "api/v1/governance/open-reference-model"
        cls.API_URL = f"{base_url}/{prefix}/resource-descriptor"
        cls.LIST_URL = f"{cls.API_URL}/list"
        cls.GET_URL = f"{cls.API_URL}/get"
        cls.CREATE_URL = f"{cls.API_URL}/create"
        cls.UPDATE_URL = f"{cls.API_URL}/update"
        cls.DELETE_URL = f"{cls.API_URL}/remove"

    def to_dto(self) -> ResourceDescriptorDTO:
        assert self._ProfileID is not None
        assert self._HasRole is not None
        assert self._UseTemplate is not None
        return ResourceDescriptorDTO(
            **super().to_dto().model_dump(exclude_none=True),
            profileId=self._ProfileID,
            hasRole=self._HasRole,
            isInheritedFrom=self._IsInheritedFrom,
            hasArtifact=self._HasArtifact,
            conformsTo=self._ConformsTo,
            format=self._Format,
            useTemplate=self._UseTemplate,
        )

    async def populate_from_dto(self, dto: GOVERNANCE_MODEL_DTO) -> None:
        await super().populate_from_dto(dto)
        dto = (
            dto
            if isinstance(dto, ResourceDescriptorDTO)
            else ResourceDescriptorDTO(**dto.model_dump())
        )
        self._ProfileID = as_id(dto.profileId)
        self._HasRole = dto.hasRole
        self._UseTemplate = dto.useTemplate
        self._IsInheritedFrom = dto.isInheritedFrom
        self._ConformsTo = dto.conformsTo
        self._Format = dto.format
        self._HasArtifact = dto.hasArtifact

        if dto.id and dto.iri and dto.useTemplate and dto.hasArtifact:
            self._TemplateArtifact = await TemplateArtifact.get_db_record(
                as_iri(dto.hasArtifact)
            )

    def has_db_record(self) -> bool:
        return super().has_db_record() and self._HasArtifact is not None

    @classmethod
    async def list_db_records(
        cls,
        page_number: int = 1,
        page_size: int = 10,
        sort_order: SortOrder = SortOrder.DESC,
        has_role: Optional[ResourceDescriptorRole] = None,
        profile_id: Optional[str] = None,
        *args: Any,
    ) -> PaginatedResponse["ResourceDescriptor"]:
        cls.throw_error_if_api_url_not_set()
        url = cast(str, cls.LIST_URL)
        try:
            response = requests.get(
                url,
                params={
                    "offset": (page_number - 1) * page_size,
                    "limit": page_size,
                    "ordered": sort_order.value,
                    "hasRole": has_role,
                    "profileId": profile_id,
                },
            )
            return cast(
                PaginatedResponse[ResourceDescriptor],
                await cls.list_response_to_paginated_response(response),
            )

        except Exception as e:
            handle_error(e)

    async def create_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_recorded()

        if self._UseTemplate and (
            self._TemplateArtifact is None or not self._TemplateArtifact.template_iri
        ):
            raise NeedToSetTemplateError()

        await super().create_db_record()

        if not self._HasArtifact:
            if self._UseTemplate:
                if self._TemplateArtifact is None:
                    raise NeedToSetTemplateError()
                if self.iri is None:
                    raise ValueError(
                        "ResourceDescriptor IRI must be set before creating artifact"
                    )
                self._TemplateArtifact._set_resource_descriptor_iri(self.iri)
                await self._TemplateArtifact.create_db_record()
                self._HasArtifact = self._TemplateArtifact.iri
            elif self._FileArtifact:
                self._FileArtifact.upload()
                self._HasArtifact = self._FileArtifact.get_download_url()
            await super().update_db_record()
            self._FileArtifact = None

    async def update_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()

        if self.use_template and not getattr(
            self.template_artifact, "template_iri", None
        ):
            raise NeedToSetTemplateError()

        if not self.use_template and not getattr(self, "file_artifact", None):
            await super().update_db_record()

        elif not self.use_template and self._FileArtifact:
            self._FileArtifact.upload()
            self._HasArtifact = self._FileArtifact.get_download_url()
            await super().update_db_record()

        elif self.use_template and self.template_artifact.has_db_record():
            await self.template_artifact.update_db_record()
            await super().update_db_record()

        elif self.use_template and not self.template_artifact.has_db_record():
            setattr(self.template_artifact, "resource_descriptor_iri", self.iri)
            await self.template_artifact.create_db_record()
            self._HasArtifact = self.template_artifact.iri
            await super().update_db_record()
        else:
            raise NeedToImplementError()

        # Remove _FileArtifact from object (optional: could use `delattr`)
        if hasattr(self, "_FileArtifact"):
            del self._FileArtifact

    async def delete_db_record(self) -> None:
        self.throw_error_if_api_url_not_set()
        self.throw_error_if_not_recorded()
        destroy(self._TemplateArtifact)
        await super().delete_db_record()

    def get_extended(self) -> "ResourceDescriptor":
        self.throw_error_if_not_recorded()

        result = ResourceDescriptor()
        result.set_to_use_template()

        result._HasRole = self._HasRole
        result._HasArtifact = self._HasArtifact
        result.conforms_to = self._ConformsTo
        result.format = self._Format

        result._UseTemplate = self._UseTemplate  # temporarily bypass set_template
        if self._UseTemplate and self._TemplateArtifact:
            result.set_template(self._TemplateArtifact.template)
            if not result._TemplateArtifact:
                result._TemplateArtifact = TemplateArtifact()
            result._TemplateArtifact.set_value(self._TemplateArtifact.get_value())

        result._IsInheritedFrom = self.iri
        return result

    def set_to_use_file(self) -> None:
        self._UseTemplate = False

    def set_to_use_template(self) -> None:
        self._UseTemplate = True
        if not self._TemplateArtifact:
            self._TemplateArtifact = TemplateArtifact()

    def set_template(self, template: Template) -> None:
        if not self._UseTemplate:
            raise RequirementsNotSetError()
        if not template.has_db_record():
            raise NotRecordedArgumentError(template)
        if (
            not self._TemplateArtifact
            or self._TemplateArtifact.template_iri != template.iri
        ):
            self._TemplateArtifact = TemplateArtifact()
            self._TemplateArtifact.set_template(template)

    def get_artifact_value(self) -> TemplateArtifactValue:
        if not self._TemplateArtifact:
            raise RequirementsNotSetError()
        return self._TemplateArtifact.get_value()

    def set_artifact_value(self, value: TemplateArtifactValue) -> None:
        if not (self._UseTemplate and self._TemplateArtifact):
            raise NotTemplateBasedResourceDescriptor(self)
        self._TemplateArtifact.set_value(value)

    def append_empty_artifact_row(self) -> None:
        if not self._TemplateArtifact:
            raise RequirementsNotSetError()
        self._TemplateArtifact.append_empty_row()

    def validate_artifact_value(self) -> None:
        if not self._Profile:
            raise RequirementsNotSetError()
        self._Profile.Options.validate(self)

    def set_file_artifact(self, file_path: str) -> None:
        self._FileArtifact = ArtifactFile()
        self._FileArtifact.set_file(file_path)

    def _set_profile(self, profile: "Profile") -> None:
        self._Profile = profile

    @property
    def profile(self) -> Optional["Profile"]:
        return self._Profile

    @property
    def profile_id(self) -> Optional[IDType]:
        return self._ProfileID

    @profile_id.setter
    def profile_id(self, value: IDType) -> None:
        self._ProfileID = value

    @property
    def has_role(self) -> Optional[ResourceDescriptorRole]:
        return self._HasRole

    @property
    def is_inherited_from(self) -> Optional[str]:
        return self._IsInheritedFrom

    @property
    def has_artifact(self) -> Optional[str]:
        return self._HasArtifact

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
    def use_template(self) -> bool:
        return self._UseTemplate

    @property
    def template(self) -> Template:
        if not self._TemplateArtifact:
            raise RequirementsNotSetError()
        return self._TemplateArtifact.template

    @property
    def template_artifact(self) -> TemplateArtifact:
        if not self._TemplateArtifact:
            raise RequirementsNotSetError()
        return self._TemplateArtifact
