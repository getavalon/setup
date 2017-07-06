"""Run avalon-examples/export.py from within the avalon-setup environment"""
import os
import sys
import subprocess

cd = os.path.dirname(os.path.abspath(__file__))
runpy = os.path.join(cd, "run.py")
examplesdir = os.getenv("AVALON_EXAMPLES",
                        os.path.join(cd, "git", "avalon-examples"))
exportpy = os.path.join(examplesdir, "export.py")

# Run this command within the avalon-setup environment
forward = [sys.executable, "-u", exportpy]

returncode = subprocess.call([
    sys.executable,
    "-u",
    runpy,
    "--forward",
    " ".join(forward + sys.argv[1:])
], shell=True)

if returncode != 0:
    # Expect the parent process to print error messages
    sys.exit(1)
