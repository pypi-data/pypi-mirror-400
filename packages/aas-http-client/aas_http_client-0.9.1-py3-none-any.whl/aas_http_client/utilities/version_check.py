"""Utility functions for version checking."""

import importlib.metadata
import logging

import requests

logger = logging.getLogger(__name__)


def check_for_update(package_name="aas-http-client"):
    """Check for updates of the package on PyPI.

    :param package_name: The name of the package to check for updates, defaults to "aas-http-client"
    """
    try:
        current_version = importlib.metadata.version(package_name)
        pypi_url = f"https://pypi.org/pypi/{package_name}/json"
        latest_version = requests.get(pypi_url, timeout=3).json()["info"]["version"]

        if current_version != latest_version:
            print(
                f"⚠️  A new version for package '{package_name}' is available: "
                f"{latest_version} (currently installed: {current_version}). "
                f"Use the following command to update the package: pip install --upgrade {package_name}"
            )
    except Exception as exc:
        logger.exception(f"Exception occurred while checking for package update: {exc}")
