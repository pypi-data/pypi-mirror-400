from sodas_sdk.sodas_sdk_class.DCAT.data_service import DataService
from sodas_sdk.sodas_sdk_class.DCAT.dataset import Dataset
from sodas_sdk.sodas_sdk_class.DCAT.dataset_series import DatasetSeries
from sodas_sdk.sodas_sdk_class.DCAT.distribution import Distribution
from sodas_sdk.sodas_sdk_class.dictionary.term import Term
from sodas_sdk.sodas_sdk_class.dictionary.vocabulary import Vocabulary
from sodas_sdk.sodas_sdk_class.PROF.profile import Profile
from sodas_sdk.sodas_sdk_class.PROF.resource_descriptor import ResourceDescriptor
from sodas_sdk.sodas_sdk_class.SODAS.template import Template
from sodas_sdk.sodas_sdk_class.SODAS.template_artifact import TemplateArtifact
from sodas_sdk.sodas_sdk_class.SODAS.template_detail import TemplateDetail
from sodas_sdk.sodas_sdk_file.artifact_file import ArtifactFile
from sodas_sdk.sodas_sdk_file.data_file import DataFile
from sodas_sdk.sodas_sdk_file.thumbnail_file import ThumbnailFile

QUALITY_API_URL: str = ""


def configure_sdk_api_url(sdk_api_url: str) -> None:
    Profile.MAPPING_API_URL = sdk_api_url
    global QUALITY_API_URL
    QUALITY_API_URL = sdk_api_url


def configure_governance_api_url(governance_portal_api_url: str) -> None:
    governance_portal_api_url = governance_portal_api_url.rstrip("/")

    if governance_portal_api_url:
        Profile.configure_api_url(governance_portal_api_url)
        ResourceDescriptor.configure_api_url(governance_portal_api_url)
        TemplateArtifact.configure_api_url(governance_portal_api_url)
        Template.configure_api_url(governance_portal_api_url)
        TemplateDetail.configure_api_url(governance_portal_api_url)
        ArtifactFile.configure_api_url(governance_portal_api_url)
        Vocabulary.configure_api_url(governance_portal_api_url)
        Term.configure_api_url(governance_portal_api_url)
    else:
        print("GOVERNANCE_API_URL not found in .env")


def configure_datahub_api_url(datahub_api_url: str) -> None:
    datahub_api_url = datahub_api_url.rstrip("/")

    if datahub_api_url:
        Distribution.configure_api_url(datahub_api_url)
        Dataset.configure_api_url(datahub_api_url)
        DatasetSeries.configure_api_url(datahub_api_url)
        DataService.configure_api_url(datahub_api_url)
        ThumbnailFile.configure_api_url(datahub_api_url)
        DataFile.configure_api_url(datahub_api_url)
    else:
        print("DATAHUB_API_URL not found in .env")


def configure_api_url(datahub_api_url: str, governance_portal_api_url: str) -> None:
    configure_datahub_api_url(datahub_api_url)
    configure_governance_api_url(governance_portal_api_url)


def set_bearer_token(token: str) -> None:
    Dataset.BEARER_TOKEN = token
    DataService.BEARER_TOKEN = token
    DatasetSeries.BEARER_TOKEN = token
    Distribution.BEARER_TOKEN = token
    Profile.BEARER_TOKEN = token
    TemplateArtifact.BEARER_TOKEN = token
    ResourceDescriptor.BEARER_TOKEN = token
    Template.BEARER_TOKEN = token
    Vocabulary.BEARER_TOKEN = token
    Term.BEARER_TOKEN = token
