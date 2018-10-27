#!/usr/bin/env python
from io import open
from setuptools import setup, find_packages


with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name="wheeltools",
    use_scm_version={"write_to": "src/wheeltools/_version.py"},
    description="General tools for working with wheels",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Matthew Brett",
    maintainer="Matthew Brett",
    author_email="matthew.brett@gmail.com",
    url="https://github.com/anthrotype/wheeltools",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=["wheel"],
    setup_requires=["setuptools_scm"],
    extras_require={
        "testing": [
            "pytest >= 3.0.0, <4",
            "pytest-cov >= 2.5.1, <3",
        ]
    },
    license="BSD license",
    classifiers=[
        "Intended Audience :: Developers",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Operating System :: MacOS :: MacOS X",
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: " "Python Modules",
        "Topic :: Software Development :: Build Tools",
    ],
)
