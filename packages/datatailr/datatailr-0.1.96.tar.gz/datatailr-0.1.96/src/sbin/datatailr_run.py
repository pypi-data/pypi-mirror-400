#!/usr/bin/env python3

# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************


# The purpose of this script is to be the entrypoint for all jobs running on datatailr.
# The main functions of the script are:
#     1. Create a linux user and group for the job.
#     2. Set the environment variables for the job.
#     3. Run the job in a separate process, as the newly created user and pass all relevant environment variables.
# There are muliple environment variables which are required for the job to run.
# Some of them are necessary for the setup stage, which is executed directly in this script as the linux root user.
# Others are passed to the job script, which is executed in a separate process with only the users' privileges and not as a root user.
#
# Setup environment variables:
#     DATATAILR_USER - the user under which the job will run.
#     DATATAILR_GROUP - the group under which the job will run.
#     DATATAILR_UID - the user ID of the user as it is defined in the system.
#     DATATAILR_GID - the group ID of the group as it is defined in the system.
#     DATATAILR_JOB_TYPE - the type of job to run. (batch\service\app\excel\IDE)
# Job environment variables (not all are always relevant, depending on the job type):
#     DATATAILR_BATCH_RUN_ID - the unique identifier for the batch run.
#     DATATAILR_BATCH_ID - the unique identifier for the batch.
#     DATATAILR_JOB_ID - the unique identifier for the job.


import concurrent.futures
import subprocess
import os
import signal
import sys
import shlex
import shutil
import sysconfig
from typing import Optional, Tuple
from datatailr.utils import ENV_VARS_PREFIX
from datatailr.utils import is_dt_installed
from datatailr.logging import DatatailrLogger
from datatailr import User
from pathlib import Path
import importlib.resources as ir


logger = DatatailrLogger(__name__).get_logger()

if not is_dt_installed():
    print("Datatailr is not installed.")
    sys.exit(1)


def get_env_var(name: str, default: str | None = None) -> str:
    """
    Get an environment variable.
    If the variable is not set, raise an error.
    """
    if name not in os.environ:
        if default is not None:
            return default
        print(f"Environment variable '{name}' is not set.")
        raise ValueError(f"Environment variable '{name}' is not set.")
    return os.environ[name]


def get_python_scripts_location() -> str:
    """
    Get the location of the python scripts.
    """
    scripts_path_file_name = "/opt/datatailr/etc/python-scripts-location"
    if os.path.exists(scripts_path_file_name):
        with open(scripts_path_file_name, "r") as f:
            scripts_path = f.read().strip()
            return scripts_path
    return ""


def create_dirs_for_user(directories: list[str], user: str, group: str):
    if get_env_var("DATATAILR_JOB_TYPE") != "workspace":
        home_dir = f"/home/{user}"
        os.makedirs(home_dir, exist_ok=True)
        shutil.chown(home_dir, user, group)
        os.chmod(home_dir, 0o773)  # rwxrwxr-x

    for directory in directories:
        dir_name = f"/home/{user}/{directory}"
        if os.path.exists(dir_name):
            continue
        os.makedirs(dir_name, exist_ok=True)
        shutil.chown(dir_name, user, group)
        os.chmod(dir_name, 0o773)  # rwxrwxr-x


def get_user_and_group() -> Tuple[str, str]:
    """
    Returns the user and group from environment variables.
    """
    user = get_env_var("DATATAILR_USER")
    group = get_env_var("DATATAILR_GROUP")

    # required for local tmp files, which can be used for local blob-storage
    create_dirs_for_user([".tmp", ".tmp/.dt"], user, group)
    return user, group


def copy_dotfiles(user: str, group: str):
    create_dirs_for_user(
        [".cache", ".config", ".config/code-server", ".local", ".vscode"], user, group
    )
    home_dir = f"/home/{user}"
    skel_dir = "/etc/skel"
    # Copy dotfiles from /etc/skel to the new user's home directory if they do not already exist
    for root, dirs, files in os.walk(skel_dir):
        rel_path = os.path.relpath(root, skel_dir)
        target_root = os.path.join(home_dir, rel_path) if rel_path != "." else home_dir

        for d in dirs:
            target_dir = os.path.join(target_root, d)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
                shutil.chown(target_dir, user, group)
                os.chmod(target_dir, 0o773)  # rwxrwxr-x

        for f in files:
            src_file = os.path.join(root, f)
            target_file = os.path.join(target_root, f)
            if not os.path.exists(target_file):
                shutil.copy(src_file, target_file)
                shutil.chown(target_file, user, group)
                os.chmod(target_file, 0o773)  # rwxrwxr-x


