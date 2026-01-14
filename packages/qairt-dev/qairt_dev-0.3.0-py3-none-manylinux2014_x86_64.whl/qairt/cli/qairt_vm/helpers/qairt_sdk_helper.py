# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

import os
import shutil
import ssl
import subprocess
from typing import Callable

import click
import requests
import yaml

from qairt.cli.qairt_vm.utils import config_utils
from qairt.cli.qairt_vm.utils.logging import qairt_vm_logger

QAIRT_SDK_QSC_URL_BASE = (
    f"https://softwarecenter.qualcomm.com/api/download/software/sdks/Qualcomm_AI_Runtime_Community/All"
)
QAIRT_SDK_QSC_URL_API_BASE = "https://apigwx-aws.qualcomm.com/saga/api/qsc/public/v1/tools"
QAIRT_SDK_VERIFY_FILE = "sdk.yaml"
_AVAILABLE_SDK_VERSIONS: dict = {}


def _get_request_wrapper(url: str, **kwargs) -> requests.Response:
    """
    This function serves as a wrapper helper for the requests.get() method that allows for retry without
    SSL certificate verification

    Args:
        url (str): The URL to send the GET request to.
        **kwargs (dict): Additional keyword arguments to pass to the requests.get method.

    Returns:
        requests.Response: The response object from the GET request.

    Raises:
        requests.RequestException: If there was an error sending the request.
    """

    def __get_request_wrapper(ssl_cert_verify=None):
        return requests.get(url=url, stream=True, verify=ssl_cert_verify, **kwargs)

    verify = (
        ssl.get_default_verify_paths().cafile
        if os.getenv("REQUEST_VERIFY", "true").lower() == "true"
        else False
    )
    try:
        response = __get_request_wrapper(ssl_cert_verify=verify)
    except requests.exceptions.SSLError:
        qairt_vm_logger.warning(f"Unable to fetch from {url} due to SSL cert verification error.")
        if click.confirm(
            "Would you like to disable SSL cert verification?",
            default=None,
            abort=True,
            err=True,
        ):
            response = __get_request_wrapper(ssl_cert_verify=False)
        else:
            raise requests.exceptions.SSLError(
                f"Unable to proceed further fetching from {url} due to SSL cert verification error"
            ) from None

    return response


def _run_command_wrapper(command: str, suppress_output: bool = False, working_dir: str = os.curdir) -> bool:
    """
    This function serves as wrapper helper for running subprocess commands with support to suppress output

    Args:
        command (str): The command to run.
        suppress_output (bool): If True, suppresses the output of the command. Defaults to False.
        working_dir (str): The working directory for running the module. Defaults to the current directory.

    Returns:
        bool: Whether the command was successful.
    """
    std_stream = None
    if suppress_output:
        std_stream = subprocess.DEVNULL
    try:
        ret = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            stdout=std_stream,
            stderr=std_stream,
        )
        if ret.returncode != 0:
            return False
    except BaseException as e:
        if not suppress_output:
            qairt_vm_logger.error(e)
        return False

    return True


def _get_available_qairt_sdk_versions() -> dict:
    """Returns a list of available QAIRT SDK versions available for download.

    Returns:
        dict: A dict of available QAIRT SDK versions where key is the version and value is the build number.
    """
    global _AVAILABLE_SDK_VERSIONS
    if _AVAILABLE_SDK_VERSIONS:
        return _AVAILABLE_SDK_VERSIONS
    qairt_prod_id = config_utils.get_qairt_sdk_qsc_product_id()
    auth_key = config_utils.get_qsc_api_key()
    url = f"{QAIRT_SDK_QSC_URL_API_BASE}/{qairt_prod_id}/releases"
    response = _get_request_wrapper(url, headers={"X-QCOM-TokenType": "apikey", "Authorization": auth_key})
    if response.status_code == 200:
        qairt_sdk_list = sorted(response.json()["data"], key=lambda qst: qst["version"], reverse=False)
        _AVAILABLE_SDK_VERSIONS = {
            qairt_sdk["version"].rsplit(".", 1)[0]: (
                qairt_sdk["version"].rsplit(".", 1)[1],
                qairt_sdk["releaseDate"],
            )
            for qairt_sdk in qairt_sdk_list
        }
        return _AVAILABLE_SDK_VERSIONS
    else:
        raise RuntimeError(f"Unable to fetch QAIRT SDK versions. Get request failed with\n {response.text}\n")


