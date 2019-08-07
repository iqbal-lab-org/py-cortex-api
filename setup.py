import os
import subprocess
import setuptools
from setuptools.command.develop import develop
from distutils.command.build import build
import sys


with open('./README.md') as file_handle:
    readme = file_handle.read()

_root_dir = os.path.dirname(os.path.realpath(__file__))


def _build_backend(root_dir):
    print('START: Building backend dependencies')
    completed_process = subprocess.run(['./cortex/ext/install_dependencies.sh'],
                                  shell=True,
                                  cwd=root_dir,
                                  stderr=subprocess.PIPE,
                                  stdout=subprocess.DEVNULL,
                                  universal_newlines = True)
    return_code = completed_process.returncode
    if return_code != 0:
        print('ERROR: backend compilation failed', return_code)
        exit(-1)

    # Display warnings
    stderr = [line for line in completed_process.stderr.split("\n") if "Warning:" in line]
    if len(stderr) > 0:
        print("\n".join(stderr), file=sys.stderr)

    print('END: Building backend dependencies. Return code:', return_code)


class _BuildCommand(build):
    """pip3 install -vvv ./py-cortex-api"""
    def run(self):
        _build_backend(_root_dir)
        #build.run(self)


class _DevelopCommand(develop):
    """pip3 install -vvv --editable ./py-cortex-api"""
    def run(self):
        _build_backend(_root_dir)
        develop.run(self)


setuptools.setup(
    name='py-cortex-api',
    version='1.0',
    description='Python API for cortex.',
    url='https://github.com/iqbal-lab-org/py-cortex-api',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages("."),
    include_package_data=True,
    install_requires=[
        'biopython >= 1.70',
    ],
    test_suite="cortex.tests",
    cmdclass={
        'build': _BuildCommand,
        'develop': _DevelopCommand
    })