def create_git_config(user: str):
    dt_user = User(user)
    git_user_email = subprocess.run(
        ["sudo", "-u", user, "git", "config", "--global", "user.email"],
        capture_output=True,
        text=True,
    ).stdout.strip()

    if git_user_email not in ["None", ""]:
        return

    for key, value in [
        ("user.name", f"{dt_user.first_name} {dt_user.last_name}"),
        ("user.email", f"{dt_user.email}"),
        ("init.defaultBranch", "main"),
    ]:
        subprocess.run(["sudo", "-u", user, "git", "config", "--global", key, value])
    print(f"Git global config created for user {user}.")


def link_script_files():
    scripts_location = get_python_scripts_location()
    if not scripts_location or scripts_location == "":
        return
    user_bin_dir = "/usr/bin"
    script_files = ["datatailr"]
    for script_file in script_files:
        src_path = os.path.join(scripts_location, script_file)
        if not os.path.exists(src_path):
            print(f"Script {script_file} not found in {scripts_location}.")
            continue
        dest_path = os.path.join(user_bin_dir, script_file)
        if not os.path.exists(dest_path):
            os.symlink(src_path, dest_path)
            print(f"Linked script {script_file} to {dest_path}")


def copy_welcome_readme(user: str):
    demo_package_root = Path(str(ir.files("datatailr_demo")))
    readme_src = demo_package_root / "README.md"
    if not readme_src.exists():
        print(f"Demo README.md not found in datatailr_demo package at: {readme_src}")
        return
    readme_dest = f"/home/{user}/README.md"
    if not os.path.exists(readme_dest):
        shutil.copy(readme_src, readme_dest)
        os.chown(readme_dest, 0, 0)
        os.chmod(readme_dest, 0o644)  # rw-r--r--


def prepare_command_argv(command: str | list, user: str, env_vars: dict) -> list[str]:
    if isinstance(command, str):
        command = shlex.split(command)

    python_libdir = sysconfig.get_config_var("LIBDIR")
    ld_library_path = get_env_var("LD_LIBRARY_PATH", None)

    # Base environment variables setup
    base_env = {
        "PATH": get_env_var("PATH", ""),
        "PYTHONPATH": get_env_var("PYTHONPATH", ""),
        "LD_LIBRARY_PATH": ":".join(filter(None, [python_libdir, ld_library_path])),
        # Ensure Python child processes flush prints immediately
        "PYTHONUNBUFFERED": "1",
        # Consistent encoding for stdout/stderr streams
        "PYTHONIOENCODING": "UTF-8",
    }

    merged_env = base_env | env_vars
    env_kv = [f"{k}={v}" for k, v in merged_env.items()]
    return ["sudo", "-u", user, "env", *env_kv, *command]


def run_single_command_non_blocking(
    command: str | list,
    user: str,
    env_vars: dict,
    log_stream_name: Optional[str | None] = None,
) -> int:
    """
    Runs a single command non-blocking and returns the exit code after it finishes.
    This is designed to be run within an Executor.
    """
    argv = prepare_command_argv(command, user, env_vars)
    cmd_label = " ".join(argv[4:])  # For logging purposes

    try:
        if log_stream_name:
            stdout_file_path = f"/opt/datatailr/var/log/{log_stream_name}.log"
            stderr_file_path = f"/opt/datatailr/var/log/{log_stream_name}_error.log"
            with (
                open(stdout_file_path, "ab", buffering=0) as stdout_file,
                open(stderr_file_path, "ab", buffering=0) as stderr_file,
            ):
                proc = subprocess.Popen(argv, stdout=stdout_file, stderr=stderr_file)
        else:
            proc = subprocess.Popen(argv)
        returncode = proc.wait()

        if returncode < 0:
            sig = -returncode
            if sig == signal.SIGKILL:
                logger.error(f"{command} killed by SIGKILL (possible OOM).")
                try:
                    with open("/sys/fs/cgroup/memory.events") as f:
                        events = dict(
                            line.strip().split() for line in f if line.strip()
                        )
                    logger.error(f"cgroup events: {events}")
                except Exception:
                    pass
            elif sig == signal.SIGSEGV:
                logger.error(f"{command} terminated by SIGSEGV (segmentation fault).")
            else:
                sig_name = (
                    signal.Signals(sig).name
                    if sig in signal.Signals.__members__.values()
                    else f"SIG{sig}"
                )
                logger.error(f"{command} terminated by signal {sig} ({sig_name}).")
        elif returncode >= 128:
            sig = returncode - 128
            if sig == signal.SIGKILL:
                logger.error(f"{command} exit={returncode} (SIGKILL, possible OOM).")
            else:
                logger.error(f"{command} exit={returncode} (signal {sig}).")
        elif returncode != 0:
            logger.error(f"{command} failed with exit code {returncode}.")

        if proc.stderr:
            logger.error(f"stderr:\n{proc.stderr}")
        return returncode
    except Exception as e:
        logger.error(f"Execution error for '{cmd_label}': {e}")
        return 1