def get_supported_sdk_versions() -> dict:
    """
    Returns a dictionary of supported QAIRT SDK versions for the current QAIRT Dev version avialable for
    download.

    Returns:
        dict: A dictionary containing the supported QAIRT SDK versions.
    """
    available_sdks = _get_available_qairt_sdk_versions()
    min_qairt_version = config_utils.get_min_qairt_sdk_version()
    return {version: details for version, details in available_sdks.items() if version >= min_qairt_version}


def get_version_build(version: str) -> str:
    """Returns the build number of the given version."""
    if get_supported_sdk_versions().get(version) is None:
        raise RuntimeError(f"Unsupported QAIRT SDK version: {version} requested")
    return str(get_supported_sdk_versions()[version][0])


def is_supported_version(version: str) -> bool:
    """Check if the given version is supported QAIRT SDK by QAIRT Dev and available for download.

    Args:
        version (str): The version to check.

    Returns:
        bool: True if the given version is supported, False otherwise.
    """
    return get_supported_sdk_versions().get(version) is not None


def get_version_from_path(qairt_sdk_root: str) -> str:
    """Returns the version of the QAIRT SDK located at the given path.

    Args:
        qairt_sdk_root (str): The path to the QAIRT SDK root directory.

    Returns:
        str: The version of the QAIRT SDK located at the given path.

    Raises:
        RuntimeError: If the given path does not contain a valid QAIRT SDK installation.
    """
    verify_path = os.path.join(qairt_sdk_root, QAIRT_SDK_VERIFY_FILE)
    if not os.path.exists(verify_path):
        raise RuntimeError(f"Unable to find expected file {verify_path} in the given QAIRT SDK root")
    return yaml.safe_load(open(verify_path, "r"))["version"]


def is_supported_qairt_sdk(qairt_sdk_root: str) -> bool:
    """Check if the given QAIRT SDK is supported by QAIRT Dev.

    Args:
        qairt_sdk_root (str): The path to the QAIRT SDK root directory.

    Returns:
        bool: True if the given QAIRT SDK version is supported and verify path is present, False otherwise.
    """
    try:
        sdk_version = get_version_from_path(qairt_sdk_root)
    except RuntimeError:
        return False

    min_supported_version = config_utils.get_min_qairt_sdk_version()
    default_supported_version = config_utils.get_default_qairt_sdk_version()
    if sdk_version > default_supported_version:
        qairt_vm_logger.warning(
            f"The QAIRT SDK version ({sdk_version}) exceeds the default tested version "
            f"({default_supported_version}) for the SDK located at {qairt_sdk_root}. "
            f"Functionality may not work as expected with the current QAIRT Dev version."
        )
    return sdk_version >= min_supported_version


def get_latest_qairt_sdk_version() -> str:
    """
    Returns the latest version of QAIRT SDK.

    Returns:
        str: The latest version of QAIRT SDK.
    """
    return max(get_supported_sdk_versions().keys())


