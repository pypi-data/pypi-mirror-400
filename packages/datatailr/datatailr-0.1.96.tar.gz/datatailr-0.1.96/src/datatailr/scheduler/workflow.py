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
Workflow
--------
```python
from datatailr import workflow, task
@task()
def get_number():
    return 42

@task()
def add(a, b):
    return a + b

@workflow("My Workflow")
def my_workflow():
    num = get_number()
    result = add(num, 8)

if __name__ == "__main__":
    my_workflow(local_run=True)
```


Running this script will execute the workflow localluy. To deploy it to the Datatailr platform,
simply remove the `local_run=True` argument.

Note that the workflow is executed as a directed acyclic graph (DAG), so tasks can run in parallel
when there are no dependencies.

Arguments to tasks can be a mix of literals and other task outputs, like in the example above.

The resulting DAG will look like this:

```mermaid
graph LR
    A[get_number] --> B[add]
    8((8)) --> B
```

More complex workflows can be built using simple function composition:

```python
@task()
def reduce_list(*numbers):
    print(f"Reducing list: {numbers}")
    return sum(numbers)

@workflow("Complex Workflow")
def complex_workflow():
    total_1 = add(get_number().alias('my number'), 13).alias('first addition')
    total_2 = reduce_list(*[get_number().alias(f"num_{i}") for i in range(5)])
    add(total_2, 1).alias('add one')
    add(total_2, 2).alias('add two')
    add(total_2, 3).alias('add three')
    add(total_2, 4).alias('add four')
    add(total_2, 5).alias('add five')
```
This will generate the following graph end deploy it for execition on the Datatailr platform:

```mermaid
graph LR
    A[my_number] --> B[first addition];
    13((13)) --> B;
    D[num_0] --> E[reduce_list];
    D1[num_1] --> E;
    D2[num_2] --> E;
    D3[num_3] --> E;
    D4[num_4] --> E;
    E --> G1[add one];
    E --> G2[add two];
    E --> G3[add three];
    E --> G4[add four];
    E --> G5[add five];
```
Note the use of the `alias()` method to give tasks specific names in the workflow graph.
This is necessary when the same task is invoked multiple times to avoid name collisions.

Controlling task properties can be done on one of two levels:
- Globally for the entire workflow via arguments to the `@workflow` decorator.
- Individually for each task via arguments to the `@task` decorator.

These resources include:
- Image
- Resources
- Run as user
- ACL
- Python version
- Python requirements
- Build scripts


In addition, some properties can be updated on a task call basis.
"""

import os
from typing import Callable, Optional, Dict, Union
import functools
from datatailr.logging import DatatailrLogger
from datatailr.scheduler import Batch, Schedule, Resources
from datatailr import Environment, Image, ACL, User

logger = DatatailrLogger(__name__).get_logger()


def workflow(
    name: Optional[str] = None,
    schedule: Optional[Schedule] = None,
    image: Optional[Image] = None,
    run_as: Optional[Union[str, User]] = None,
    resources: Resources = Resources(memory="100m", cpu=1),
    acl: Optional[ACL] = None,
    python_version: str = "auto",
    python_requirements: str = "",
    build_script_pre: str = "",
    build_script_post: str = "",
    env_vars: Dict[str, str | int | float | bool] = {},
):
    _name = name
    _schedule = schedule
    _image = image
    _run_as = run_as
    _resources = resources
    _acl = acl
    _python_version = python_version
    _python_requirements = python_requirements
    _build_script_pre = build_script_pre
    _build_script_post = build_script_post
    _env_vars = env_vars

    def decorator(func) -> Callable:
        @functools.wraps(func)
        def wrapper(
            *args,
            local_run: bool = False,
            schedule: Optional[Schedule] = None,
            image: Optional[Image] = None,
            run_as: Optional[Union[str, User]] = None,
            resources: Optional[Resources] = None,
            acl: Optional[ACL] = None,
            python_version: Optional[str] = None,
            python_requirements: Optional[str] = None,
            build_script_pre: Optional[str] = None,
            build_script_post: Optional[str] = None,
            env_vars: Optional[Dict[str, str | int | float | bool]] = None,
            **kwargs,
        ):
            workflow_file_path = func.__code__.co_filename
            # If the workflow is being invoked from a package installed in the container then raise a warning and return
            if (
                workflow_file_path.startswith(
                    "/opt/datatailr/usr/lib/python/site-packages/"
                )
                and os.getenv("DATATAILR_JOB_TYPE") == "batch"
            ) or os.getenv("DATATAILR_BATCH_DONT_RUN_WORKFLOW") == "true":
                return
            __schedule = schedule or _schedule
            __image = image or _image
            __run_as = run_as or _run_as
            __resources = resources or _resources
            __acl = acl or _acl
            __python_version = python_version or _python_version
            __python_requirements = python_requirements or _python_requirements
            __build_script_pre = build_script_pre or _build_script_pre
            __build_script_post = build_script_post or _build_script_post
            __env_vars = env_vars or _env_vars

            if local_run and (__schedule is not None):
                raise ValueError("Cannot set schedule for local run.")

            dag = Batch(
                name=_name or func.__name__.replace("_", " ").title(),
                environment=Environment.DEV,
                schedule=__schedule,
                image=__image,
                run_as=__run_as,
                resources=__resources,
                acl=__acl,
                local_run=local_run,
                python_version=__python_version,
                python_requirements=__python_requirements,
                build_script_pre=__build_script_pre,
                build_script_post=__build_script_post,
                env_vars=__env_vars,
            )
            dag.set_autorun(False)
            with dag:
                func(*args, **kwargs)

        return wrapper

    return decorator