def run_commands_in_parallel(
    commands: list[str | list],
    user: str,
    env_vars: dict,
    log_stream_names: Optional[list[str | None]] = None,
) -> int:
    """
    Executes two commands concurrently using a ThreadPoolExecutor.
    Returns a tuple of (return_code_cmd1, return_code_cmd2).
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(commands)) as executor:
        futures = []
        for command, log_stream_name in zip(
            commands, log_stream_names or [None] * len(commands)
        ):
            futures.append(
                executor.submit(
                    run_single_command_non_blocking,
                    command,
                    user,
                    env_vars,
                    log_stream_name,
                )
            )
        results = [
            future.result() for future in concurrent.futures.as_completed(futures)
        ]
        return 0 if all(code == 0 for code in results) else 1


def main():
    user, group = get_user_and_group()
    job_type = get_env_var("DATATAILR_JOB_TYPE")

    env = {
        "DATATAILR_JOB_TYPE": job_type,
        "DATATAILR_JOB_NAME": get_env_var("DATATAILR_JOB_NAME"),
        "DATATAILR_JOB_ID": get_env_var("DATATAILR_JOB_ID"),
    }
    user_env_vars = {
        key.replace(ENV_VARS_PREFIX, ""): value
        for key, value in os.environ.items()
        if key.startswith(ENV_VARS_PREFIX)
    }
    env = user_env_vars | env

    if job_type == "batch":
        run_id = get_env_var("DATATAILR_BATCH_RUN_ID")
        batch_id = get_env_var("DATATAILR_BATCH_ID")
        entrypoint = get_env_var("DATATAILR_BATCH_ENTRYPOINT")
        batch_args = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("DATATAILR_BATCH_ARG_")
        }
        env = (
            {
                "DATATAILR_BATCH_RUN_ID": run_id,
                "DATATAILR_BATCH_ID": batch_id,
                "DATATAILR_BATCH_ENTRYPOINT": entrypoint,
            }
            | env
            | batch_args
        )
        return run_single_command_non_blocking("datatailr_run_batch", user, env)
    elif job_type == "service":
        port = get_env_var("DATATAILR_SERVICE_PORT", "8080")
        entrypoint = get_env_var("DATATAILR_ENTRYPOINT")
        env = {
            "DATATAILR_ENTRYPOINT": entrypoint,
            "DATATAILR_SERVICE_PORT": port,
        } | env
        return run_single_command_non_blocking("datatailr_run_service", user, env)
    elif job_type == "app":
        entrypoint = get_env_var("DATATAILR_ENTRYPOINT")
        env = {
            "DATATAILR_ENTRYPOINT": entrypoint,
        } | env
        return run_single_command_non_blocking("datatailr_run_app", user, env)
    elif job_type == "excel":
        host = get_env_var("EXCEL_HOST", "")
        entrypoint = get_env_var("DATATAILR_ENTRYPOINT")
        local = get_env_var("DATATAILR_LOCAL", "0")
        dt_environment = get_env_var("DATATAILR_JOB_ENVIRONMENT")
        env = {
            "DATATAILR_ENTRYPOINT": entrypoint,
            "EXCEL_HOST": host,
            "DATATAILR_LOCAL": local,
            "DATATAILR_JOB_ENVIRONMENT": dt_environment,
        } | env
        return run_single_command_non_blocking("datatailr_run_excel", user, env)

    elif job_type == "workspace":
        os.makedirs("/opt/datatailr/var/log", exist_ok=True)
        copy_dotfiles(user, group)
        create_git_config(user)
        copy_welcome_readme(user)
        ide_command = [
            "code-server",
            "--disable-telemetry",
            "--disable-update-check",
            "--auth=none",
            "--bind-addr=127.0.0.1:9090",
            f'--app-name="Datatailr IDE {get_env_var("DATATAILR_USER")}"',
            f"--user-data-dir=/home/{user}/.vscode",
            f"/home/{user}",
        ]
        job_name = get_env_var("DATATAILR_JOB_NAME")
        jupyter_command = [
            "jupyter-lab",
            "--ip='127.0.0.1'",
            "--port=7070",
            "--no-browser",
            "--NotebookApp.token=''",
            "--NotebookApp.password=''",
            f"--ServerApp.base_url=/workspace/dev/{job_name}/jupyter/",
            f"--ServerApp.file_url_prefix=/workspace/dev/{job_name}/jupyter/static/",
            f"--ServerApp.root_dir=/home/{user}",
        ]
        return run_commands_in_parallel(
            [ide_command, jupyter_command], user, env, ["code-server", "jupyter"]
        )

    else:
        raise ValueError(f"Unknown job type: {job_type}")


if __name__ == "__main__":
    try:
        print("Starting job execution...")
        returncode = main()
        print(f"Job executed successfully, with code {returncode}")
        raise SystemExit(returncode)
    except Exception as e:
        print(f"Error during job execution: {e}")
        raise SystemExit(1)
