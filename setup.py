import os
import subprocess
import setuptools
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.test import test


class DependencyInstaller:
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.realpath(__file__))
        self.cmake_dir = os.path.join(self.root_dir, 'cmake-build-debug')

    @staticmethod
    def build():
        print('Building dependencies')
        subprocess.call(['./cortex/ext/install_dependencies.sh'], shell=True)

    def test(self):
        pass


class InstallCommand(install):
    """pip3 install -vvv ./gramtools"""
    def run(self):
        dependencies = DependencyInstaller()
        dependencies.build()
        dependencies.test()
        install.run(self)


class DevelopCommand(develop):
    """pip3 install -vvv --editable ./gramtools"""
    def run(self):
        dependencies = DependencyInstaller()
        dependencies.build()
        dependencies.test()
        develop.run(self)


class TestCommand(test):
    """python3 setup.py test"""
    def run(self):
        dependencies = DependencyInstaller()
        dependencies.build()
        dependencies.test()
        test.run(self)


package_data = {
    'cortex': ['ext/*'],
}

with open('./README.md') as fhandle:
    readme = fhandle.read()

setuptools.setup(
    name='cortex',
    version='1.0',
    description='Python API for cortex.',
    url='https://github.com/iqbal-lab-org/py-cortex-api',
    long_description=readme,
    packages=setuptools.find_packages("."),
    package_data=package_data,
    include_package_data=True,
    install_requires=[
        'biopython >= 1.70',
    ],
    cmdclass={
        'dependencies': InstallCommand,
        'develop': DevelopCommand,
        'test': TestCommand,
    })
