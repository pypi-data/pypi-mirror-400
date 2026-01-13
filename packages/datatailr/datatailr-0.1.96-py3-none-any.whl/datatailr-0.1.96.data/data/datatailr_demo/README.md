<div style="text-align: center;">
  <a href="https://www.datatailr.com/" target="_blank">
    <img src="https://s3.eu-west-1.amazonaws.com/datatailr.com/assets/datatailr-logo.svg" alt="Datatailr Logo" />
  </a>
</div>

---

**Datatailr empowers your team to streamline analytics and data workflows
from idea to production without infrastructure hurdles.**

# Getting Started
To get started with Datatailr you can initialize a new project using the Datatailr CLI:

```bash
datatailr init-demo
```
This will create a new demo project with some example code and open it in a new IDE window.

The project includes examples of creating and deploying data workflows, web applications, REST API services, and Excel add-ins.

## Deploying the Demo
To deploy any of the demos you can use the examples script located in the `datatailr_demo` folder.

For example, to deploy the data pipeline demo, you can run:

```bash
python -m examples data_pipeline
```

To deploy the web application demo, you can run:

```bash
python -m examples app
```

To deploy all the demos at once, you can run:

```bash
python -m examples all
```

## Workflows
The following example shows how to create a simple data pipeline using the Datatailr Python package.

In the data_pipeline module, we define a few tasks using the `@task()` decorator in the data_processing.py file.

```python
from datatailr import task

@task()
def get_data() -> dict:
    return {"a": 1, "b": 2, "c": 3}

@task()
def process_data(data: dict) -> dict:
    data["sum"] = sum(data.values())
    return data
```

Those are simple functions that represent steps in a data pipeline. They can be still used as regular functions, but when decorated with `@task()`, they can be orchestrated and executed as part of a workflow.

You can see an example of a workflow in the examples.py file:

```python
from datatailr import workflow
from data_pipelines.data_processing import func_no_args

@workflow(name="simple_data_pipeline_<>USERNAME<>")
def simple_workflow():
    func_no_args()
```

Now you can run this workflow locally by executing:
```python
>>> from datatailr_examples import simple_workflow
>>> simple_workflow(local_run=True)
```

This will execute the workflow in a local context, allowing you to test and debug your data pipeline before deploying it to a larger scale.

Running this code will create a graph of jobs and execute it.
Each node on the graph represents a job, which in turn is a call to a function decorated with `@task()`.

Since this is a local run then the execution of each node will happen sequentially in the same process.

To take advantage of the datatailr platform and execute the graph at scale, you can run it using the job scheduler as presented in the next section.

## Execution at Scale
To execute the graph at scale, you can use the Datatailr job scheduler. This allows you to run your jobs in parallel, taking advantage of the underlying infrastructure.

You will first need to separate your task definitions from the workflow definition. This means you should define your functions as a separate module, which can be imported into the module where the workflow is defined.


```python
# my_module.py

from datatailr import task

@task()
def func_no_args() -> str:
    return "no_args"

@task()
def func_with_args(a: int, b: float) -> str:
    return f"args: {a}, {b}"
```

To use these functions in a batch job, you just need to import them and run as part of a workflow:

```python
from my_module import func_no_args, func_with_args
from datatailr import workflow

@workflow(name="my_test_workflow_<>USERNAME<>")
def my_workflow():
    for n in range(2):
        res1 = func_no_args().alias(f"func_{n}")
        res2 = func_with_args(1, res1).alias(f"func_with_args_{n}")

schedule = Schedule(at_hours=0)
my_workflow(schedule=schedule)
```

This will submit the entire workflow for execution, and the scheduler will take care of running the jobs in parallel and managing the resources.
The workflow in the example above will be scheduled to run daily at 00:00.

___
Visit [our website](https://www.datatailr.com/) for more!
