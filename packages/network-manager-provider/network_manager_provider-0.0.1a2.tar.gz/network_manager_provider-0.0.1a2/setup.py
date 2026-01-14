#!/usr/bin/python
# coding: utf-8
# Copyright (C) 2024  rasmunk
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
from setuptools import setup, find_packages

cur_dir = os.path.abspath(os.path.dirname(__file__))


def read(path):
    with open(path, "r") as _file:
        return _file.read()


def read_req(name):
    path = os.path.join(cur_dir, name)
    return [req.strip() for req in read(path).splitlines() if req.strip()]


version_ns = {}
version_path = os.path.join(cur_dir, "network_manager_provider", "_version.py")
version_content = read(version_path)
exec(version_content, {}, version_ns)


long_description = open("README.rst").read()
setup(
    name="network_manager_provider",
    version=version_ns["__version__"],
    description="A corc plugin for providing network infrastructure",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Rasmus Munk",
    author_email="code@munk0.dk",
    packages=find_packages(),
    url="https://github.com/rasmunk/network_manager_provider",
    license="GNU General Public License v2 (GPLv2)",
    keywords=["Orchstration", "Networking"],
    install_requires=read_req("requirements.txt"),
    extras_require={
        "test": read_req("tests/requirements.txt"),
        "dev": read_req("requirements-dev.txt"),
    },
    # Ensures that the plugin can be discovered/loaded by corc
    entry_points={
        "console_scripts": [
            "network-manager-provider=network_manager_provider.cli.cli:cli"
        ],
        "corc.plugins": ["network_manager_provider=network_manager_provider"],
        "corc.plugins.networking": [
            "network_manager_provider=network_manager_provider"
        ],
        "corc.plugins.cli": [
            "network_manager_provider=network_manager_provider.cli.corc:network_manager_provider_cli"
        ],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
