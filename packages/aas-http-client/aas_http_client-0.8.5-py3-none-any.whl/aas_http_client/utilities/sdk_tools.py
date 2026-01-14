"""Utility functions for working with the BaSyx SDK framework objects."""

import json
import logging
from typing import Any

import basyx.aas.adapter.json
from basyx.aas import model

logger = logging.getLogger(__name__)


def add_submodel_to_aas(aas: model.AssetAdministrationShell, submodel: model.Submodel) -> None:
    """Add a given Submodel correctly to a provided AssetAdministrationShell.

    :param aas: provided AssetAdministrationShell to which the Submodel should be added
    :param submodel: given Submodel to add
    """
    aas.submodel.add(model.ModelReference.from_referable(submodel))


def remove_submodel_from_aas(aas: model.AssetAdministrationShell, submodel: model.Submodel) -> None:
    """Remove a given Submodel correctly from a provided AssetAdministrationShell.

    :param aas: provided AssetAdministrationShell from which the Submodel should be removed
    :param submodel: given Submodel to remove
    """
    aas.submodel.remove(model.ModelReference.from_referable(submodel))


def convert_to_object(content: dict) -> Any | None:
    """Convert a dictionary to a BaSyx SDK framework object.

    :param content: dictionary to convert
    :return: BaSyx SDK framework object or None
    """
    if not content or len(content) == 0:
        logger.debug("Empty content provided for conversion to object.")
        return None

    try:
        dict_string = json.dumps(content)
        model_object = json.loads(dict_string, cls=basyx.aas.adapter.json.AASFromJsonDecoder)
        return model_object
    except Exception as e:
        logger.error(f"Decoding error: {e}")
        logger.error(f"In JSON: {content}")
        return None


def convert_to_dict(object: Any) -> dict | None:
    """Convert a BaSyx SDK framework object. to a dictionary.

    :param object: BaSyx SDK framework object to convert
    :return: dictionary representation of the object or None
    """
    if not object:
        logger.debug("Empty object provided for conversion to dictionary.")
        return None

    try:
        data_string = json.dumps(object, cls=basyx.aas.adapter.json.AASToJsonEncoder)
        model_dict = json.loads(data_string)
        return model_dict
    except Exception as e:
        logger.error(f"Encoding error: {e}")
        logger.error(f"In object: {object}")
        return None
