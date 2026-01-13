#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name="conftool",
    version="6.1.0",
    description="Tools to interoperate with distributed k/v stores",
    author="Joe",
    author_email="joe@wikimedia.org",
    url="https://github.com/wikimedia/operations-software-conftool",
    install_requires=[
        "python-etcd>=0.4.3",
        "pyyaml",
        "jsonschema",
    ],
    zip_safe=False,
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "conftool-sync = conftool.cli.syncer:main",
            "confctl = conftool.cli.tool:main",
            "dbctl = conftool.extensions.dbconfig:main [with-dbctl]",
            "conftool2git = conftool.cli.conftool2git:main [with-conftool2git]",
        ],
    },
    extras_require={
        "with-dbctl": [],  # No extra dependencies, but allow to mark it
        "with-conftool2git": ["pygit2", "aiohttp"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Clustering",
    ],
)
