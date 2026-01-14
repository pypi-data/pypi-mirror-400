"""Submodel Registry Implementation Module."""

import json
import logging
from typing import TYPE_CHECKING

import requests
from pydantic import BaseModel

if TYPE_CHECKING:
    from aas_http_client.classes.client.aas_client import AasHttpClient


from aas_http_client.utilities.encoder import decode_base_64
from aas_http_client.utilities.http_helper import (
    STATUS_CODE_200,
    STATUS_CODE_201,
    STATUS_CODE_204,
    STATUS_CODE_404,
    log_response,
)

logger = logging.getLogger(__name__)


class SubmodelRegistryImplementation(BaseModel):
    """Implementation of Submodel Registry related API calls."""

    def __init__(self, client: "AasHttpClient"):
        """Initializes the SubmodelRegistryImplementation with the given client."""
        self._client = client

    # GET /submodel-descriptors/{submodelIdentifier}
    def get_submodel_descriptor_by_id(self, submodel_identifier: str) -> dict | None:
        """Returns the Submodel Descriptor for the given submodel identifier.

        :param submodel_identifier: The unique identifier of the Submodel Descriptor
        :return: Submodel Descriptor data or None if an error occurred
        """
        if not self._client.encoded_ids:
            submodel_identifier: str = decode_base_64(submodel_identifier)

        url = f"{self._client.base_url}/submodel-descriptors/{submodel_identifier}"

        self._client.set_token()

        try:
            response = self._client.get_session().get(url, timeout=self._client.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code == STATUS_CODE_404:
                logger.warning(f"Submodel Descriptor with id '{submodel_identifier}' not found.")
                logger.debug(response.text)
                return None

            if response.status_code != STATUS_CODE_200:
                log_response(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)

    # PUT /submodel-descriptors/{submodelIdentifier}
    def put_submodel_descriptor_by_id(self, submodel_identifier: str, request_body: dict) -> bool:
        """Creates or updates an existing Submodel Descriptor.

        :param submodel_identifier: The unique identifier of the Submodel Descriptor
        :param request_body: Submodel Descriptor object
        :return: Updated Submodel Descriptor data or None if an error occurred
        """
        if not self._client.encoded_ids:
            submodel_identifier: str = decode_base_64(submodel_identifier)

        url = f"{self._client.base_url}/submodel-descriptors/{submodel_identifier}"

        self._client.set_token()

        try:
            response = self._client.get_session().put(url, json=request_body, timeout=self._client.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code == STATUS_CODE_404:
                logger.warning(f"Submodel Descriptor with id '{submodel_identifier}' not found.")
                logger.debug(response.text)
                return False

            if response.status_code != STATUS_CODE_204:
                log_response(response)
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return False

        return True

    # DELETE /submodel-descriptors/{submodelIdentifier}
    def delete_submodel_descriptor_by_id(self, submodel_identifier: str) -> bool:
        """Deletes a Submodel Descriptor, i.e. de-registers a submodel.

        :param submodel_identifier: The unique identifier of the Submodel Descriptor
        :return: True if deletion was successful, False otherwise
        """
        if not self._client.encoded_ids:
            submodel_identifier: str = decode_base_64(submodel_identifier)

        url = f"{self._client.base_url}/submodel-descriptors/{submodel_identifier}"

        self._client.set_token()

        try:
            response = self._client.get_session().delete(url, timeout=self._client.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code == STATUS_CODE_404:
                logger.warning(f"Submodel Descriptor with id '{submodel_identifier}' not found.")
                logger.debug(response.text)
                return False

            if response.status_code != STATUS_CODE_204:
                log_response(response)
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return False

        return True

    # GET /submodel-descriptors
    def get_all_submodel_descriptors(self, limit: int = 100, cursor: str = "") -> dict | None:
        """Returns all Submodel Descriptors.

        :param limit: The maximum number of elements in the response array
        :param cursor: A server-generated identifier retrieved from pagingMetadata that specifies from which position the result listing should continue
        :return: Submodel Descriptors data or None if an error occurred
        """
        url = f"{self._client.base_url}/submodel-descriptors"

        params = {}
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor

        self._client.set_token()

        try:
            response = self._client.get_session().get(url, params=params, timeout=self._client.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_200:
                log_response(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)

    # POST /submodel-descriptors
    def post_submodel_descriptor(self, request_body: dict) -> dict | None:
        """Creates a new Submodel Descriptor, i.e. registers a submodel.

        :param request_body: Submodel Descriptor object
        :return: Created Submodel Descriptor data or None if an error occurred
        """
        url = f"{self._client.base_url}/submodel-descriptors"

        self._client.set_token()

        try:
            response = self._client.get_session().post(url, json=request_body, timeout=self._client.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_201:
                log_response(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)

    # DELETE /submodel-descriptors
    def delete_all_submodel_descriptors(self) -> bool:
        """Deletes all Submodel Descriptors.

        :return: True if deletion was successful, False otherwise
        """
        url = f"{self._client.base_url}/submodel-descriptors"

        self._client.set_token()

        try:
            response = self._client.get_session().delete(url, timeout=self._client.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_204:
                log_response(response)
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return False

        return True

    # GET /description
    def get_self_description(self) -> dict | None:
        """Returns the self-describing information of a network resource (ServiceDescription).

        :return: self-describing information of a network resource
        """
        url = f"{self._client.base_url}/description"

        self._client.set_token()

        try:
            response = self._client.get_session().get(url, timeout=self._client.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_200:
                log_response(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)
