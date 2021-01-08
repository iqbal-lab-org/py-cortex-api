import os
import sys
import subprocess
import setuptools
from setuptools.command.develop import develop
from setuptools.command.build_py import build_py

from cortex import __version__

with open("./README.md") as file_handle:
    readme = file_handle.read()

_root_dir = os.path.dirname(os.path.realpath(__file__))


def _build_backend(root_dir):
    print("START: Building backend dependencies")
    completed_process = subprocess.run(
        ["./cortex/ext/install_dependencies.sh"],
        cwd=root_dir,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        universal_newlines=True,
    )
    return_code = completed_process.returncode

    # Display warnings
    print(completed_process.stderr, file=sys.stderr)

    if return_code != 0:
        print("ERROR: backend compilation failed", return_code)
        exit(-1)

    print("END: Building backend dependencies. Return code:", return_code)


class _BuildCommand(build_py):
    """pip3 build_py -vvv ./py-cortex-api"""

    def run(self):
        _build_backend(_root_dir)
        build_py.run(self)


class _DevelopCommand(develop):
    """pip3 build_py -vvv --editable ./py-cortex-api"""

    def run(self):
        _build_backend(_root_dir)
        develop.run(self)


setuptools.setup(
    name="py-cortex-api",
    version=__version__,
    description="Python API for cortex.",
    url="https://github.com/iqbal-lab-org/py-cortex-api",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=["biopython == 1.76"],
    packages=setuptools.find_packages("."),
    include_package_data=True,
    test_suite="cortex.tests",
    cmdclass=dict(build_py=_BuildCommand, develop=_DevelopCommand),
)
