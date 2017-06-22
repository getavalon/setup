"""Avalon Setup entrypoint

"""

import os
import sys
import subprocess

os.chdir(os.path.normpath(os.path.dirname(__file__)))
cd = os.getcwd()


if __name__ == '__main__':
    os.environ["PYBLISH_BASE"] = os.path.join(cd, "git", "pyblish-base")
    os.environ["PYBLISH_QML"] = os.path.join(cd, "git", "pyblish-qml")
    os.environ["PYBLISH_MAYA"] = os.path.join(cd, "git", "avalon-maya")
    os.environ["PYBLISH_NUKE"] = os.path.join(cd, "git", "avalon-nuke")
    os.environ["PYBLISH_LITE"] = os.path.join(cd, "git", "avalon-lite")
    os.environ["AVALON_CORE"] = os.path.join(cd, "git", "avalon-core")
    os.environ["AVALON_LAUNCHER"] = os.path.join(cd, "git", "avalon-launcher")
    os.environ["PATH"] = os.pathsep.join([os.environ["PATH"],
                                         os.path.join(cd, "bin")])

    os.environ["PYTHONPATH"] = os.pathsep.join([

        # Third-party dependencies for Avalon
        os.path.join(cd, "bin", "pythonpath"),

        # The Launcher itself
        os.path.join(cd, "git", "avalon-launcher")] + [

        path for path in os.getenv("PYTHONPATH", "").split(os.pathsep)
        if path is not None
    ])

    root = os.getenv("AVALON_PROJECTS", os.path.join(
        cd, "git", "avalon-examples", "projects"))

    print("Environment ready")
    popen = subprocess.Popen(
        [sys.executable, "-u", "-m", "launcher", "--root", root],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    # Blocks until finished
    for line in iter(popen.stdout.readline, ""):
        sys.stdout.write(line)

    print("Shutting down..")
    popen.wait()

    print("Good bye")
