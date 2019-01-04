import os
import subprocess
import setuptools
from setuptools.command.develop import develop
from distutils.command.build import build


with open('./README.md') as file_handle:
    readme = file_handle.read()

_root_dir = os.path.dirname(os.path.realpath(__file__))


def _build_backend(root_dir):
    print('START: Building backend dependencies')
    return_code = subprocess.call(['./cortex/ext/install_dependencies.sh'], shell=True, cwd=root_dir)
    if return_code != 0:
        print('ERROR: backend compilation failed', return_code)
        exit(-1)
    print('END: Building backend dependencies. Return code:', return_code)


class _BuildCommand(build):
    """pip3 install -vvv ./py-cortex-api"""
    def run(self):
        _build_backend(_root_dir)
        build.run(self)


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
    packages=setuptools.find_packages("."),
    include_package_data=True,
    install_requires=[
        'biopython >= 1.70',
    ],
    cmdclass={
        'build': _BuildCommand,
        'develop': _DevelopCommand
    })
