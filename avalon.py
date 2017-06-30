#!/usr/bin/env python2

"""Avalon entrypoint

This establishes an environment relative to what
is available in this distribution of Avalon.

- https://github.com/getavalon/setup

Dependencies:
    - Python 2/3
    - PyQt5
    - PyMongo

Usage:
    $ ./avalon.py

Overrides:
    avalon.py takes into account dependencies bundled
    together with this distribution, but these can be
    overridden via environment variables.

    Set any of the below to override which path to put
    on your PYTHONPATH

    - PYBLISH_BASE
    - PYBLISH_QML
    - AVALON_CORE
    - AVALON_LAUNCHER

"""

import os
import sys
import platform
import subprocess

REPO_DIR = os.path.normpath(os.path.dirname(__file__))


def install():
    missing_dependencies = list()
    for dependency in ("PyQt5",
                       "pymongo"):
        try:
            __import__(dependency)
        except ImportError:
            missing_dependencies.append(dependency)

    if missing_dependencies:
        print("Sorry, there are some dependencies missing from your system.\n")
        print("\n".join(" - %s" % d for d in missing_dependencies))
        print("\nSee https://getavalon.github.io/2.0/howto/#install "
              "for details.")
        return 1

    # Enable overriding from local environment
    for dependency, name in (("PYBLISH_BASE", "pyblish-base"),
                             ("PYBLISH_QML", "pyblish-qml"),
                             ("AVALON_CORE", "avalon-core"),
                             ("AVALON_LAUNCHER", "avalon-launcher")):
        if dependency not in os.environ:
            os.environ[dependency] = os.path.join(REPO_DIR, "git", name)

    os.environ["PATH"] = os.pathsep.join([
        os.environ["PATH"],
        os.path.join(REPO_DIR, "bin"),

        # Add OS-level dependencies
        os.path.join(REPO_DIR, "bin", platform.system().lower()),
    ])

    os.environ["PYTHONPATH"] = os.pathsep.join(
        # Append to PYTHONPATH
        os.getenv("PYTHONPATH", "").split(os.pathsep) + [
            # Third-party dependencies for Avalon
            os.path.join(REPO_DIR, "bin", "pythonpath"),

            # Default config and dependency
            os.getenv("PYBLISH_BASE"),

            # The Launcher itself
            os.getenv("AVALON_LAUNCHER"),
            os.getenv("AVALON_CORE"),
        ]
    )

    # Override default configuration by setting this value.
    if "AVALON_CONFIG" not in os.environ:
        os.environ["AVALON_CONFIG"] = "polly"
        os.environ["PYTHONPATH"] += os.pathsep + os.path.join(
            REPO_DIR, "git", "mindbender-config")

    try:
        root = os.environ["AVALON_PROJECTS"]
    except KeyError:
        root = os.path.join(REPO_DIR, "git", "avalon-examples", "projects")
        os.environ["AVALON_PROJECTS"] = root

    try:
        config = os.environ["AVALON_CONFIG"]
    except KeyError:
        config = "polly"
        os.environ["AVALON_CONFIG"] = config

    if subprocess.call([sys.executable, "-c", "import %s" % config]) != 0:
        print("ERROR: config not found, check your PYTHONPATH.")
        return 1


def forward(args, silent=False):
    """Pass `args` to the Avalon CLI, within the Avalon Setup environment

    Arguments:
        args (list): Command-line arguments to run
            within the active environment

    """

    print("avalon.py: Forwarding %s.." % " ".join(args))
    popen = subprocess.Popen(
        [sys.executable, "-u", "-m"] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    # Blocks until finished
    for line in iter(popen.stdout.readline, ""):
        if not silent:
            sys.stdout.write(line)

    print("avalon.py: Finishing up..")
    popen.wait()
    return popen.returncode


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true",
                        help="Build project at the current working directory")
    parser.add_argument("--load", action="store_true",
                        help="Load project at the current working directory")
    parser.add_argument("--save", action="store_true",
                        help="Save project from the current working directory")
    parser.add_argument("--show", action="store_true",
                        help="Show the Avalon Launcher")

    kwargs = parser.parse_args()

    install()

    if kwargs.build:
        sys.exit(forward(["avalon.build"]))
    elif kwargs.load:
        sys.exit(forward(["avalon.inventory", "--load"]))
    elif kwargs.save:
        sys.exit(forward(["avalon.inventory", "--save"]))
    else:
        root = os.environ["AVALON_PROJECTS"]
        sys.exit(forward(["avalon.inventory", "--save"], silent=True))
        sys.exit(forward(["launcher", "--root", root]))
