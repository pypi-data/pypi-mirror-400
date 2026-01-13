from typing import Optional

import requests

from sodas_sdk.core.error import NeedToImplementError, UnexpectedResponseFormatError
from sodas_sdk.core.util import destroy
from sodas_sdk.sodas_sdk_file.sodas_sdk_file import SODAS_SDK_FILE


class DataFile(SODAS_SDK_FILE):
    DOWNLOAD_URL: Optional[str] = None
    BUCKET_NAME: Optional[str] = None

    def __init__(self) -> None:
        super().__init__()
        self._endpoint: Optional[str] = None
        self._bucket_name: Optional[str] = None

    @classmethod
    def configure_bucket_name(cls, bucket_name: str) -> None:
        cls.BUCKET_NAME = bucket_name

    @classmethod
    def configure_api_url(cls, url: str) -> None:
        cls.UPLOAD_URL = f"{url}/data/upload"
        cls.REMOVE_URL = f"{url}/data/remove/"
        cls.DOWNLOAD_URL = f"{url}/data/download"

    def upload(self) -> None:
        if not self._file_content:
            return
        if not self.UPLOAD_URL:
            raise NeedToImplementError()

        files = {"file": (self._file_name, self._file_content)}
        upload_url = (
            f"{self.UPLOAD_URL}?bucketName={self.BUCKET_NAME}"
            if self.BUCKET_NAME
            else self.UPLOAD_URL
        )
        response = requests.post(upload_url, files=files)

        if response.status_code in (200, 201):
            json_data = response.json()
            if "id" in json_data:
                self._id = json_data["id"]
                self._bucket_name = json_data.get("bucketName")
                self._endpoint = json_data.get("endpoint")
            else:
                raise UnexpectedResponseFormatError(response)
        else:
            raise UnexpectedResponseFormatError(response)

    def remove(self) -> None:
        if not self._id:
            return
        if not self.REMOVE_URL:
            raise NeedToImplementError()

        remove_url = (
            f"{self.REMOVE_URL}{self._id}?bucketName={self._bucket_name}"
            if self._bucket_name
            else f"{self.REMOVE_URL}{self._id}"
        )
        response = requests.get(remove_url)

        if response.status_code in (200, 204):
            destroy(self)
        else:
            raise UnexpectedResponseFormatError(response)

    def get_download_url(self) -> str:
        if not self._id or not self._bucket_name or not self._endpoint:
            raise ValueError("Download URL components are not fully initialized.")
        if not self.DOWNLOAD_URL:
            raise NeedToImplementError()

        return f"{self.DOWNLOAD_URL}/{self._id}?bucketName={self._bucket_name}&endpoint={self._endpoint}"
