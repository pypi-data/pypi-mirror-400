# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

import os
import sys

import yaml
from cryptography.fernet import Fernet


def get_qairt_dev_config() -> dict:
    """Loads and returns the QAIRT DEV config.

    Returns:
        dict: The QAIRT DEV config
    """
    top_level_module = sys.modules.get("qairt", None)
    if top_level_module is None or top_level_module.__file__ is None:
        raise RuntimeError("Unable to locate QAIRT DEV Config in package")
    qairt_pkg_dir = os.path.dirname(top_level_module.__file__)
    qairt_dev_config = os.path.join(qairt_pkg_dir, "qairt_dev_config.yaml")
    with open(qairt_dev_config, "r") as f:
        return dict(yaml.safe_load(f))


_CONFIG_DICT = get_qairt_dev_config()


def get_default_qairt_sdk_version() -> str:
    """Returns the default QAIRT SDK version used in the current QAIRT DEV installation.

    Returns:
        str: The default QAIRT SDK version.
    """
    return _CONFIG_DICT["default_qairt_version"]


def get_min_qairt_sdk_version() -> str:
    """Returns the minimum QAIRT SDK version required for the current QAIRT DEV installation.
    This is used to ensure compatibility with the QAIRT DEV tools.

    Returns:
        str: The minimum QAIRT SDK version.
    """
    return _CONFIG_DICT["min_qairt_version"]


def get_qairt_sdk_qsc_product_id() -> str:
    """Returns the QAIRT SDK product ID provided by Qualcomm Software Center.

    Returns:
        str: The QAIRT SDK product ID.
    """
    return _CONFIG_DICT["qairt_qsc_product_id"]


def get_qsc_api_key() -> str:
    """Returns the API key used to authenticate with the Qualcomm Software Center.

    Returns:
        str: The decrypted API key.
    """
    encrypted_api_key = _CONFIG_DICT["qsc_api_token"]
    fernet_qairt_key = b"ff7aaub6Hheq8ZMi0ZkgfX3PEHcbek72_YDnsOMhSqI="
    fernet_qairt_obj = Fernet(fernet_qairt_key)
    api_key = fernet_qairt_obj.decrypt(encrypted_api_key.encode()).decode()
    return api_key
