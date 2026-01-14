# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

import platform
from typing import Optional

from qairt.cli.qairt_vm.qairt_vm_context import (
    BaseQairtVmContext,
    LinuxX86QairtVmContext,
    WindowsArm64QairtVmContext,
    WindowsX86QairtVmContext,
)
from qairt.utils.os_utils import is_arm_64, is_linux, is_windows, is_x86_64


def get_platform_qairt_vm(qairt_root_dir: Optional[str] = None) -> BaseQairtVmContext:
    """Returns the Qairt VM context based on the current platform.

    This function determines the current platform and returns the corresponding
    Qairt VM context. The platform is determined by checking the operating system
    and architecture.

    Args:
        qairt_root_dir (str): The root directory of the Qairt installation. If not provided, it will use
        the default install location based on the platform.

    Returns:
        BaseQairtVmContext: The Qairt VM context for the current platform.
    """
    os_name = platform.system()
    arch_name = platform.processor()
    if is_windows(os_name) and is_x86_64(arch_name):
        return WindowsX86QairtVmContext(qairt_root_dir=qairt_root_dir)
    elif is_windows(os_name) and is_arm_64(arch_name):
        return WindowsArm64QairtVmContext(qairt_root_dir=qairt_root_dir)
    elif is_linux(os_name) and is_x86_64(arch_name):
        return LinuxX86QairtVmContext(qairt_root_dir=qairt_root_dir)
    else:
        raise RuntimeError(
            f"Unable to setup QAIRT DEV, OS and Architecture combo not supported. Got os_name:"
            f" {os_name}, arch_name: {arch_name}"
        )
