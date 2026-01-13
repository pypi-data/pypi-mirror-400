"""
Copyright (c) 2025 - Datatailr Inc.
All Rights Reserved.

This file is part of Datatailr and subject to the terms and conditions
defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
of this file, in parts or full, via any medium is strictly prohibited.
"""

import os
import sys
import importlib
import subprocess
import inspect
from urllib.parse import urlparse

import numpy as np

try:
    from dt.excel_base import Addin as AddinBase, Queue  # type: ignore
except ImportError as e:
    from datatailr.excel.stubs import AddinBase, Queue


def __progress__(queue, stop):
    from time import sleep

    bar = ["█", "██", "███", "████", "█████", "██████", "███████"]

    count = 0
    while True:
        if stop.is_set():
            return
        queue.push(bar[count % len(bar)])
        count += 1
        sleep(0.25)


def get_package_root(mod):
    # Given module, e.g., dt.excel located at /opt/datatailr/python/dt/excel.py
    # return entry for sys.path so it could be imported as a module.
    # For the module above: /opt/datatailr/python
    mod_path = os.path.abspath(mod.__file__)
    mod_parts = mod.__name__.split(".")
    for _ in range(len(mod_parts)):
        mod_path = os.path.dirname(mod_path)
    return mod_path


def matches_annotation(value, annotation):
    if isinstance(value, np.ndarray):
        return True
    if annotation is bool:
        return isinstance(value, bool) or (type(value) is int and value in (0, 1))
    if annotation is float:
        return isinstance(value, float) or (type(value) is int)
    return isinstance(value, annotation)


def extract_hostname(url: str) -> str | None:
    url = url if url else ""
    if "://" not in url:
        url = "//" + url
    return urlparse(url).hostname


class Addin(AddinBase):  # type: ignore
    def __init__(self, *args, **kwargs):
        super(Addin, self).__init__(*args, **kwargs)
        f = inspect.currentframe().f_back  # type: ignore
        mod = inspect.getmodule(f)
        if mod is not None:
            setattr(mod, "__dt_addin__", self)

    def run(self, port, ws_port, ide=True):
        # Excel addin executable will try to import an object literally called "addin"
        # from a module passed to dt-excel.sh as an argument. So to find which module
        # to pass to dt-excel.sh, we walk the callstack until a module with "addin"
        # object of type Addin is found. If not -- inform user about this requirement.
        found_module = None
        for frame_info in inspect.stack():
            mod = inspect.getmodule(frame_info.frame)
            if not mod or not hasattr(mod, "__name__"):
                continue

            temp_path = get_package_root(mod)
            sys.path.insert(0, temp_path)
            try:
                imported_mod = importlib.import_module(mod.__name__)
            finally:
                sys.path.pop(0)

            addin_obj = getattr(imported_mod, "__dt_addin__", None)
            if addin_obj is self or id(addin_obj) == id(self):
                found_module = mod
                break

        if not found_module:
            raise ValueError("'__dt_addin__' not found.")

        if found_module.__name__ != "__main__":
            # addin.run was called from the initial python script (where __name__ == "__main__")
            module_name = found_module.__name__
            if found_module.__file__ is None:
                raise ValueError(f"Module {found_module.__name__} has no __file__")
            dir_name = os.path.dirname(os.path.abspath(found_module.__file__))
        else:
            # initial python script did not call addin.run() itself (e.g. it imported function that called addin.run)
            filename = inspect.getsourcefile(found_module)
            if filename is None:
                raise ValueError(f"Cannot determine filename for module {found_module}")
            module_name = os.path.splitext(os.path.basename(filename))[0]
            dir_name = os.path.dirname(os.path.abspath(filename))

        ide_flag = "-i" if ide else ""
        hostname = extract_hostname(
            os.environ.get("VSCODE_PROXY_URI")
        )  # ty:ignore[invalid-argument-type]

        subprocess.run(
            [
                "bash",
                "-c",
                f'PYTHONPATH="{dir_name}:$PYTHONPATH" /opt/datatailr/bin/dt-excel.sh {ide_flag} -n -H {hostname} -p {port} -w {ws_port} {module_name}',
            ]
        )

    def expose(
        self, description, help, volatile=False, streaming=False, progressbar=False
    ):
        if streaming and progressbar:
            raise ValueError(
                "you cannot specify progressbar and streaming at the same time"
            )

        def decorator(func):
            signature = inspect.signature(func)

            def wrapper(*args, **kwargs):
                # TODO: check whether it's possible to use a kwarg instead so that a decorated function can
                # be called directly from python code without requiring positional argument for _id
                _id = args[0]

                bound = signature.bind_partial(**kwargs)
                bound.apply_defaults()
                for arg in signature.parameters.values():
                    if streaming and arg.name == "queue":
                        continue

                    if not matches_annotation(
                        bound.arguments[arg.name], arg.annotation
                    ):
                        raise ValueError(
                            "excel/python/dt/excel.py: Got argument of wrong type, expected %s or numpy.ndarray, got %s"
                            % (arg.annotation, type(bound.arguments[arg.name]))
                        )
                queue = Queue(self.name.lower() + "." + func.__name__, _id)
                if not streaming:
                    if not progressbar:
                        result = func(**kwargs)
                        if hasattr(result, "tolist"):
                            result = result.tolist()
                        return result

                    from threading import Event, Thread

                    error = None

                    stop = Event()
                    thread = Thread(target=__progress__, args=(queue, stop))
                    thread.start()
                    try:
                        result = func(**kwargs)
                    except Exception as exception:
                        error = str(exception)

                    stop.set()
                    thread.join()

                    if error is not None:
                        queue.error(error)
                    else:
                        queue.push(result)
                    return
                try:
                    func(queue, **kwargs)
                except Exception as exception:
                    queue.error(str(exception))

            self.decorator_impl(
                signature,
                wrapper,
                func.__name__,
                description,
                help,
                volatile,
                streaming or progressbar,
            )
            return wrapper

        return decorator
