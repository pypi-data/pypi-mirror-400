# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

import os
import subprocess
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

import click

from qairt.cli.qairt_vm.helpers import qairt_sdk_helper
from qairt.cli.qairt_vm.utils import config_utils
from qairt.cli.qairt_vm.utils.confirm_utils import confirm
from qairt.cli.qairt_vm.utils.logging import qairt_vm_logger


class QAIRTDevReqs(Enum):
    QAIRT_SDK_INSTALL = "qairt_SDK_install"
    QAIRT_OS_DEPS = "qairt_os_deps"
    QAIRT_PY_DEPS = "qairt_py_deps"


class BaseQairtVmContext(ABC):
    """
    This class is the base class for all the classes that implement the
    functionality of the qairt-vm command.
    """

    def __init__(
        self,
        zip_extract_dest: str,
        qairt_platform: str,
        *,
        qairt_root_dir: Optional[str] = None,
    ):
        """Initializes the BaseQairtVmContext.
        Args:
            zip_extract_dest: The location of where the downloaded file should be
                extracted to.
            qairt_platform: The qairt platform tag in the SDK for the given os
                and architecture.
            qairt_root_dir: The root directory of the qairt installation. If not
                provided, it will default to qairt_platform_root_dir.
        """
        self.default_qairt_version = config_utils.get_default_qairt_sdk_version()
        self.qairt_min_version = config_utils.get_min_qairt_sdk_version()
        self.qairt_version_full = (
            f"{self.default_qairt_version}.{qairt_sdk_helper.get_version_build(self.default_qairt_version)}"
        )
        self.zip_download_path = os.path.join(zip_extract_dest, f"{self.default_qairt_version}.zip")
        self.zip_extract_path = zip_extract_dest
        self.qairt_platform = qairt_platform
        self.default_qairt_root_dir = os.path.join(zip_extract_dest, "qairt", self.qairt_version_full)
        self.default_verify_path = os.path.join(
            self.default_qairt_root_dir, qairt_sdk_helper.QAIRT_SDK_VERIFY_FILE
        )
        self._set_qairt_root_vars(qairt_root_dir)

    def _set_qairt_root_vars(self, qairt_root_dir: Optional[str] = None):
        if qairt_root_dir is None:
            self.qairt_root_dir = self.default_qairt_root_dir
        else:
            self.qairt_root_dir = qairt_root_dir
        self.verify_path = os.path.join(self.qairt_root_dir, qairt_sdk_helper.QAIRT_SDK_VERIFY_FILE)
        self.qairt_bin_dir = os.path.join(self.qairt_root_dir, "bin")
        self.qairt_os_lib_dir = os.path.join(self.qairt_root_dir, "lib", self.qairt_platform)
        self.qairt_py_lib_dir = os.path.join(self.qairt_root_dir, "lib", "python")

    def check_qairt_dev_env(self, suppress_output: bool = True) -> list[QAIRTDevReqs]:
        """Iterates and checks applicable missing packages and/or versions mismatches required by qairt-dev.
        Args:
            suppress_output: Whether to suppress output. Defaults to True.

        Returns:
            list[QAIRTDevReqs]: A list of unmet requirements.
        """

        missing_reqs = []

        # Check 1: Verify expected QAIRT SDK installation
        if not qairt_sdk_helper.is_supported_qairt_sdk(self.qairt_root_dir):
            qairt_vm_logger.error(
                f"QAIRT SDK installation is missing or incompatible. Expected a minimum version of "
                f"{self.qairt_min_version} or higher. Ensure QAIRT_SDK_ROOT is set correctly, "
                f"or install the default version {self.default_qairt_version}."
            )
            missing_reqs.extend(
                [QAIRTDevReqs.QAIRT_SDK_INSTALL, QAIRTDevReqs.QAIRT_OS_DEPS, QAIRTDevReqs.QAIRT_PY_DEPS]
            )
            return missing_reqs

        # Check 2: Verify if missing QAIRT OS Dependency
        if not qairt_sdk_helper.run_qairt_os_deps(
            platform_os_deps_func=self._get_os_deps_cmd,
            dry_run=True,
            suppress_output=suppress_output,
            working_dir=self.qairt_bin_dir,
        ):
            qairt_vm_logger.error(f"Missing expected QAIRT OS Dependencies on system.")
            missing_reqs.append(QAIRTDevReqs.QAIRT_OS_DEPS)

        # Check 3: Verify missing QAIRT Python Dependency
        if not qairt_sdk_helper.run_qairt_py_deps(
            with_optional=False, dry_run=True, suppress_output=suppress_output, working_dir=self.qairt_bin_dir
        ):
            qairt_vm_logger.error(f"Missing expected QAIRT Python Dependencies in environment.")
            missing_reqs.append(QAIRTDevReqs.QAIRT_PY_DEPS)

        return missing_reqs

    def inspect(self, verbose: bool = False) -> None:
        """Dry run inspection to check if any missing packages and/or versions mismatches
        required by qairt-dev.

        Args:
            verbose: Whether to print out detailed inspection results. Defaults to False.
        """
        suppress_output = not verbose
        if len(self.check_qairt_dev_env(suppress_output=suppress_output)):
            if self.default_qairt_root_dir != self.qairt_root_dir:
                qairt_vm_logger.error(
                    f"Custom QAIRT SDK location is set at {self.qairt_root_dir}. Please "
                    f"fix SDK setup at location or use default QAIRT installation that "
                    f"comes with qairt-vm and unset QAIRT_SDK_ROOT environment variable to proceed."
                )
            raise RuntimeError(
                "QAIRT-VM Inspection Failed. Please run `qairt-vm -f/--fix` to resolve issues."
            )

        qairt_vm_logger.info(
            f"Found QAIRT SDK at location: {self.qairt_root_dir} and all dependencies are met!"
        )
        qairt_vm_logger.info("QAIRT-VM Inspection Passed!")

    def fix(self, verbose: bool = False, accept_all: bool = False) -> None:
        """Iterates and installs applicable missing packages and/or versions mismatches required by qairt-dev.

        Args:
            verbose: Whether to print out detailed inspection results.
            accept_all: If True, run non-interactively and accept all prompts automatically.
        """
        suppress_output = not verbose
        try:
            # run with suppress output to avoid noise of print out for all checks at once. If there is missing
            # requirement, we will re-run the individual checks without output suppression
            missing_reqs = self.check_qairt_dev_env(suppress_output=True)
            if len(missing_reqs):
                qairt_vm_logger.info("Attempting to fix missing requirements for QAIRT DEV...")
                for missing_req in missing_reqs:
                    if missing_req == QAIRTDevReqs.QAIRT_SDK_INSTALL:
                        if self.qairt_root_dir != self.default_qairt_root_dir and os.path.exists(
                            self.default_verify_path
                        ):
                            if confirm(
                                accept_all,
                                f"Missing QAIRT SDK dependency at {self.qairt_root_dir}, "
                                f"however, expected QAIRT SDK found at {self.default_qairt_root_dir}, "
                                f"would you like to use that location?",
                                default=None,
                                abort=True,
                                err=True,
                            ):
                                self._set_qairt_root_vars()
                        else:
                            if confirm(
                                accept_all,
                                f"Missing QAIRT SDK dependency, would you like to install QAIRT, "
                                f"version: {self.default_qairt_version}?",
                                default=None,
                                abort=True,
                                err=True,
                            ):
                                qairt_sdk_helper.download_and_extract_qairt_sdk(
                                    version=self.default_qairt_version,
                                    zip_extract_path=self.zip_extract_path,
                                    unzip_platform_func=self._get_unzip_command,
                                )

                                # Given the SDK dependency was missing, reset qairt root vars to use
                                # default location
                                self._set_qairt_root_vars()
                        qairt_vm_logger.info(f"QAIRT ROOT DIR set at: {self.qairt_root_dir}")
                    elif missing_req == QAIRTDevReqs.QAIRT_OS_DEPS:
                        if not qairt_sdk_helper.run_qairt_os_deps(
                            platform_os_deps_func=self._get_os_deps_cmd,
                            dry_run=True,
                            suppress_output=suppress_output,
                            working_dir=self.qairt_bin_dir,
                        ):
                            if confirm(
                                accept_all,
                                f"Missing required OS dependencies, would you like to install?",
                                default=None,
                                abort=True,
                                err=True,
                            ):
                                qairt_vm_logger.info("Installing QAIRT OS dependencies...")
                                qairt_sdk_helper.run_qairt_os_deps(
                                    platform_os_deps_func=self._get_os_deps_cmd,
                                    suppress_output=suppress_output,
                                    working_dir=self.qairt_bin_dir,
                                )
                    elif missing_req == QAIRTDevReqs.QAIRT_PY_DEPS:
                        if not qairt_sdk_helper.run_qairt_py_deps(
                            dry_run=True, suppress_output=suppress_output, working_dir=self.qairt_bin_dir
                        ):
                            if confirm(
                                accept_all,
                                f"Missing required Python dependencies, would you like to install?",
                                default=None,
                                abort=True,
                                err=True,
                            ):
                                with_optional = confirm(
                                    accept_all,
                                    f"Would you like to install with optional dependencies?",
                                    default=None,
                                    err=True,
                                )
                                qairt_vm_logger.info("Installing QAIRT Python dependencies...")
                                qairt_sdk_helper.run_qairt_py_deps(
                                    with_optional=with_optional,
                                    suppress_output=suppress_output,
                                    working_dir=self.qairt_bin_dir,
                                )
            qairt_vm_logger.info("Verifying requirements are met...")
            if len(self.check_qairt_dev_env(suppress_output=suppress_output)):
                raise RuntimeError(
                    "Unable to fix post install and setup for QAIRT DEV, please check logs for errors."
                )
            qairt_vm_logger.info("QAIRT DEV post install and setup complete.")
        except BaseException as e:
            raise RuntimeError(f"Unable to do post install and setup for QAIRT DEV. \n {e}")

    def fetch_sdk(self, version: str, out_dir: Optional[str] = None) -> None:
        """
        Downloads QAIRT SDK for  the specified version and extracts it to the provided
        output directory.

        Args:
            version (str): The version of the QAIRT SDK to fetch. Can be "latest" or "default" to fetch the
            latest or default version respectively.
            out_dir (Optional[str], optional): The directory where the fetched SDK will be extracted.
            Defaults to None, which means the SDK will be extracted to the default location for the platform.

        Raises:
            RuntimeError: If the requested QAIRT SDK version is unsupported or the provided output directory
            does
            not exist.
        """
        if version == "latest":
            version = qairt_sdk_helper.get_latest_qairt_sdk_version()
        elif version == "default":
            version = config_utils.get_default_qairt_sdk_version()
        if not qairt_sdk_helper.is_supported_version(version):
            raise RuntimeError(
                f"Requested QAIRT SDK version '{version}' is unsupported. Please run `qairt-vm fetch --list`)"
            )
        if out_dir is not None and not os.path.exists(out_dir):
            raise RuntimeError(
                f"Provided output directory {out_dir} for storing the requested SDK does not exist."
            )
        try:
            qairt_sdk_helper.download_and_extract_qairt_sdk(
                version=version,
                zip_extract_path=out_dir if out_dir else self.zip_extract_path,
                unzip_platform_func=self._get_unzip_command,
            )
        except click.exceptions.Abort:
            qairt_vm_logger.warning(f"Aborted Fetching QAIRT SDK version {version}.")
        except BaseException as e:
            raise RuntimeError(f" Unable to fetch QAIRT SDK version {version}.\n Reason: {e}")

    @staticmethod
    def list_sdks() -> None:
        """
        Lists all available QAIRT SDKs.

        This function retrieves the list of available QAIRT SDKs. It then prints out the list in a
        formatted table, including the version number, release date, and details such as build information,
        and whether it is the latest or default version.
        """
        qairt_vm_logger.info("Fetching SDK list...")
        qairt_sdks = qairt_sdk_helper.get_supported_sdk_versions()
        latest_version = qairt_sdk_helper.get_latest_qairt_sdk_version()
        default_version = config_utils.get_default_qairt_sdk_version()
        max_version_len = max(len(version) for version in qairt_sdks)
        max_version_len_border = max_version_len + 3
        max_rel_date_len = max(len(rel_date) for _, (_, rel_date) in qairt_sdks.items())
        max_rel_date_len_border = max_rel_date_len + 3
        max_details_len = max(
            len(f"{version}.{build} *latest *default") for version, (build, _) in qairt_sdks.items()
        )
        max_details_len_border = max_details_len + 2
        # Table header
        print("Available QAIRT SDKs:".rjust(max_version_len))
        print(
            f"+{'-' * max_version_len_border}+{'-' * max_rel_date_len_border}+{'-' * max_details_len_border}+"
        )
        print(
            f"| {'Version'.ljust(max_version_len)} | "
            f"{'Release Date'.ljust(max_rel_date_len)}  | "
            f"{'Details'.ljust(max_details_len)} |"
        )
        # Table body
        print(
            f"+{'-' * max_version_len_border}+{'-' * max_rel_date_len_border}+{'-' * max_details_len_border}+"
        )
        for version, (build, release_date) in qairt_sdks.items():
            version_str = f"{version}.{build}"
            details_str = version_str
            if version == latest_version:
                details_str += " *latest"
            if version == default_version:
                details_str += " *default"
            print(
                f"| {version.ljust(max_version_len)}  | "
                f"{release_date.ljust(max_rel_date_len)}  | "
                f"{details_str.ljust(max_details_len)} |"
            )
        print(
            f"+{'-' * max_version_len_border}+{'-' * max_rel_date_len_border}+{'-' * max_details_len_border}+"
        )
        # Table footer
        print("Legend:")
        print("  *latest: Latest available QAIRT SDK version")
        print("  *default: Default QAIRT SDK version tested with qairt-dev")

    @abstractmethod
    def _get_unzip_command(self, zip_path: str, extract_path: str) -> str:
        """Get the command to unzip the given zip file to the specified extract path.
        Args:
            zip_path: The path to the zip file to extract.
            extract_path: The path to extract the zip file to.

        Returns:
            The command to unzip the zip file.
        """

    @abstractmethod
    def _get_os_deps_cmd(self, options: Optional[str] = None) -> str:
        """Gets the os deps command for the platform.

        Args:
            options: The options to pass to the os deps command.

        Returns:
            The os deps command string.
        """