def download_and_extract_qairt_sdk(
    version: str, zip_extract_path: str, unzip_platform_func: Callable
) -> None:
    """
    Downloads and extracts the QAIRT SDK for the specified version.

    Args:
        version (str): The version of the QAIRT SDK to download.
        zip_extract_path (str): The path where the zip file will be downloaded and extracted.
        unzip_platform_func (Callable): platform specific function to unzip the downloaded zip file.

    Raises:
        RuntimeError: If the specified version is not supported or if the download and extraction
        process fails.
        requests.exceptions.SSLError: If there was an error sending the request due to SSL cert verification.
    """
    try:
        if not is_supported_version(version):
            raise RuntimeError(f"Unsupported QAIRT SDK version: {version} requested for download")
        version_full = f"{version}.{get_version_build(version)}"
        zip_download_path = os.path.join(zip_extract_path, f"{version_full}.zip")
        url = QAIRT_SDK_QSC_URL_BASE + f"/{version_full}/v{version_full}.zip"
        qairt_vm_logger.info(f"Fetching QAIRT SDK, version {version} to location {zip_extract_path}")
        qairt_root_dir = os.path.join(zip_extract_path, "qairt", version_full)
        if os.path.exists(qairt_root_dir):
            if click.confirm(
                f"Existing QAIRT SDK installation found at {qairt_root_dir}. Would you like to remove "
                f"and fetch again?",
                default=None,
                abort=True,
                err=True,
            ):
                try:
                    shutil.rmtree(qairt_root_dir)
                except FileNotFoundError:
                    pass
        os.makedirs(zip_extract_path, exist_ok=True)
        response = _get_request_wrapper(url=url)
        if response.status_code == 200:
            with open(zip_download_path, "wb") as file:
                file.write(response.content)
        else:
            raise RuntimeError(
                f"Unable to fetch QAIRT version {version_full}. Get request failed with\n {response.text}\n"
            )

        qairt_vm_logger.info(f"Unzipping QAIRT SDK, Version {version} at {zip_download_path}")
        unzip_platform_cmd = unzip_platform_func(zip_download_path, zip_extract_path)
        ret_code = subprocess.run(
            unzip_platform_cmd,
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        verify_path = os.path.join(zip_extract_path, "qairt", version_full, QAIRT_SDK_VERIFY_FILE)
        if ret_code.returncode != 0 or not os.path.exists(verify_path):
            raise RuntimeError(
                f"Extracting QAIRT SDK {zip_download_path} failed. Unable to find expected "
                f"files at {verify_path}"
            )
    except requests.exceptions.SSLError:
        raise requests.exceptions.SSLError(
            "Unable to do post install and setup for QAIRT DEV, post install failed to fetch files "
            "due to inability to verify SSL certs. If you would like to disable cert checking, "
            "set environment variable REQUEST_VERIFY=false"
        ) from None


def run_qairt_os_deps(
    platform_os_deps_func: Callable,
    dry_run: bool = False,
    suppress_output: bool = False,
    working_dir: str = os.curdir,
) -> bool:
    """
    Runs the QAIRT OS dependencies.

    Args:
        platform_os_deps_func (Callable): A function that returns the platform specific QAIRT OS
            dependencies module.
        dry_run (bool): If True, does not actually run the command, but instead prints
            what would be run. Defaults to False.
        suppress_output (bool): If True, suppresses the output of the command. Defaults
            to False.
        working_dir (str): The working directory for running the module. Defaults to the current directory.

    Returns:
        bool: Whether the command was successful.
    """
    options = ""
    if dry_run:
        options = options + " -n "
    return _run_command_wrapper(
        platform_os_deps_func(options),
        suppress_output=suppress_output,
        working_dir=working_dir,
    )


def run_qairt_py_deps(
    with_optional: bool = False,
    dry_run: bool = False,
    suppress_output: bool = False,
    working_dir: str = os.curdir,
) -> bool:
    """
    Runs the QAIRT python dependencies.

    Args:
        with_optional: If True, includes optional dependencies. Defaults to False.
        dry_run: If True, does not actually run the command, but instead prints
            what would be run. Defaults to False.
        suppress_output: If True, suppresses the output of the command. Defaults
            to False.
        working_dir (str): The working directory for running the module. Defaults to the current directory.

    Returns:
        bool: Whether the command was successful.
    """
    options = ""
    if dry_run:
        options = options + " --dry-run "
    if with_optional:
        options = options + " --with_optional "
    return _run_command_wrapper(
        f"python check-python-dependency {options}",
        suppress_output=suppress_output,
        working_dir=working_dir,
    )
