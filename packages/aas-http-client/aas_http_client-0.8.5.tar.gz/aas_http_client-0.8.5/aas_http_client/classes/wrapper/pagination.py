"""Pagination wrapper classes for AAS HTTP Client."""

import logging

from basyx.aas import model

from aas_http_client.utilities.sdk_tools import convert_to_object

logger = logging.getLogger(__name__)


class PagingMetadata:
    """Class representing pagination metadata."""

    cursor: str

    def __init__(self, cursor: str) -> None:
        """Initialize a paging metadata object.

        :param cursor: Cursor for the next page
        """
        self.cursor = cursor


class ShellPaginatedData:
    """Class representing paginated data for Asset Administration Shells."""

    paging_metadata: PagingMetadata
    results: list[model.AssetAdministrationShell]

    def __init__(self, cursor: str, results: list[model.AssetAdministrationShell]) -> None:
        """Initialize a paginated data object.

        :param paging_metadata: Paging metadata
        :param results: list of results
        """
        self.paging_metadata = PagingMetadata(cursor)
        self.results = results


class SubmodelPaginatedData:
    """Class representing paginated data for Submodels."""

    paging_metadata: PagingMetadata
    results: list[model.Submodel]

    def __init__(self, cursor: str, results: list[model.Submodel]) -> None:
        """Initialize a paginated data object.

        :param paging_metadata: Paging metadata
        :param results: list of results
        """
        self.paging_metadata = PagingMetadata(cursor)
        self.results = results


class SubmodelElementPaginatedData:
    """Class representing paginated data for Submodel Elements."""

    paging_metadata: PagingMetadata
    results: list[model.SubmodelElement]

    def __init__(self, cursor: str, results: list[model.SubmodelElement]) -> None:
        """Initialize a paginated data object.

        :param paging_metadata: Paging metadata
        :param results: list of results
        """
        self.paging_metadata = PagingMetadata(cursor)
        self.results = results


class ShellDescriptorPaginatedData:
    """Class representing paginated data for Shell Descriptors."""

    paging_metadata: PagingMetadata
    results: list[model.SubmodelElement]

    def __init__(self, cursor: str, results: list[model.SubmodelElement]) -> None:
        """Initialize a paginated data object.

        :param paging_metadata: Paging metadata
        :param results: list of results
        """
        self.paging_metadata = PagingMetadata(cursor)
        self.results = results


def create_shell_paging_data(content: dict) -> ShellPaginatedData:
    """Create a ShellPaginatedData object from a dictionary.

    :param content: Dictionary containing paginated shell data
    :return: ShellPaginatedData object
    """
    aas_list: list[model.AssetAdministrationShell] = []

    results: list = content.get("result", [])
    if not results or len(results) == 0:
        logger.warning("No shells found on server.")
        return ShellPaginatedData(cursor="", results=[])

    for result in results:
        if not isinstance(result, dict):
            logger.error(f"Invalid shell data: {result}")
            return None

        aas = convert_to_object(result)

        if aas:
            aas_list.append(aas)

    cursor = ""
    paging_metadata_dict = content.get("paging_metadata", {})

    if "cursor" in paging_metadata_dict:
        cursor = paging_metadata_dict["cursor"]

    return ShellPaginatedData(
        cursor=cursor,
        results=aas_list,
    )


def create_submodel_paging_data(content: dict) -> SubmodelPaginatedData:
    """Create a SubmodelPaginatedData object from a dictionary.

    :param content: Dictionary containing paginated submodel data
    :return: SubmodelPaginatedData object
    """
    sm_list: list[model.Submodel] = []

    results: list = content.get("result", [])
    if not results or len(results) == 0:
        logger.warning("No shells found on server.")
        return SubmodelPaginatedData(cursor="", results=[])

    for result in results:
        if not isinstance(result, dict):
            logger.error(f"Invalid shell data: {result}")
            return None

        sm = convert_to_object(result)

        if sm:
            sm_list.append(sm)

    cursor = ""
    paging_metadata_dict = content.get("paging_metadata", {})

    if "cursor" in paging_metadata_dict:
        cursor = paging_metadata_dict["cursor"]

    return SubmodelPaginatedData(
        cursor=cursor,
        results=sm_list,
    )


def create_submodel_element_paging_data(content: dict) -> SubmodelElementPaginatedData:
    """Create a SubmodelElementPaginatedData object from a dictionary.

    :param content: Dictionary containing paginated submodel element data
    :return: SubmodelElementPaginatedData object
    """
    sme_list: list[model.SubmodelElement] = []

    results: list = content.get("result", [])
    if not results or len(results) == 0:
        logger.warning("No shells found on server.")
        return SubmodelElementPaginatedData(cursor="", results=[])

    for result in results:
        if not isinstance(result, dict):
            logger.error(f"Invalid shell data: {result}")
            return None

        sme = convert_to_object(result)

        if sme:
            sme_list.append(sme)

    cursor = ""
    paging_metadata_dict = content.get("paging_metadata", {})

    if "cursor" in paging_metadata_dict:
        cursor = paging_metadata_dict["cursor"]

    return SubmodelElementPaginatedData(
        cursor=cursor,
        results=sme_list,
    )


def create_shell_descriptor_paging_data(content: dict) -> SubmodelElementPaginatedData:
    """Create a SubmodelElementPaginatedData object from a dictionary.

    :param content: Dictionary containing paginated submodel element data
    :return: SubmodelElementPaginatedData object
    """
    sme_list: list[model.SubmodelElement] = []

    results: list = content.get("result", [])
    if not results or len(results) == 0:
        logger.warning("No shells found on server.")
        return SubmodelElementPaginatedData(cursor="", results=[])

    for result in results:
        if not isinstance(result, dict):
            logger.error(f"Invalid shell data: {result}")
            return None

        sme = convert_to_object(result)

        if sme:
            sme_list.append(sme)

    cursor = ""
    paging_metadata_dict = content.get("paging_metadata", {})

    if "cursor" in paging_metadata_dict:
        cursor = paging_metadata_dict["cursor"]

    return SubmodelElementPaginatedData(
        cursor=cursor,
        results=sme_list,
    )
