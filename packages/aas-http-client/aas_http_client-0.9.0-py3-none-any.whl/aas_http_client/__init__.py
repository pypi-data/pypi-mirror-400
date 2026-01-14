"""AAS HTTP Client Package."""

import importlib.metadata
from datetime import datetime, timezone

from aas_http_client.classes.client.aas_client import AasHttpClient, create_client_by_config, create_client_by_dict, create_client_by_url
from aas_http_client.classes.wrapper.sdk_wrapper import SdkWrapper, create_wrapper_by_config, create_wrapper_by_dict, create_wrapper_by_url
from aas_http_client.utilities import encoder, model_builder, sdk_tools
from aas_http_client.utilities.version_check import check_for_update

__copyright__ = f"Copyright (C) {datetime.now(tz=timezone.utc).year} :em engineering methods AG. All rights reserved."
__author__ = "Daniel Klein"

try:
    __license__ = "MIT"
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0-dev"

__project__ = "aas-http-client"
__package__ = "aas-http-client"

check_for_update()

__all__ = [
    "AasHttpClient",
    "SdkWrapper",
    "create_client_by_config",
    "create_client_by_dict",
    "create_client_by_url",
    "create_wrapper_by_config",
    "create_wrapper_by_dict",
    "create_wrapper_by_url",
    "encoder",
    "model_builder",
    "sdk_tools",
]
