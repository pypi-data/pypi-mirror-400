"""BaSyx Server interface for REST API communication."""

import json
import logging
from enum import Enum
from pathlib import Path

import puremagic
from basyx.aas import model

from aas_http_client.classes.client.aas_client import AasHttpClient, _create_client
from aas_http_client.classes.wrapper.attachment import Attachment
from aas_http_client.classes.wrapper.pagination import (
    ShellPaginatedData,
    SubmodelElementPaginatedData,
    SubmodelPaginatedData,
    create_shell_paging_data,
    create_submodel_element_paging_data,
    create_submodel_paging_data,
)
from aas_http_client.utilities.sdk_tools import convert_to_dict as _to_dict
from aas_http_client.utilities.sdk_tools import convert_to_object as _to_object

logger = logging.getLogger(__name__)


class IdEncoding(Enum):
    """Determines the ID encoding mode for API requests."""

    default = 0
    encoded = 1
    decoded = 2

    def __str__(self) -> str:
        """String representation of the IdMode enum."""
        if self == IdEncoding.encoded:
            return "encoded"
        if self == IdEncoding.decoded:
            return "decoded"

        return ""


class Level(Enum):
    """Determines the structural depth of the respective resource content."""

    default = 0
    core = 1
    deep = 2

    def __str__(self) -> str:
        """String representation of the Level enum."""
        if self == Level.core:
            return "core"
        if self == Level.deep:
            return "deep"

        return ""


class Extent(Enum):
    """Determines to which extent the resource is being serialized."""

    default = 0
    with_blob_value = 1
    without_blob_value = 2

    def __str__(self) -> str:
        """String representation of the Extent enum."""
        if self == Extent.with_blob_value:
            return "withBlobValue"
        if self == Extent.without_blob_value:
            return "withoutBlobValue"

        return ""


class AssetKind(Enum):
    """Determines to which asset kind the resource is being serialized."""

    default = 0
    instance = 1
    not_applicable = 2
    type = 3

    def __str__(self) -> str:
        """String representation of the Extent enum."""
        if self == AssetKind.instance:
            return "Instance"
        if self == AssetKind.not_applicable:
            return "NotApplicable"
        if self == AssetKind.type:
            return "Type"

        return ""


# region SdkWrapper


