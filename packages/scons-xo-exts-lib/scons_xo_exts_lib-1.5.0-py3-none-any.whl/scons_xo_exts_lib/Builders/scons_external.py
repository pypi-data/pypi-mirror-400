#!/usr/bin/env python


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import subprocess

from SCons.Script import Builder
from SCons.Script import Environment

from scons_xo_exts_lib.BuildSupport import NodeMangling


def scons_external_action(target, source, env: Environment) -> int:
    source_dir: str = NodeMangling.get_first_directory(nodes=source)

    scons_exe: str = env.get("SCONS_EXE", "scons")
    scons_default_flags: str = env.get("SCONS_DEFAULT_FLAGS", "")
    scons_extra_flags: str = env.get("SCONS_EXTRA_FLAGS", "")

    cmd_args: list[str] = [
        scons_exe,
        scons_default_flags,
        scons_extra_flags,
    ]

    if target:
        if isinstance(target, list):
            cmd_args.extend([a_target.abspath for a_target in target])
        else:
            cmd_args.append(target.abspath)

    cmd: str = " ".join(cmd_args)
    print(cmd)

    result = subprocess.run(
        args=cmd,
        cwd=source_dir,
        capture_output=False,
        check=False,
        shell=True,
    )

    return result.returncode


def generate(env: Environment):
    scons_external_builddir_builder = Builder(action=scons_external_action)

    env.Append(BUILDERS={"SconsExternalBinary": scons_external_builddir_builder})


def exists(env: Environment):
    return env.Detect("scons_external")
