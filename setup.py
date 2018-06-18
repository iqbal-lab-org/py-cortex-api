import setuptools

with open('./README.md') as fhandle:
    readme = fhandle.read()

setuptools.setup(
    name='cortex-api',
    version='1.0',
    description='Python API for cortex.',
    url='https://github.com/iqbal-lab-org/py-cortex-api',
    long_description=readme,
    packages=setuptools.find_packages("."),
    include_package_data=True,
    install_requires=[
        'pyfastaq >= 3.16.0',
    ])