class SdkWrapper:
    """Represents a wrapper for the BaSyx Python SDK to communicate with a REST API."""

    _client: AasHttpClient = None
    base_url: str = ""

    def __init__(self, config_string: str, basic_auth_password: str = "", o_auth_client_secret: str = "", bearer_auth_token: str = ""):
        """Initializes the wrapper with the given configuration.

        :param config_string: Configuration string for the BaSyx server connection.
        :param basic_auth_password: Password for the BaSyx server interface client, defaults to "".
        :param o_auth_client_secret: Client secret for OAuth authentication, defaults to "".
        :param bearer_auth_token: Bearer token for authentication, defaults to "".
        """
        client = _create_client(config_string, basic_auth_password, o_auth_client_secret, bearer_auth_token)

        if not client:
            raise ValueError("Failed to create AAS HTTP client with the provided configuration.")

        self._client = client
        self.base_url = client.base_url

    def set_encoded_ids(self, encoded_ids: IdEncoding):
        """Sets whether to use encoded IDs for API requests.

        :param encoded_ids: If enabled, all IDs used in API requests have to be base64-encoded
        """
        if encoded_ids == IdEncoding.encoded:
            self._client.encoded_ids = True
        else:
            self._client.encoded_ids = False

    def get_encoded_ids(self) -> IdEncoding:
        """Gets whether encoded IDs are used for API requests.

        :return: True if encoded IDs are used, False otherwise
        """
        if self._client.encoded_ids:
            return IdEncoding.encoded

        return IdEncoding.decoded

    def get_client(self) -> AasHttpClient:
        """Returns the underlying AAS HTTP client.

        :return: The AAS HTTP client instance.
        """
        return self._client

    # endregion

    # region shells

    # GET /shells/{aasIdentifier}
    def get_asset_administration_shell_by_id(self, aas_identifier: str) -> model.AssetAdministrationShell | None:
        """Returns a specific Asset Administration Shell.

        :param aas_identifier: The Asset Administration Shells unique id (decoded)
        :return: Asset Administration Shells or None if an error occurred
        """
        content: dict = self._client.shell.get_asset_administration_shell_by_id(aas_identifier)

        if not content:
            logger.warning(f"No shell found with ID '{aas_identifier}' on server.")
            return None

        return _to_object(content)

    # PUT /shells/{aasIdentifier}
    def put_asset_administration_shell_by_id(self, aas_identifier: str, aas: model.AssetAdministrationShell) -> bool:
        """Creates or replaces an existing Asset Administration Shell.

        :param aas_identifier: The Asset Administration Shells unique id (decoded)
        :param aas: Asset Administration Shell to put
        :return: True if the update was successful, False otherwise
        """
        aas_data = _to_dict(aas)
        return self._client.shell.put_asset_administration_shell_by_id(aas_identifier, aas_data)

    # DELETE /shells/{aasIdentifier}
    def delete_asset_administration_shell_by_id(self, aas_identifier: str) -> bool:
        """Deletes an Asset Administration Shell.

        :param aas_identifier: The Asset Administration Shells unique id (decoded)
        :return: True if the deletion was successful, False otherwise
        """
        return self._client.shell.delete_asset_administration_shell_by_id(aas_identifier)

    # GET /shells/{aasIdentifier}/asset-information/thumbnail
    def get_thumbnail_aas_repository(self, aas_identifier: str) -> Attachment | None:
        """Downloads the thumbnail of a specific Asset Administration Shell.

        :param aas_identifier: The Asset Administration Shells unique id (decoded)
        :return: Attachment object with thumbnail content as bytes (octet-stream) or None if an error occurred
        """
        byte_content = self._client.shell.get_thumbnail_aas_repository(aas_identifier)

        if not byte_content:
            logger.warning(f"No thumbnail found for AAS with ID '{aas_identifier}' on server.")
            return None

        return Attachment(
            content=byte_content,
            content_type=puremagic.from_string(byte_content, mime=True),
            filename="thumbnail",
        )

    # PUT /shells/{aasIdentifier}/asset-information/thumbnail
    def put_thumbnail_aas_repository(self, aas_identifier: str, file_name: str, file: Path) -> bool:
        """Creates or updates the thumbnail of the Asset Administration Shell.

        :param aas_identifier: The Asset Administration Shells unique id
        :param file_name: The name of the thumbnail file
        :param file: Path to the thumbnail file to upload as attachment
        :return: True if the update was successful, False otherwise
        """
        return self._client.shell.put_thumbnail_aas_repository(aas_identifier, file_name, file)

    # DELETE /shells/{aasIdentifier}/asset-information/thumbnail
    def delete_thumbnail_aas_repository(self, aas_identifier: str) -> bool:
        """Deletes the thumbnail of a specific Asset Administration Shell.

        :param aas_identifier: The Asset Administration Shells unique id (decoded)
        :return: True if the deletion was successful, False otherwise
        """
        return self._client.shell.delete_thumbnail_aas_repository(aas_identifier)

    # GET /shells
    def get_all_asset_administration_shells(
        self, asset_ids: list[dict] | None = None, id_short: str = "", limit: int = 100, cursor: str = ""
    ) -> ShellPaginatedData | None:
        """Returns all Asset Administration Shells.

        :param assetIds: A list of specific Asset identifiers (format: {"identifier": "string",  "encodedIdentifier": "string"})
        :param idShort: The Asset Administration Shell's IdShort
        :param limit: The maximum number of elements in the response array
        :param cursor: A server-generated identifier retrieved from pagingMetadata that specifies from which position the result listing should continue
        :return: List of paginated Asset Administration Shells or None if an error occurred
        """
        content: dict = self._client.shell.get_all_asset_administration_shells(asset_ids, id_short, limit, cursor)

        if not content:
            return None

        return create_shell_paging_data(content)

    # POST /shells
    def post_asset_administration_shell(self, aas: model.AssetAdministrationShell) -> model.AssetAdministrationShell | None:
        """Creates a new Asset Administration Shell.

        :param aas: Asset Administration Shell to post
        :return: Asset Administration Shell or None if an error occurred
        """
        aas_data = _to_dict(aas)
        content: dict = self._client.shell.post_asset_administration_shell(aas_data)
        return _to_object(content)

    # GET /shells/{aasIdentifier}/submodel-refs
    # POST /shells/{aasIdentifier}/submodel-refs
    # DELETE /shells/{aasIdentifier}/submodel-refs/{submodelIdentifier}

    # not supported by Java Server

    # PUT /shells/{aasIdentifier}/submodels/{submodelIdentifier}
    def put_submodel_by_id_aas_repository(self, aas_identifier: str, submodel_identifier: str, submodel: model.Submodel) -> bool:
        """Updates the Submodel.

        :param aas_identifier: The Asset Administration Shells unique id (decoded)
        :param submodel_identifier: ID of the submodel to put
        :param submodel: Submodel to put
        :return: True if the update was successful, False otherwise
        """
        sm_data = _to_dict(submodel)
        return self._client.shell.put_submodel_by_id_aas_repository(aas_identifier, submodel_identifier, sm_data)

    # GET /shells/{aasIdentifier}/$reference
    def get_asset_administration_shell_by_id_reference_aas_repository(self, aas_identifier: str) -> model.Reference | None:
        """Returns a specific Asset Administration Shell as a Reference.

        :param aas_identifier: ID of the AAS reference to retrieve
        :return: Asset Administration Shells reference object or None if an error occurred
        """
        # workaround because serialization not working
        aas = self.get_asset_administration_shell_by_id(aas_identifier)
        return model.ModelReference.from_referable(aas)

    # GET /shells/{aasIdentifier}/submodels/{submodelIdentifier}
    def get_submodel_by_id_aas_repository(self, aas_identifier: str, submodel_identifier: str) -> model.Submodel | None:
        """Returns the Submodel.

        :param aas_identifier: ID of the AAS to retrieve the submodel from
        :param submodel_identifier: ID of the submodel to retrieve
        :return: Submodel or None if an error occurred
        """
        content: dict = self._client.shell.get_submodel_by_id_aas_repository(aas_identifier, submodel_identifier)
        return _to_object(content)

    # endregion

    # region submodels

    # GET /submodels/{submodelIdentifier}
    def get_submodel_by_id(self, submodel_identifier: str, level: Level = Level.default, extent: Extent = Extent.default) -> model.Submodel | None:
        """Returns a specific Submodel.

        :param submodel_identifier: Encoded ID of the Submodel to retrieve
        :param level: Determines the structural depth of the respective resource content. Available values : deep, core
        :param extent: Determines to which extent the resource is being serialized. Available values : withBlobValue, withoutBlobValue
        :return: Submodel data or None if an error occurred
        """
        content = self._client.submodel.get_submodel_by_id(submodel_identifier, str(level), str(extent))

        if not content:
            logger.warning(f"No submodel found with ID '{submodel_identifier}' on server.")
            return None

        return _to_object(content)

    # PUT /submodels/{submodelIdentifier}
    def put_submodels_by_id(self, submodel_identifier: str, submodel: model.Submodel) -> bool:
        """Updates a existing Submodel.

        :param submodel_identifier: Identifier of the submodel to update
        :param submodel: Submodel data to update
        :return: True if the update was successful, False otherwise
        """
        sm_data = _to_dict(submodel)
        return self._client.submodel.put_submodels_by_id(submodel_identifier, sm_data)

    # DELETE /submodels/{submodelIdentifier}
    def delete_submodel_by_id(self, submodel_id: str) -> bool:
        """Deletes a Submodel.

        :param submodel_id: ID of the submodel to delete
        :return: True if the deletion was successful, False otherwise
        """
        return self._client.submodel.delete_submodel_by_id(submodel_id)

    # GET /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}
    def get_submodel_element_by_path_submodel_repo(
        self, submodel_identifier: str, id_short_path: str, level: Level = Level.default, extent: Extent = Extent.default
    ) -> model.SubmodelElement | None:
        """Returns a specific submodel element from the Submodel at a specified path.

        :param submodel_identifier: Encoded ID of the Submodel to retrieve element from
        :param id_short_path: Path of the Submodel element to retrieve
        :param level: Determines the structural depth of the respective resource content. Available values : deep, core
        :param extent: Determines to which extent the resource is being serialized. Available values : withBlobValue, withoutBlobValue
        :return: Submodel element data or None if an error occurred
        """
        content: dict = self._client.submodel.get_submodel_element_by_path_submodel_repo(submodel_identifier, id_short_path, str(level), str(extent))
        return _to_object(content)

    # PUT /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}

    # POST /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}
    def post_submodel_element_by_path_submodel_repo(
        self,
        submodel_identifier: str,
        id_short_path: str,
        submodel_element: model.SubmodelElement,
        level: Level = Level.default,
        extent: Extent = Extent.default,
    ) -> model.SubmodelElement | None:
        """Creates a new submodel element at a specified path within submodel elements hierarchy.

        :param submodel_identifier: Encoded ID of the submodel to create elements for
        :param id_short_path: Path within the Submodel elements hierarchy
        :param submodel_element: The new Submodel element
        :param level: Determines the structural depth of the respective resource content. Available values : deep, core
        :param extent: Determines to which extent the resource is being serialized. Available values : withBlobValue, withoutBlobValue
        :return: Submodel element object or None if an error occurred
        """
        sme_data = _to_dict(submodel_element)
        content: dict = self._client.submodel.post_submodel_element_by_path_submodel_repo(
            submodel_identifier, id_short_path, sme_data, str(level), str(extent)
        )
        return _to_object(content)

    # DELETE /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}
    # TODO write test
    def delete_submodel_element_by_path_submodel_repo(self, submodel_identifier: str, id_short_path: str):
        """Deletes a submodel element at a specified path within the submodel elements hierarchy.

        :param submodel_identifier: Encoded ID of the Submodel to delete submodel element from
        :param id_short_path: Path of the Submodel element to delete
        :return: True if the deletion was successful, False otherwise
        """
        return self._client.submodel.delete_submodel_element_by_path_submodel_repo(submodel_identifier, id_short_path)

    # GET /submodels
    def get_all_submodels(
        self,
        semantic_id: str = "",
        id_short: str = "",
        limit: int = 0,
        cursor: str = "",
        level: Level = Level.default,
        extent: Extent = Extent.default,
    ) -> SubmodelPaginatedData | None:
        """Returns all Submodels.

        :param semantic_id: The value of the semantic id reference (UTF8-BASE64-URL-encoded)
        :param id_short: The idShort of the Submodel
        :param limit: Maximum number of Submodels to return
        :param cursor: Cursor for pagination
        :param level: Determines the structural depth of the respective resource content. Available values : deep, core
        :param extent: Determines to which extent the resource is being serialized. Available values : withBlobValue, withoutBlobValue
        :return: List of Submodel or None if an error occurred
        """
        content: list = self._client.submodel.get_all_submodels(semantic_id, id_short, limit, cursor, str(level), str(extent))

        if not content:
            return None

        return create_submodel_paging_data(content)

    # POST /submodels
    def post_submodel(self, submodel: model.Submodel) -> model.Submodel | None:
        """Creates a new Submodel.

        :param submodel: Submodel to post
        :return: Submodel or None if an error occurred
        """
        sm_data = _to_dict(submodel)
        content: dict = self._client.submodel.post_submodel(sm_data)
        return _to_object(content)

    # GET /submodels/{submodelIdentifier}/submodel-elements
    def get_all_submodel_elements_submodel_repository(
        self,
        submodel_id: str,
    ) -> SubmodelElementPaginatedData | None:
        """Returns all submodel elements including their hierarchy. !!!Serialization to model.SubmodelElement currently not possible.

        :param submodel_id: Encoded ID of the Submodel to retrieve elements from
        :return: List of Submodel elements or None if an error occurred
        """
        content = self._client.submodel.get_all_submodel_elements_submodel_repository(submodel_id)

        if not content:
            return []

        return create_submodel_element_paging_data(content)

    # POST /submodels/{submodelIdentifier}/submodel-elements
    def post_submodel_element_submodel_repo(self, submodel_id: str, submodel_element: model.SubmodelElement) -> model.SubmodelElement | None:
        """Creates a new submodel element.

        :param submodel_identifier: Encoded ID of the Submodel to create elements for
        :param request_body: Submodel element
        :return: Submodel or None if an error occurred
        """
        sme_data = _to_dict(submodel_element)
        content: dict = self._client.submodel.post_submodel_element_submodel_repo(submodel_id, sme_data)
        return _to_object(content)

    # POST /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/invoke
    # GET /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/$value

    # PATCH /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/$value
    def patch_submodel_element_by_path_value_only_submodel_repo(self, submodel_id: str, submodel_element_path: str, value: str) -> bool:
        """Updates the value of an existing SubmodelElement.

        :param submodel_id: Encoded ID of the Submodel to update submodel element for
        :param submodel_element_path: Path of the Submodel element to update
        :param value: Submodel element value to update as string
        :return: True if the patch was successful, False otherwise
        """
        return self._client.submodel.patch_submodel_element_by_path_value_only_submodel_repo(submodel_id, submodel_element_path, value)

    # GET /submodels/{submodelIdentifier}/$value
    # PATCH /submodels/{submodelIdentifier}/$value
    # GET /submodels/{submodelIdentifier}/$metadata

    # not supported by Java Server

    # PATCH /submodels/{submodelIdentifier}
    def patch_submodel_by_id(self, submodel_id: str, submodel: model.Submodel):
        """Updates an existing Submodel.

        :param submodel_id: Encoded ID of the Submodel to delete
        :return: True if the patch was successful, False otherwise
        """
        sm_data = _to_dict(submodel)
        return self._client.submodel.patch_submodel_by_id(submodel_id, sm_data)

    # endregion

    # region shell registry

    # currently no SDK implementation for descriptor classes -> no implementation for wrapper

    # endregion

    # region experimental

    # GET /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/attachment
    def experimental_get_file_by_path_submodel_repo(self, submodel_identifier: str, id_short_path: str) -> Attachment | None:
        """Downloads file content from a specific submodel element from the Submodel at a specified path. Experimental feature - may not be supported by all servers.

        :param submodel_identifier: The Submodels unique id
        :param id_short_path: IdShort path to the submodel element (dot-separated)
        :return: Attachment object with file content as bytes (octet-stream) or None if an error occurred
        """
        sme = self.get_submodel_element_by_path_submodel_repo(submodel_identifier, id_short_path)

        if not sme or not isinstance(sme, model.File):
            logger.warning(f"No submodel element found at path '{id_short_path}' in submodel '{submodel_identifier}' on server.")
            return None

        byte_content = self._client.experimental.get_file_by_path_submodel_repo(submodel_identifier, id_short_path)

        if not byte_content:
            logger.warning(f"No file found at path '{id_short_path}' in submodel '{submodel_identifier}' on server.")
            return None

        return Attachment(
            content=byte_content,
            content_type=puremagic.from_string(byte_content, mime=True),
            filename=sme.value,
        )

    # POST /submodels/{submodelIdentifier}/submodel-elements/{idShortPath}/attachment
    def experimental_post_file_by_path_submodel_repo(self, submodel_identifier: str, id_short_path: str, file: Path) -> bool:
        """Uploads file content to an existing submodel element at a specified path within submodel elements hierarchy. Experimental feature - may not be supported by all servers.

        :param submodel_identifier: The Submodels unique id
        :param id_short_path: IdShort path to the submodel element (dot-separated)
        :param file: Path to the file to upload as attachment
        :return: Attachment data as bytes or None if an error occurred
        """
        return self._client.experimental.post_file_by_path_submodel_repo(submodel_identifier, id_short_path, file)

    def experimental_put_file_by_path_submodel_repo(self, submodel_identifier: str, id_short_path: str, file: Path) -> bool:
        """Uploads file content to an existing submodel element at a specified path within submodel elements hierarchy. Experimental feature - may not be supported by all servers.

        :param submodel_identifier: The Submodels unique id
        :param id_short_path: IdShort path to the submodel element (dot-separated)
        :param file: Path to the file to upload as attachment
        :return: Attachment data as bytes or None if an error occurred
        """
        return self._client.experimental.put_file_by_path_submodel_repo(submodel_identifier, id_short_path, file)

    def experimental_delete_file_by_path_submodel_repo(self, submodel_identifier: str, id_short_path: str) -> bool:
        """Deletes file content of an existing submodel element at a specified path within submodel elements hierarchy. Experimental feature - may not be supported by all servers.

        :param submodel_identifier: The Submodels unique id
        :param id_short_path: IdShort path to the submodel element (dot-separated)
        :return: True if deletion was successful, False otherwise
        """
        return self._client.experimental.delete_file_by_path_submodel_repo(submodel_identifier, id_short_path)

    # endregion


