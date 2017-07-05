"""Avalon entrypoint

This establishes an environment relative to what
is available in this distribution of Avalon.

- https://github.com/getavalon/setup

Dependencies:
    - Python 2/3
    - PyQt5

Usage:
    $ ./avalon.py

Overrides:
    avalon.py takes into account dependencies bundled
    together with this distribution, but these can be
    overridden via environment variables.

    Set any of the below to override which path to put
    on your PYTHONPATH

    # Database
    - AVALON_MONGO=mongodb://username:pass@address:port

    # Dependencies
    - PYBLISH_BASE=absolute/path
    - PYBLISH_QML=absolute/path
    - AVALON_CORE=absolute/path
    - AVALON_LAUNCHER=absolute/path

    # Enable additional output
    - AVALON_DEBUG=True

"""

import os
import sys
import platform
import subprocess

REPO_DIR = os.path.normpath(os.path.dirname(__file__))
AVALON_DEBUG = bool(os.getenv("AVALON_DEBUG"))


def install():
    missing_dependencies = list()
    for dependency in ("PyQt5",):
        try:
            __import__(dependency)
        except ImportError:
            missing_dependencies.append(dependency)

    if missing_dependencies:
        print("Sorry, there are some dependencies missing from your system.\n")
        print("\n".join(" - %s" % d for d in missing_dependencies))

    missing_environment = list()
    for variable in ("AVALON_MONGO",):
        if variable not in os.environ:
            missing_environment.append(variable)

    if missing_environment:
        print("Don't forget to set the required environment variables.")
        print("\n".join("- %s" % v for v in missing_environment))

    if missing_dependencies or missing_environment:
        print("\nSee https://getavalon.github.io/2.0/howto/#install "
              "for more details.")
        sys.exit(1)

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
        sys.exit(1)


def forward(args, silent=False):
    """Pass `args` to the Avalon CLI, within the Avalon Setup environment

    Arguments:
        args (list): Command-line arguments to run
            within the active environment

    """

    if AVALON_DEBUG:
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

    if AVALON_DEBUG:
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
        if forward(["avalon.inventory", "--save"], silent=True) == 0:
            sys.exit(forward(["avalon.build"]))
        else:
            print("Couldn't save, this is a bug")
            sys.exit(1)

    elif kwargs.load:
        sys.exit(forward(["avalon.inventory", "--load"]))

    elif kwargs.save:
        sys.exit(forward(["avalon.inventory", "--save"]))

    elif kwargs.show:
        root = os.environ["AVALON_PROJECTS"]
        sys.exit(forward(["launcher", "--root", root]))

    else:
        print(__doc__)
