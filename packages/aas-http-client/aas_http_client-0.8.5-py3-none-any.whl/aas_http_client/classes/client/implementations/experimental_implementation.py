"""Experimental implementation of Asset Administration Shell Registry related API calls."""

import logging
import mimetypes
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aas_http_client.classes.client.aas_client import AasHttpClient

import requests
from pydantic import BaseModel

from aas_http_client.utilities.encoder import decode_base_64
from aas_http_client.utilities.http_helper import (
    STATUS_CODE_200,
    STATUS_CODE_201,
    STATUS_CODE_204,
    STATUS_CODE_404,
    log_response,
)

logger = logging.getLogger(__name__)


class ExperimentalImplementation(BaseModel):
    """Implementation of Asset Administration Shell Registry related API calls."""

    def __init__(self, client: "AasHttpClient"):
        """Initializes the ExperimentalImplementation with the given client."""
        self._client = client

    # GET /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/attachment
    def get_file_by_path_submodel_repo(self, submodel_identifier: str, id_short_path: str) -> bytes | None:
        """Downloads file content from a specific submodel element from the Submodel at a specified path. Experimental feature - may not be supported by all servers.

        :param submodel_identifier: The Submodels unique id
        :param id_short_path: IdShort path to the submodel element (dot-separated)
        :return: Attachment file data as bytes (octet-stream) or None if an error occurred
        """
        if not self._client.encoded_ids:
            submodel_identifier = decode_base_64(submodel_identifier)

        url = f"{self._client.base_url}/submodels/{submodel_identifier}/submodel-elements/{id_short_path}/attachment"

        self._client.set_token()  # ensures Authorization header is set

        try:
            response = self._client.get_session().get(url, timeout=self._client.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code == STATUS_CODE_404:
                logger.warning(
                    f"Submodel with id '{submodel_identifier}' or Submodel element with IDShort path '{id_short_path}' or file content not found."
                )
                logger.debug(response.text)
                return None

            if response.status_code != STATUS_CODE_200:
                log_response(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling REST API: {e}")
            return None

        return response.content

    # POST /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/attachment
    def post_file_by_path_submodel_repo(self, submodel_identifier: str, id_short_path: str, file: Path) -> bool:
        """Uploads file content to an existing submodel element at a specified path within submodel elements hierarchy. Experimental feature - may not be supported by all servers.

        :param submodel_identifier: The Submodels unique id
        :param id_short_path: IdShort path to the submodel element (dot-separated)
        :param file: Path to the file to upload as attachment
        :return: Attachment data as bytes or None if an error occurred
        """
        if file.exists() is False or not file.is_file():
            logger.error(f"Attachment file '{file}' does not exist.")
            return False

        if not self._client.encoded_ids:
            submodel_identifier = decode_base_64(submodel_identifier)

        url = f"{self._client.base_url}/submodels/{submodel_identifier}/submodel-elements/{id_short_path}/attachment"

        self._client.set_token()

        try:
            mime_type, _ = mimetypes.guess_type(file)

            with file.open("rb") as f:
                files = {"file": (file.name, f, mime_type or "application/octet-stream")}
                response = self._client.get_session().post(url, files=files, timeout=self._client.time_out)

            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code == STATUS_CODE_404:
                logger.warning(f"Submodel with id '{submodel_identifier}' or Submodel element with IDShort path '{id_short_path}' not found.")
                logger.debug(response.text)
                return False

            # original dotnet server delivers 200 instead of 204
            if response.status_code not in (STATUS_CODE_200, STATUS_CODE_204):
                log_response(response)
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return False

        return True

    # PUT /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/attachment
    def put_file_by_path_submodel_repo(self, submodel_identifier: str, id_short_path: str, file: Path) -> bool:
        """Uploads file content to an existing submodel element at a specified path within submodel elements hierarchy. Experimental feature - may not be supported by all servers.

        :param submodel_identifier: The Submodels unique id
        :param id_short_path: IdShort path to the submodel element (dot-separated)
        :param file: Path to the file to upload as attachment
        :return: Attachment data as bytes or None if an error occurred
        """
        if file.exists() is False or not file.is_file():
            logger.error(f"Attachment file '{file}' does not exist.")
            return False

        if not self._client.encoded_ids:
            submodel_identifier = decode_base_64(submodel_identifier)

        url = f"{self._client.base_url}/submodels/{submodel_identifier}/submodel-elements/{id_short_path}/attachment"

        self._client.set_token()

        try:
            mime_type, _ = mimetypes.guess_type(file)

            with file.open("rb") as f:
                files = {"file": (file.name, f, mime_type or "application/octet-stream")}
                response = self._client.get_session().put(url, files=files, timeout=self._client.time_out)

            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code == STATUS_CODE_404:
                logger.warning(f"Submodel with id '{submodel_identifier}' or Submodel element with IDShort path '{id_short_path}' not found.")
                logger.debug(response.text)
                return False

            # original dotnet server delivers 200 instead of 204
            if response.status_code not in (STATUS_CODE_200, STATUS_CODE_204):
                log_response(response)
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return False

        return True

    # DELETE /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/attachment
    def delete_file_by_path_submodel_repo(self, submodel_identifier: str, id_short_path: str) -> bool:
        """Deletes file content of an existing submodel element at a specified path within submodel elements hierarchy. Experimental feature - may not be supported by all servers.

        :param submodel_identifier: The Submodels unique id
        :param id_short_path: IdShort path to the submodel element (dot-separated)
        :return: True if deletion was successful, False otherwise
        """
        if not self._client.encoded_ids:
            submodel_identifier = decode_base_64(submodel_identifier)

        url = f"{self._client.base_url}/submodels/{submodel_identifier}/submodel-elements/{id_short_path}/attachment"

        self._client.set_token()

        try:
            response = self._client.get_session().delete(url, timeout=self._client.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code == 404:
                logger.warning(f"Submodel with id '{submodel_identifier}' or Submodel element with IDShort path '{id_short_path}' not found.")
                return False

            if response.status_code != STATUS_CODE_200:
                log_response(response)
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling REST API: {e}")
            return False

        return True

    def _post_multipart(self, url, files):
        headers = dict(self._client.get_session().headers)
        headers.pop("Content-Type", None)
        return self._client.get_session().post(url, headers=headers, files=files)