# region wrapper


def create_wrapper_by_url(
    base_url: str,
    basic_auth_username: str = "",
    basic_auth_password: str = "",
    o_auth_client_id: str = "",
    o_auth_client_secret: str = "",
    o_auth_token_url: str = "",
    bearer_auth_token: str = "",
    http_proxy: str = "",
    https_proxy: str = "",
    time_out: int = 200,
    connection_time_out: int = 60,
    ssl_verify: str = True,  # noqa: FBT002
    trust_env: bool = True,  # noqa: FBT001, FBT002
    encoded_ids: bool = True,  # noqa: FBT001, FBT002
) -> SdkWrapper | None:
    """Create a wrapper for a AAS server connection from the given parameters.

    :param base_url: Base URL of the AAS server, e.g. "http://basyx_python_server:80/"
    :param basic_auth_username: Username for the AAS server basic authentication, defaults to ""
    :param basic_auth_password: Password for the AAS server basic authentication, defaults to ""
    :param o_auth_client_id: Client ID for OAuth authentication, defaults to ""
    :param o_auth_client_secret: Client secret for OAuth authentication, defaults to ""
    :param o_auth_token_url: Token URL for OAuth authentication, defaults to ""
    :param bearer_auth_token: Bearer token for authentication, defaults to ""
    :param http_proxy: HTTP proxy URL, defaults to ""
    :param https_proxy: HTTPS proxy URL, defaults to ""
    :param time_out: Timeout for the API calls, defaults to 200
    :param connection_time_out: Timeout for the connection to the API, defaults to 60
    :param ssl_verify: Whether to verify SSL certificates, defaults to True
    :param trust_env: Whether to trust environment variables for proxy settings, defaults to True
    :param encoded_ids: If enabled, all IDs used in API requests have to be base64-encoded
    :return: An instance of SdkWrapper initialized with the provided parameters or None if initialization fails
    """
    logger.info(f"Create AAS server http client from URL '{base_url}'.")
    config_dict: dict[str, str] = {}
    config_dict["BaseUrl"] = base_url
    config_dict["HttpProxy"] = http_proxy
    config_dict["HttpsProxy"] = https_proxy
    config_dict["TimeOut"] = time_out
    config_dict["ConnectionTimeOut"] = connection_time_out
    config_dict["SslVerify"] = ssl_verify
    config_dict["TrustEnv"] = trust_env
    config_dict["EncodedIds"] = encoded_ids

    config_dict["AuthenticationSettings"] = {
        "BasicAuth": {"Username": basic_auth_username},
        "OAuth": {
            "ClientId": o_auth_client_id,
            "TokenUrl": o_auth_token_url,
        },
    }

    return create_wrapper_by_dict(config_dict, basic_auth_password, o_auth_client_secret, bearer_auth_token)


