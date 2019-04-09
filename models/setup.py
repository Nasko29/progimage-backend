#!/usr/bin/env python3
import setuptools
import sys
import os

with open("README.md", "r") as fh:
    readme = fh.read()

packages = [
    'progimagemodels',
]

if sys.argv[-1] == 'publish':
    # PYPI now uses twine for package management.
    # For this to work you must first `$ pip3 install twine`
    os.system('python3 setup.py sdist bdist_wheel')
    os.system('python3 -m twine upload --skip-existing dist/*')
    sys.exit()
    
with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="progimagemodels",
    version="0.1.0",
    author="Nasko Grozdanov",
    author_email="antonasko@gmail.com",
    description="Python models for the ProgImage API",
    long_description=readme,
    include_package_data=True,
    install_requires=required,
    long_description_content_type="text/markdown",
    url="",
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
