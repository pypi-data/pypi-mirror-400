from sodas_sdk.sodas_sdk_file.sodas_sdk_file import SODAS_SDK_FILE


class ThumbnailFile(SODAS_SDK_FILE):
    @classmethod
    def configure_api_url(cls, url: str) -> None:
        cls.UPLOAD_URL = f"{url}/thumbnail/upload"
        cls.REMOVE_URL = f"{url}/thumbnail/remove/"
        cls.DOWNLOAD_URL = f"{url}/thumbnails"
