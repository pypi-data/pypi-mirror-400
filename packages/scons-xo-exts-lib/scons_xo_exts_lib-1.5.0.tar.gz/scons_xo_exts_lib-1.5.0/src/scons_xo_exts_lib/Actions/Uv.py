#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os

from SCons.Script import Environment

from ..GenericExtensions import execute_command


def uv_venv_action(target, source, env):
    if os.path.exists(".venv"):
        return
    else:
        execute_command(env, "${UV_EXE} venv")


def uv_sync_action(target, source, env):
    execute_command(env, "${UV_EXE} sync --all-packages")


def uv_pip(env, cmd):
    execute_command(env, "${UV_EXE} pip " + cmd)


def uv_pip_freeze_action(target, source, env):
    output_file = str(target[0])

    uv_pip(env, f"freeze --exclude-editable > {output_file}")


def uv_export_requirements_action(target, source, env):
    output_file = str(target[0])

    execute_command(env, "${UV_EXE} export --frozen --output-file=" + output_file)


def uv_build_pkg_action(target, source, env):
    if source and isinstance(source, list):
        pkgs = []

        for a_source in source:
            a_source_str = str(a_source)

            if "pyproject.toml" in a_source_str:
                pkg_dir = os.path.dirname(a_source_str)

                pkgs.append(pkg_dir)

        for pkg in pkgs:
            if pkg:
                execute_command(env, "${UV_EXE} build " + pkg)
    else:
        execute_command(env, "${UV_EXE} build --all-packages")


def uv_pytest_action(target, source, env):
    pytest_exec_flags = env.get("PYTEST_FLAGS", "--capture=no")

    execute_command(env, f"${{UV_EXE}} run -- pytest {pytest_exec_flags}")
