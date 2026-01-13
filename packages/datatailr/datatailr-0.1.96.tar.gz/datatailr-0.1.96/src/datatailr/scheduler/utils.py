# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

import os
import re
import unicodedata

from datatailr.scheduler.constants import BATCH_JOB_ARGUMENTS
from datatailr.errors import BatchJobError
from datatailr.tag import get_tag
from datatailr.utils import run_shell_command


def get_available_env_args():
    """
    Get the available environment variables for batch job arguments.

    This function retrieves the environment variables that match the keys defined in DATATAILR_BATCH_JOB_ARGUMENTS.

    Returns:
        dict: A dictionary of available environment variables for batch jobs.
    """
    available_args = {}
    for key, value in os.environ.items():
        arg_key = key.replace("DATATAILR_BATCH_ARG_", "").lower()
        if arg_key in BATCH_JOB_ARGUMENTS:
            available_args[arg_key] = value
    return available_args


def normalize_name(name: str) -> str:
    """
    Normalize a name by converting it to lowercase, removing non unicode characters, and replacing spaces with underscores.

    Args:
        name (str): The name to normalize.

    Returns:
        str: The normalized name.
    """
    name = unicodedata.normalize("NFKC", name).lower()
    return re.sub(r"[^0-9a-z]+", "-", name).strip("-")


def get_base_url() -> str:
    """
    Get the job scheduler URL from environment variables.
    Returns:
        str: The job scheduler URL or an empty string if not set.
    """
    hostname = get_tag("public_hostname", cached=True)
    domain = get_tag("public_domain", cached=True)
    if hostname and domain:
        return f"https://{hostname}.{domain}"
    return ""


class RepoValidationError(BatchJobError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def get_path_to_module(func) -> str:
    """
    Get the file system path to the module where the function is defined.

    Args:
        func (function): The function whose module path is to be retrieved.

    Returns:
        str: The file system path to the module.
    """
    import importlib.util

    module_name = func.__module__
    try:
        module_spec = importlib.util.find_spec(module_name)
    except ValueError:
        module_spec = None
    if module_spec:
        # Resolve the filesystem directory of the top package for module_name
        if module_spec.submodule_search_locations:
            # It's a package; get its directory
            package_root = os.path.abspath(
                next(iter(module_spec.submodule_search_locations))
            )
        elif module_spec.origin:
            # It's a module; use its containing directory
            package_root = os.path.abspath(os.path.dirname(module_spec.origin))
        else:
            raise RepoValidationError(f"Cannot resolve path for {module_name}")
    else:
        file_path = os.path.abspath(func.__code__.co_filename)
        package_root = os.path.dirname(file_path)
    return package_root


def get_path_to_repo(path_to_module) -> str:
    """
    Get the path to the git repository root for the module where the function is defined.

    Args:
        func (function): The function whose repository path is to be retrieved.

    Returns:
        str: The file system path to the git repository root.
    """
    try:
        path_to_repo = run_shell_command(
            f"cd {path_to_module} && git rev-parse --show-toplevel"
        )[0]
    except RuntimeError:
        # simply return the parent directory if not a git repo
        path_to_repo = os.path.abspath(os.path.join(path_to_module, ".."))
    return path_to_repo
