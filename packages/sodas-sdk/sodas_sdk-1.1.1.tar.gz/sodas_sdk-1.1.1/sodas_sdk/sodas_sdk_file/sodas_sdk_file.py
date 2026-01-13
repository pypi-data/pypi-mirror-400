import os
from pathlib import Path
from typing import Optional

import requests

from sodas_sdk.core.error import NeedToImplementError, UnexpectedResponseFormatError
from sodas_sdk.core.util import destroy


class SODAS_SDK_FILE:
    UPLOAD_URL: Optional[str] = None
    REMOVE_URL: Optional[str] = None
    DOWNLOAD_URL: Optional[str] = None

    def __init__(self) -> None:
        self._id: Optional[str] = None
        self._file_name: Optional[str] = None
        self._file_size: Optional[int] = None
        self._file_type: Optional[str] = None
        self._file_content: Optional[bytes] = None

    @classmethod
    def configure_api_url(cls, url: str) -> None:
        raise NeedToImplementError()

    def set_file(self, file_path: str) -> None:
        path = Path(file_path)
        self._file_name = path.name
        self._file_type = path.suffix.lstrip(".")
        self._file_size = os.path.getsize(path)
        with open(path, "rb") as f:
            self._file_content = f.read()

    def upload(self) -> None:
        if not self._file_content:
            return
        if not self.UPLOAD_URL:
            raise NeedToImplementError()

        files = {"file": (self._file_name, self._file_content)}
        response = requests.post(self.UPLOAD_URL, files=files)

        if response.status_code in (200, 201):
            json_data = response.json()
            if "id" in json_data:
                self._id = json_data["id"]
            else:
                raise UnexpectedResponseFormatError(response)
        else:
            raise UnexpectedResponseFormatError(response)

    def remove(self) -> None:
        if not self._id:
            return
        if not self.REMOVE_URL:
            raise NeedToImplementError()

        remove_url = f"{self.REMOVE_URL}{self._id}"
        response = requests.get(remove_url)

        if response.status_code in (200, 204):
            destroy(self)
        else:
            raise UnexpectedResponseFormatError(response)

    def get_download_url(self) -> str:
        if not self._id:
            raise ValueError("ID is not set yet.")
        if not self.DOWNLOAD_URL:
            raise NeedToImplementError()
        return f"{self.DOWNLOAD_URL}/{self._id}"
