# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

import os

from qti.aisw.tools.core.utilities.qairt_logging import LogAreas, QAIRTLogger

qairt_vm_log_area = LogAreas.register_log_area("QAIRT-VM")
qairt_vm_log_level = os.getenv("QAIRT_VM_LOG_LEVEL", "INFO")
qairt_vm_logger = QAIRTLogger.register_area_logger(
    qairt_vm_log_area, level=qairt_vm_log_level, formatter_val="extended", handler_list=["dev_console"]
)
