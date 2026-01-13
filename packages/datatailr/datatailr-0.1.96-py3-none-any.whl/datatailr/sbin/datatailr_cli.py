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

from __future__ import annotations

import sys
import shutil
import os
from pathlib import Path
import subprocess
import argparse
import importlib.resources as ir
from datatailr.logging import CYAN, RED, YELLOW, GREEN
from datatailr import User, is_dt_installed

DEFAULT_TARGET = "datatailr_demo_project"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="datatailr",
        description="Datatailr command line utilities. Use subcommands to access features.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # init-demo subcommand
    p_init = sub.add_parser(
        "init-demo",
        help="Copy the bundled demo project into a target directory.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p_init.add_argument(
        "-d",
        "--destination",
        metavar="PATH",
        default=str(Path.cwd() / DEFAULT_TARGET),
        help="Destination directory to create (will be created if missing).",
    )
    p_init.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing files (by default existing files are skipped).",
    )

    # version subcommand
    sub.add_parser("version", help="Show python and datatailr versions.")

    return parser


def copy_tree(src: Path, dst: Path, username: str, overwrite: bool = False) -> None:
    file_types = (
        ".py",
        ".yaml",
        ".yml",
        ".md",
        ".txt",
        ".csv",
        ".json",
        ".png",
        ".jpg",
        ".jpeg",
        ".ico",
    )
    for root, dirs, files in os.walk(src):
        rel = Path(root).relative_to(src)
        target_root = dst / rel
        target_root.mkdir(parents=True, exist_ok=True)
        for d in dirs:
            (target_root / d).mkdir(exist_ok=True)
        for f in files:
            if not f.lower().endswith(file_types):
                continue  # skip non-relevant files
            src_file = Path(root) / f
            dst_file = target_root / f
            if dst_file.exists() and not overwrite:
                continue  # skip existing unless force enabled
            # replace <>USERNAME<> placeholders in the files:

            with open(src_file, "r") as sf, open(dst_file, "w") as df:
                content = sf.read()
                content = content.replace("<>USERNAME<>", username)
                df.write(content)


def git_init_repo(path: Path) -> None:
    """Initialize a git repository at the given path if not already a git repo."""
    if (path / ".git").exists():
        return  # already a git repo

    if not shutil.which("git"):
        print(
            YELLOW(
                "Git is not installed or not found in PATH; skipping git initialization."
            )
        )
        return

    for command in [
        ["git", "init"],
        ["git", "add", "."],
        ["git", "commit", "-m", "Initial commit"],
    ]:
        subprocess.run(
            command,
            cwd=str(path),
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def install_code_extensions() -> None:
    """Install recommended code-server extensions for Datatailr."""
    if not shutil.which("code-server"):
        print(
            YELLOW(
                "Code server is not installed or not found in PATH; skipping extension installation."
            )
        )
        return
    extensions = ["ms-python.python", "ms-python.debugpy", "astral-sh.ty"]
    print(CYAN("Installing recommended code-server extensions..."))
    for ext in extensions:
        subprocess.run(["code-server", "--install-extension", ext], check=True)
    print(GREEN("Extensions installed."))


def open_folder(path: Path) -> None:
    """Launch code server in the target path."""
    if not shutil.which("code-server"):
        print(
            YELLOW(
                "Code server is not installed or not found in PATH; skipping code server launch."
            )
        )
        return
    subprocess.run(["code-server", str(path)], check=True)


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init-demo":
        try:
            template_root = ir.files("datatailr_demo")
        except Exception as e:  # pragma: no cover
            print(RED(f"Could not access demo template package: {e}"))
            return 1
        src_path = Path(str(template_root))

        target = Path(args.destination)
        if target.exists() and any(target.iterdir()) and not args.force:
            print(
                YELLOW(
                    f"Target '{target}' already exists and is not empty\nUse --force to overwrite or choose a different path."
                )
            )
            return 0
        print(CYAN(f"Copying Datatailr demo template to: {target}"))
        if is_dt_installed():
            username = User.signed_user().name
        else:
            username = os.getlogin()
            print(
                YELLOW(f"The dt CLI is not installed. Using OS login name: {username}.")
            )
        copy_tree(src_path, target, username, overwrite=args.force)
        git_init_repo(target)
        print(GREEN("Done. Explore the README.md inside the demo project."))
        open_folder(target)
        install_code_extensions()
        return 0

    elif args.command == "version":
        # Lazy import to avoid unnecessary startup cost
        import importlib.metadata as im

        pkg_version = (
            im.version("datatailr")
            if "datatailr" in {d.metadata["Name"] for d in im.distributions()}
            else "unknown"
        )
        # print nicely colored version info
        print(GREEN(f"Datatailr {pkg_version}"))
        print(CYAN(f"Python {sys.version.split()[0]}"))
        return 0

    # No subcommand: show help and exit
    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
