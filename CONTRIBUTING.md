# Development

virtual environment and pre-commit hooks:
```bash
python 3 -m venv venv && . venv/bin/activate && pip install -U pip
pip install pre-commit
pre-commit install
```

running tests:
```bash
python -m unittest discover -s cortex/tests
```

# Packaging

MANIFEST.in is used both for specifying:
* which data files to include in the 
installation (setup.py: `include_package_data=True`). This is crucial
 for proper functioning of the installed tool.
 
*  which data files to include in the packaged distribution (`python setup.py sdist bdist_wheel`).

For the latter this results in files that exceed PyPi's 60Mb limit.

Instead, run `python setup.py sdist`, and remove everything in 
`dist/py-cortex-api-<version>/cortex/ext` EXCEPT for `install_dependencies.sh`:

```bash
cd dist
tar xf py-cortex-api-<version>
rm -rf py-cortex-api-<version>{cortex,stampy,vcftools}
tar cfzv py-cortex-api-<version>.tar.gz py-cortex-api-<version>
```
 
Then can upload to PyPi: 
`pip install twine && twine upload dist/*`)


