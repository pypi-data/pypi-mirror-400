# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 12:46:54 2024

@author: MejdiTRABELSI
"""

import toml


def update_version(version):
    version_list = [int(i) for i in version.split(".")]
    version_list[-1] += 1
    return ".".join([str(i) for i in version_list])


# Read the pyproject.toml file
with open("pyproject.toml", "r") as f:
    pyproject_toml = toml.load(f)

actual_version = pyproject_toml["project"]["version"]
new_version = update_version(actual_version)
pyproject_toml["project"]["version"] = new_version
print("new_version:", new_version)

# Write the updated pyproject.toml file
with open("pyproject.toml", "w") as f:
    toml.dump(pyproject_toml, f)
