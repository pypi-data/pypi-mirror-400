# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

"""
Datatailr - Python SDK
======================

The **datatailr** package provides a Python SDK for interacting with the Datatailr platform.

For a quickstart guide please launch the default workspace
on your installation and open the README file.

Datatailr provides a simple interface for scheduling and managing data tasks,
handling user access control, working with data blobs and secrets, and more.

"""

from datatailr.wrapper import dt__System, mock_cli_tool
from datatailr.group import Group
from datatailr.user import User
from datatailr.acl import ACL
from datatailr.acl import Permission
from datatailr.blob import Blob
from datatailr.build import Image
from datatailr.utils import Environment, is_dt_installed
from datatailr.version import __version__
from datatailr.scheduler import (
    App,
    Service,
    ExcelAddin,
    Resources,
    workflow,  # :no-index:
    task,
    set_allow_unsafe_scheduling,
)

system = dt__System()
if isinstance(system, mock_cli_tool):
    __provider__ = "not installed"
else:
    __provider__ = system.provider()

__all__ = [
    "ACL",
    "Permission",
    "Blob",
    "Environment",
    "Group",
    "Image",
    "User",
    "__version__",
    "__provider__",
    "is_dt_installed",
    "App",
    "Service",
    "ExcelAddin",
    "Resources",
    "workflow",
    "task",
    "set_allow_unsafe_scheduling",
]