def create_wrapper_by_dict(
    configuration: dict, basic_auth_password: str = "", o_auth_client_secret: str = "", bearer_auth_token: str = ""
) -> SdkWrapper | None:
    """Create a wrapper for a AAS server connection from the given configuration.

    :param configuration: Dictionary containing the AAS server connection settings
    :param basic_auth_password: Password for the AAS server basic authentication, defaults to ""
    :param o_auth_client_secret: Client secret for OAuth authentication, defaults to ""
    :param bearer_auth_token: Bearer token for authentication, defaults to ""
    :return: An instance of SdkWrapper initialized with the provided parameters or None if initialization fails
    """
    logger.info("Create AAS server wrapper from dictionary.")
    config_string = json.dumps(configuration, indent=4)
    return SdkWrapper(config_string, basic_auth_password, o_auth_client_secret, bearer_auth_token)


def create_wrapper_by_config(
    config_file: Path, basic_auth_password: str = "", o_auth_client_secret: str = "", bearer_auth_token: str = ""
) -> SdkWrapper | None:
    """Create a wrapper for a AAS server connection from a given configuration file.

    :param config_file: Path to the configuration file containing the AAS server connection settings
    :param basic_auth_password: Password for the AAS server basic authentication, defaults to ""
    :param o_auth_client_secret: Client secret for OAuth authentication, defaults to ""
    :param bearer_auth_token: Bearer token for authentication, defaults to ""
    :return: An instance of SdkWrapper initialized with the provided parameters or None if initialization fails
    """
    logger.info(f"Create AAS wrapper client from configuration file '{config_file}'.")
    if not config_file.exists():
        config_string = "{}"
        logger.warning(f"Configuration file '{config_file}' not found. Using default config.")
    else:
        config_string = config_file.read_text(encoding="utf-8")
        logger.debug(f"Configuration file '{config_file}' found.")
    return SdkWrapper(config_string, basic_auth_password, o_auth_client_secret, bearer_auth_token)


# endregion
