from sodas_sdk.sodas_sdk_file.sodas_sdk_file import SODAS_SDK_FILE


class ArtifactFile(SODAS_SDK_FILE):
    @classmethod
    def configure_api_url(cls, url: str) -> None:
        cls.UPLOAD_URL = f"{url}/api/v1/governance/open-reference-model/resource-descriptor/artifact/upload"
        cls.REMOVE_URL = f"{url}/api/v1/governance/open-reference-model/resource-descriptor/artifact/remove?id="
        cls.DOWNLOAD_URL = f"{url}/artifacts"
