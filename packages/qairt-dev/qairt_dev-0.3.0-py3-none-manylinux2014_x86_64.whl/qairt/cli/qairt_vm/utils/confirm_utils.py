# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

import click


def confirm(
    accept_all: bool,
    *args,
    **kwargs,
) -> bool:
    """
    Wrapper around click.confirm that supports a global accept-all flag.

    Args:
        accept_all (bool): If True, auto-accept the confirmation without prompting.
        *args: Positional args to pass to click.confirm (e.g., text).
        **kwargs: Keyword args to pass to click.confirm (e.g., default, abort, err).

    Returns:
        bool: True if accepted, False otherwise.
    """
    if accept_all:
        return True
    return click.confirm(*args, **kwargs)
