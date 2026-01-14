# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================

"""Post install helper module to manage QAIRT SDK installation and OS level dependency installation"""

import argparse
import os
import sys

from qairt.cli.qairt_vm.qairt_vm_context import qairt_vm_logger
from qairt.cli.qairt_vm.qairt_vm_factory import get_platform_qairt_vm


def parse_args():
    """
    QAIRT VM command line arguments parser method

    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    program_name = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(
        prog=program_name,
        description="\nQAIRT Version Manager (QAIRT-VM) is a post install and setup tool for QAIRT DEV "
        "package \n\n"
        "QAIRT-VM inspection functionality is run by default when running tools and APIs from "
        "QAIRT DEV",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--inspect",
        action="store_true",
        help="Verifies if QAIRT SDK and all OS and python dependencies for qairt-dev is met",
    )
    parser.add_argument(
        "-f",
        "--fix",
        action="store_true",
        help="Attempts to fetch expected QAIRT SDK and fix OS and python dependency "
        "requirements for qairt-dev",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        default=False,
        help="Run fix non-interactively and answer 'yes' to all prompts automatically (installs SDK, "
        "OS and Python deps, including optional)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="Prints detailed output and stack trace"
    )

    subparsers = parser.add_subparsers(dest="subcommands", title="subcommands")

    fetch_parser = subparsers.add_parser(
        "fetch",
        help="Downloads and extracts a specified version of QAIRT SDK",
        description="Fetch downloads and extracts the specified version of QAIRT SDK. ",
    )
    fetch_parser.add_argument("-l", "--list", action="store_true", help="List available QAIRT SDK versions")
    fetch_parser.add_argument(
        "-v",
        "--version",
        metavar="VERSION",
        help="QAIRT SDK version to download and extract.\n "
        "Version can be provided as semantic version string (e.g '2.38.0') or use 'latest'/'default'",
    )
    fetch_parser.add_argument(
        "-d", "--dir", metavar="PATH", help="Destination directory for downloading and extract QAIRT SDK"
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    # If user already has a QAIRT_SDK_ROOT set, use that
    # Otherwise, use the default SDK root location at install location
    qairt_root_dir = os.environ.get("QAIRT_SDK_ROOT", None)
    qairt_vm = get_platform_qairt_vm(qairt_root_dir=qairt_root_dir)

    try:
        if args.inspect:
            qairt_vm_logger.info("Running QAIRT environment inspection...")
            qairt_vm.inspect(args.verbose)
        elif args.fix:
            qairt_vm_logger.info("Running QAIRT environment fix... ")
            qairt_vm.fix(args.verbose, accept_all=args.yes)
        elif args.subcommands == "fetch":
            if args.list:
                qairt_vm.list_sdks()
            elif args.version:
                qairt_vm.fetch_sdk(args.version, args.dir)
            else:
                raise RuntimeError("Must Pass either -v/--version or --list")
        else:
            raise RuntimeError("Must Pass either -i/--inspect or -f/--fix")
    except BaseException as e:
        if args.verbose:
            raise e
        qairt_vm_logger.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
