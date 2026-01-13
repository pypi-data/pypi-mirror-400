# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

from typing import Dict, List, Optional, Union, Callable
from datatailr.build import Image
from datatailr import ACL, Environment, User
from datatailr.scheduler.base import Job, JobType, EntryPoint, Resources


class App(Job):
    """
    App
    ---
    Represents a web application or a dashboard deployment on Datatailr.
    """

    def __init__(
        self,
        name: str,
        entrypoint: Callable,
        environment: Optional[Environment] = Environment.DEV,
        image: Optional[Image] = None,
        run_as: Optional[Union[str, User]] = None,
        resources: Resources = Resources(),
        acl: Optional[ACL] = None,
        python_version: str = "3.12",
        python_requirements: str | List[str] = "",
        build_script_pre: str = "",
        build_script_post: str = "",
        env_vars: Dict[str, str | int | float | bool] = {},
        update_existing: bool = False,
    ):
        entrypoint = EntryPoint(JobType.APP, entrypoint)
        super().__init__(
            name=name,
            type=JobType.APP,
            entrypoint=entrypoint,
            environment=environment,
            image=image,
            run_as=run_as,
            resources=resources,
            acl=acl,
            python_version=python_version,
            python_requirements=python_requirements,
            build_script_pre=build_script_pre,
            build_script_post=build_script_post,
            env_vars=env_vars,
            update_existing=update_existing,
        )


class Service(Job):
    def __init__(
        self,
        name: str,
        entrypoint: Callable,
        environment: Optional[Environment] = Environment.DEV,
        image: Optional[Image] = None,
        run_as: Optional[Union[str, User]] = None,
        resources: Resources = Resources(),
        acl: Optional[ACL] = None,
        python_version: str = "3.12",
        python_requirements: str | List[str] = "",
        build_script_pre: str = "",
        build_script_post: str = "",
        env_vars: Dict[str, str | int | float | bool] = {},
        update_existing: bool = False,
    ):
        entrypoint = EntryPoint(JobType.SERVICE, entrypoint)
        super().__init__(
            name=name,
            type=JobType.SERVICE,
            entrypoint=entrypoint,
            environment=environment,
            image=image,
            run_as=run_as,
            resources=resources,
            acl=acl,
            python_version=python_version,
            python_requirements=python_requirements,
            build_script_pre=build_script_pre,
            build_script_post=build_script_post,
            env_vars=env_vars,
            update_existing=update_existing,
        )


class ExcelAddin(Job):
    def __init__(
        self,
        name: str,
        entrypoint: Callable,
        environment: Optional[Environment] = Environment.DEV,
        image: Optional[Image] = None,
        run_as: Optional[Union[str, User]] = None,
        resources: Resources = Resources(),
        acl: Optional[ACL] = None,
        python_version: str = "3.12",
        python_requirements: str | List[str] = "",
        build_script_pre: str = "",
        build_script_post: str = "",
        env_vars: Dict[str, str | int | float | bool] = {},
        update_existing: bool = False,
    ):
        entrypoint = EntryPoint(JobType.EXCEL, entrypoint)
        super().__init__(
            name=name,
            type=JobType.EXCEL,
            entrypoint=entrypoint,
            environment=environment,
            image=image,
            run_as=run_as,
            resources=resources,
            acl=acl,
            python_version=python_version,
            python_requirements=python_requirements,
            build_script_pre=build_script_pre,
            build_script_post=build_script_post,
            env_vars=env_vars,
            update_existing=update_existing,
        )