class BaseWindowsQairtVmContext(BaseQairtVmContext):
    @staticmethod
    def _verify_powershell_in_env():
        cmd = "where.exe powershell"
        ret = subprocess.run(
            cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, encoding="utf-8"
        )
        if ret.returncode != 0:
            raise RuntimeError(
                f"Issue finding powershell in environment, please ensure powershell is installed and in "
                f"your PATH. \n"
                f"`{cmd}` failed with -> {ret.stderr}"
            )

    def _get_unzip_command(self, zip_path: str, extract_path: str) -> str:
        return f'tar -xf "{zip_path}" -C "{extract_path}"'

    def _get_os_deps_cmd(self, options: Optional[str] = None) -> str:
        prompt_y_cmd = r"function Read-Host { param([string]$prompt) return 'y' }"  # suppress any prompts
        return (
            f'powershell.exe -ExecutionPolicy Bypass -Command "{prompt_y_cmd}; '
            f"& '.\\check-windows-dependency.ps1' {options}\""
        )


class BaseLinuxQairtVmContext(BaseQairtVmContext):
    def _get_unzip_command(self, zip_path: str, extract_path: str) -> str:
        return f'unzip "{zip_path}" -d "{extract_path}"'

    def _get_os_deps_cmd(self, options: Optional[str] = None) -> str:
        return f"yes | sudo bash ./check-linux-dependency.sh {options}"


class WindowsX86QairtVmContext(BaseWindowsQairtVmContext):
    def __init__(self, *, qairt_root_dir: Optional[str] = None):
        self._verify_powershell_in_env()
        extract_location = os.path.join("C:\\", "Qualcomm", "AIStack")
        super().__init__(
            zip_extract_dest=extract_location,
            qairt_platform="x86_64-windows-msvc",
            qairt_root_dir=qairt_root_dir,
        )


class WindowsArm64QairtVmContext(BaseWindowsQairtVmContext):
    def __init__(self, *, qairt_root_dir: Optional[str] = None):
        self._verify_powershell_in_env()
        extract_location = os.path.join("C:\\", "Qualcomm", "AIStack")
        super().__init__(
            zip_extract_dest=extract_location,
            qairt_platform="arm64x-windows-msvc",
            qairt_root_dir=qairt_root_dir,
        )


class LinuxX86QairtVmContext(BaseLinuxQairtVmContext):
    def __init__(self, *, qairt_root_dir: Optional[str] = None):
        extract_location = os.path.join("/opt", "qcom", "aistack")
        super().__init__(
            zip_extract_dest=extract_location,
            qairt_platform="x86_64-linux-clang",
            qairt_root_dir=qairt_root_dir,
        )
